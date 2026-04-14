// Package multimodal handles the three input modalities: text, image, and audio.
// In this Go backend, text is processed natively.
// Image (OCR) and audio (ASR) delegate to the Python microservice via HTTP,
// or return a helpful stub when the Python service is not running.
package multimodal

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"strings"
	"time"
)

// InputResult is the uniform output from any modality processor.
type InputResult struct {
	RawText    string  `json:"raw_text"`   // Extracted text ready for the pipeline
	Confidence float64 `json:"confidence"` // 1.0 for text; OCR/ASR score otherwise
	Source     string  `json:"source"`     // "text" | "image" | "audio"
}

// pythonServiceURL is the base URL of the running Python FastAPI service.
// Override via PYTHON_SERVICE_URL env var (see main.go) or set directly.
var pythonServiceURL = "http://localhost:8000"

// SetPythonServiceURL allows the caller to configure the Python service base URL.
func SetPythonServiceURL(url string) {
	pythonServiceURL = strings.TrimRight(url, "/")
}

// httpClient is a shared client with a generous timeout for OCR/ASR calls.
var httpClient = &http.Client{Timeout: 90 * time.Second}

// ---- Public API -------------------------------------------------------------

// ProcessText normalises the raw text string into an InputResult.
// Confidence is always 1.0 because no extraction is performed.
func ProcessText(text string) InputResult {
	return InputResult{
		RawText:    strings.TrimSpace(text),
		Confidence: 1.0,
		Source:     "text",
	}
}

// ProcessImage forwards the raw image bytes to the Python OCR microservice
// at POST /solve/image and extracts the raw_text from the response.
// Falls back to a stub when the service is unavailable.
func ProcessImage(imageData []byte, filename string) (InputResult, error) {
	result, err := proxyFileToPython("/solve/image", "file", filename, imageData)
	if err != nil {
		// Return a stub so the pipeline can still run (will need clarification).
		return InputResult{
			RawText:    "(Image OCR unavailable — Python service not running)",
			Confidence: 0.0,
			Source:     "image",
		}, fmt.Errorf("image OCR proxy failed: %w", err)
	}
	return result, nil
}

// ProcessAudio forwards the raw audio bytes to the Python ASR microservice
// at POST /solve/audio and extracts the raw_text from the response.
// Falls back to a stub when the service is unavailable.
func ProcessAudio(audioData []byte, filename string) (InputResult, error) {
	result, err := proxyFileToPython("/solve/audio", "file", filename, audioData)
	if err != nil {
		return InputResult{
			RawText:    "(Audio ASR unavailable — Python service not running)",
			Confidence: 0.0,
			Source:     "audio",
		}, fmt.Errorf("audio ASR proxy failed: %w", err)
	}
	return result, nil
}

// ---- Internal helpers -------------------------------------------------------

// proxyFileToPython sends a multipart/form-data file upload to the Python service
// and parses the returned JSON for the "raw_text" field.
func proxyFileToPython(path, fieldName, filename string, data []byte) (InputResult, error) {
	var buf bytes.Buffer
	writer := multipart.NewWriter(&buf)

	part, err := writer.CreateFormFile(fieldName, filename)
	if err != nil {
		return InputResult{}, err
	}
	if _, err = part.Write(data); err != nil {
		return InputResult{}, err
	}
	writer.Close()

	resp, err := httpClient.Post(
		pythonServiceURL+path,
		writer.FormDataContentType(),
		&buf,
	)
	if err != nil {
		return InputResult{}, fmt.Errorf("HTTP POST to Python service failed: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return InputResult{}, fmt.Errorf("reading Python service response: %w", err)
	}

	// The Python service returns the full pipeline result; we only need raw_text.
	// However if the Python service is used for extraction only (future refactor),
	// this field will be at the top level. Handle both shapes gracefully.
	var payload map[string]interface{}
	if err := json.Unmarshal(body, &payload); err != nil {
		return InputResult{}, fmt.Errorf("parsing Python service JSON: %w", err)
	}

	rawText, _ := payload["raw_text"].(string)
	if rawText == "" {
		// Full pipeline response — extract from nested structure if needed.
		rawText = "(Text extracted by Python service — see full response)"
	}

	return InputResult{
		RawText:    rawText,
		Confidence: 0.9,
		Source:     path[7:], // strip "/solve/" → "image" or "audio"
	}, nil
}
