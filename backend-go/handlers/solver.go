// Package handlers contains the HTTP handler functions for the Math Mentor API.
// Each handler reads a request, calls the appropriate multimodal processor,
// runs the pipeline, and writes a JSON response.
package handlers

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/math-mentor/backend/multimodal"
	"github.com/math-mentor/backend/pipeline"
)

// Solver groups the HTTP handlers that expose the Math Mentor pipeline.
type Solver struct {
	runner *pipeline.Runner
}

// NewSolver creates a Solver with the given pipeline runner.
func NewSolver(runner *pipeline.Runner) *Solver {
	return &Solver{runner: runner}
}

// ---- HTTP Handlers ----------------------------------------------------------

// HealthCheck handles GET / — a simple liveness probe.
func (s *Solver) HealthCheck(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{
		"message": "Math Mentor API running 🚀 (Go backend)",
	})
}

// SolveText handles POST /solve/text.
// Request body: { "problem": "..." }
func (s *Solver) SolveText(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeError(w, http.StatusMethodNotAllowed, "method not allowed")
		return
	}

	var req struct {
		Problem string `json:"problem"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid JSON body: "+err.Error())
		return
	}
	if req.Problem == "" {
		writeError(w, http.StatusBadRequest, "field 'problem' is required")
		return
	}

	log.Printf("[text] solving: %.80s…", req.Problem)

	extraction := multimodal.ProcessText(req.Problem)
	result := s.runner.Run(extraction.RawText)
	writeJSON(w, http.StatusOK, result)
}

// SolveImage handles POST /solve/image.
// Expects a multipart/form-data file field named "file".
func (s *Solver) SolveImage(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeError(w, http.StatusMethodNotAllowed, "method not allowed")
		return
	}

	// Limit upload to 10 MB.
	r.Body = http.MaxBytesReader(w, r.Body, 10<<20)

	if err := r.ParseMultipartForm(10 << 20); err != nil {
		writeError(w, http.StatusBadRequest, "failed to parse multipart form: "+err.Error())
		return
	}

	file, header, err := r.FormFile("file")
	if err != nil {
		writeError(w, http.StatusBadRequest, "missing 'file' field in form data")
		return
	}
	defer file.Close()

	data := make([]byte, header.Size)
	if _, err := file.Read(data); err != nil {
		writeError(w, http.StatusInternalServerError, "failed to read uploaded file")
		return
	}

	log.Printf("[image] processing file: %s (%d bytes)", header.Filename, header.Size)

	extraction, err := multimodal.ProcessImage(data, header.Filename)
	if err != nil {
		// Non-fatal — extraction returns a stub text; pipeline will ask for clarification.
		log.Printf("[image] OCR warning: %v", err)
	}

	result := s.runner.Run(extraction.RawText)
	writeJSON(w, http.StatusOK, result)
}

// SolveAudio handles POST /solve/audio.
// Expects a multipart/form-data file field named "file".
func (s *Solver) SolveAudio(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeError(w, http.StatusMethodNotAllowed, "method not allowed")
		return
	}

	r.Body = http.MaxBytesReader(w, r.Body, 50<<20) // 50 MB for audio

	if err := r.ParseMultipartForm(50 << 20); err != nil {
		writeError(w, http.StatusBadRequest, "failed to parse multipart form: "+err.Error())
		return
	}

	file, header, err := r.FormFile("file")
	if err != nil {
		writeError(w, http.StatusBadRequest, "missing 'file' field in form data")
		return
	}
	defer file.Close()

	data := make([]byte, header.Size)
	if _, err := file.Read(data); err != nil {
		writeError(w, http.StatusInternalServerError, "failed to read uploaded file")
		return
	}

	log.Printf("[audio] processing file: %s (%d bytes)", header.Filename, header.Size)

	extraction, err := multimodal.ProcessAudio(data, header.Filename)
	if err != nil {
		log.Printf("[audio] ASR warning: %v", err)
	}

	result := s.runner.Run(extraction.RawText)
	writeJSON(w, http.StatusOK, result)
}

// ---- helpers ----------------------------------------------------------------

// writeJSON encodes v as JSON and writes it with the given HTTP status code.
func writeJSON(w http.ResponseWriter, status int, v interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(v); err != nil {
		log.Printf("writeJSON error: %v", err)
	}
}

// writeError writes a JSON error response.
func writeError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, map[string]string{"error": message})
}
