// Package config loads and exposes all application configuration.
// Values are read from the .env file at the project root (one level above backend-go/).
package config

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"runtime"
	"strconv"

	"github.com/joho/godotenv"
)

// Config holds all configuration values for the Math Mentor Go backend.
type Config struct {
	// Groq LLM settings
	GroqAPIKey   string
	LLMModel     string
	LLMTempLow   float64 // used by parser, router, verifier (deterministic)
	LLMTempHigh  float64 // used by explainer (more natural tone)
	LLMMaxTokens int

	// Confidence thresholds
	ParserAmbiguityThreshold  float64
	VerifierConfidenceThreshold float64

	// RAG settings
	KnowledgeBaseDir string
	TopKRetrieval    int
	TopKMemory       int

	// Supported math topics
	SupportedTopics []string

	// Server
	Port string
}

// Load reads environment variables (from .env) and returns a populated Config.
// Panics if the mandatory GROQ_API_KEY is missing.
func Load() *Config {
	// Locate the project root (.env lives one directory above backend-go/)
	_, filename, _, _ := runtime.Caller(0)
	projectRoot := filepath.Join(filepath.Dir(filename), "..", "..")

	envPath := filepath.Join(projectRoot, ".env")
	if err := godotenv.Load(envPath); err != nil {
		log.Printf("Warning: could not load .env from %s: %v", envPath, err)
	}

	apiKey := os.Getenv("GROQ_API_KEY")
	if apiKey == "" {
		panic("GROQ_API_KEY is required — set it in the .env file at the project root")
	}

	return &Config{
		GroqAPIKey:   apiKey,
		LLMModel:     getEnv("LLM_MODEL", "meta-llama/llama-4-maverick-17b-128e-instruct"),
		LLMTempLow:   getEnvFloat("LLM_TEMP_LOW", 0.2),
		LLMTempHigh:  getEnvFloat("LLM_TEMP_HIGH", 0.4),
		LLMMaxTokens: getEnvInt("LLM_MAX_TOKENS", 2048),

		ParserAmbiguityThreshold:    getEnvFloat("PARSER_AMBIGUITY_THRESHOLD", 0.8),
		VerifierConfidenceThreshold: getEnvFloat("VERIFIER_CONFIDENCE_THRESHOLD", 0.85),

		// Absolute path to the knowledge base (lives at project root / knowledge)
		KnowledgeBaseDir: filepath.Join(projectRoot, "knowledge"),
		TopKRetrieval:    getEnvInt("TOP_K_RETRIEVAL", 5),
		TopKMemory:       getEnvInt("TOP_K_MEMORY_RETRIEVAL", 3),

		SupportedTopics: []string{"algebra", "probability", "calculus", "linear_algebra"},

		Port: getEnv("PORT", "8080"),
	}
}

// ---- helpers ----------------------------------------------------------------

func getEnv(key, defaultVal string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return defaultVal
}

func getEnvFloat(key string, defaultVal float64) float64 {
	if v := os.Getenv(key); v != "" {
		if f, err := strconv.ParseFloat(v, 64); err == nil {
			return f
		}
		fmt.Printf("Warning: invalid float for %s, using default %.2f\n", key, defaultVal)
	}
	return defaultVal
}

func getEnvInt(key string, defaultVal int) int {
	if v := os.Getenv(key); v != "" {
		if i, err := strconv.Atoi(v); err == nil {
			return i
		}
		fmt.Printf("Warning: invalid int for %s, using default %d\n", key, defaultVal)
	}
	return defaultVal
}
