// main.go — entry point for the Math Mentor Go backend.
//
// Start the server:
//
//	cd backend-go
//	go run .
//
// The server listens on :8080 by default (override with PORT env var).
//
// Endpoints:
//
//	GET  /              — health check
//	POST /solve/text    — solve a math problem given as JSON { "problem": "..." }
//	POST /solve/image   — solve from an uploaded image file (OCR via Python service)
//	POST /solve/audio   — solve from an uploaded audio file (ASR via Python service)
package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/math-mentor/backend/config"
	"github.com/math-mentor/backend/handlers"
	"github.com/math-mentor/backend/multimodal"
	"github.com/math-mentor/backend/pipeline"
	"github.com/math-mentor/backend/rag"
)

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	log.Println("🚀 Math Mentor Go backend starting…")

	// ── 1. Load configuration ─────────────────────────────────────────────────
	cfg := config.Load()
	log.Printf("   Model : %s", cfg.LLMModel)
	log.Printf("   Port  : %s", cfg.Port)

	// ── 2. Configure multimodal Python service URL (if set) ───────────────────
	if pyURL := os.Getenv("PYTHON_SERVICE_URL"); pyURL != "" {
		multimodal.SetPythonServiceURL(pyURL)
		log.Printf("   Python OCR/ASR service: %s", pyURL)
	} else {
		log.Println("   Python OCR/ASR service: not configured (image/audio will use stub)")
	}

	// ── 3. Initialise the RAG knowledge store ─────────────────────────────────
	log.Printf("   Loading knowledge base from: %s", cfg.KnowledgeBaseDir)
	store := rag.New(cfg.KnowledgeBaseDir)
	log.Println("   ✅ RAG store ready")

	// ── 4. Create the pipeline runner ─────────────────────────────────────────
	runner := pipeline.New(cfg, store)

	// ── 5. Register HTTP routes ───────────────────────────────────────────────
	solver := handlers.NewSolver(runner)

	mux := http.NewServeMux()
	mux.HandleFunc("/", solver.HealthCheck)
	mux.HandleFunc("/solve/text", solver.SolveText)
	mux.HandleFunc("/solve/image", solver.SolveImage)
	mux.HandleFunc("/solve/audio", solver.SolveAudio)

	// ── 6. Start HTTP server ──────────────────────────────────────────────────
	addr := fmt.Sprintf(":%s", cfg.Port)
	log.Printf("   Listening on http://localhost%s", addr)
	log.Println("   Press Ctrl+C to stop.")

	if err := http.ListenAndServe(addr, withCORS(mux)); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}

// withCORS wraps the given handler and adds permissive CORS headers so that
// the frontend (running on a different port during development) can call the API.
func withCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		// Handle preflight requests.
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}

		next.ServeHTTP(w, r)
	})
}
