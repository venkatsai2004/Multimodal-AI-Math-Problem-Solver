// Package pipeline contains the single Run() function that orchestrates the
// full Math Mentor agent pipeline: Parse → Route → RAG → Solve → Verify → Explain.
package pipeline

import (
	"github.com/math-mentor/backend/agents"
	"github.com/math-mentor/backend/config"
	"github.com/math-mentor/backend/groq"
	"github.com/math-mentor/backend/rag"
)

// Result is the final response struct sent back to the HTTP client.
// It mirrors the Python FastAPI response shape so the frontend needs no changes.
type Result struct {
	Status      string              `json:"status"`       // "success" | "clarification_needed"
	Message     string              `json:"message,omitempty"`  // Set when clarification is needed
	Topic       string              `json:"topic,omitempty"`
	Solution    *agents.Solution    `json:"solution,omitempty"`
	Explanation string              `json:"explanation,omitempty"`
	Confidence  float64             `json:"confidence,omitempty"`
	Issues      []string            `json:"issues,omitempty"`
	Retrieved   []rag.Result        `json:"retrieved,omitempty"`
}

// Runner holds the shared dependencies needed to execute the pipeline.
// Create one at startup and reuse it across requests.
type Runner struct {
	cfg        *config.Config
	ragStore   *rag.Store
	// Three Groq clients with different temperature settings.
	llmLow     *groq.Client // parser, router, verifier (deterministic)
	llmHigh    *groq.Client // explainer (natural tone)
}

// New creates a Runner from the given config and RAG store.
func New(cfg *config.Config, store *rag.Store) *Runner {
	return &Runner{
		cfg:      cfg,
		ragStore: store,
		llmLow: groq.NewClient(
			cfg.GroqAPIKey, cfg.LLMModel, cfg.LLMTempLow, cfg.LLMMaxTokens),
		llmHigh: groq.NewClient(
			cfg.GroqAPIKey, cfg.LLMModel, cfg.LLMTempHigh, cfg.LLMMaxTokens),
	}
}

// Run executes the full agent pipeline on a piece of raw text and returns
// the aggregated Result. It is safe to call concurrently from multiple goroutines.
func (r *Runner) Run(rawText string) Result {
	// ── Step 1: Parse ──────────────────────────────────────────────────────────
	// Convert raw (possibly noisy) text into a structured problem description.
	parsed := agents.ParseProblem(r.llmLow, rawText)

	// If the parser flagged the problem as ambiguous, stop early and ask the
	// user to clarify instead of producing a potentially wrong answer.
	if parsed.NeedsClarification {
		return Result{
			Status:  "clarification_needed",
			Message: parsed.ClarificationNeeded,
		}
	}

	// ── Step 2: Route ──────────────────────────────────────────────────────────
	// Determine which tools the solver needs and how deep to do RAG retrieval.
	routing := agents.RouteProblem(r.llmLow, parsed)

	// ── Step 3: Retrieve ───────────────────────────────────────────────────────
	// Pull relevant knowledge chunks from the in-memory RAG store.
	topK := r.cfg.TopKRetrieval
	if routing.RAGDepth == "none" {
		topK = 0 // Solver gets no context — straightforward problem
	} else if routing.RAGDepth == "shallow" && topK > 3 {
		topK = 3 // Limit to 3 chunks for shallow retrieval
	}
	retrieved := r.ragStore.Retrieve(parsed.ProblemText, topK)

	// ── Step 4: Solve ──────────────────────────────────────────────────────────
	// Ask the LLM to solve the problem, grounded on the retrieved context.
	solution := agents.SolveProblem(r.llmLow, parsed.ProblemText, retrieved)

	// ── Step 5: Verify ─────────────────────────────────────────────────────────
	// Critically check the proposed solution and compute a confidence score.
	verification := agents.VerifySolution(r.llmLow, parsed.ProblemText, solution)

	// ── Step 6: Explain ────────────────────────────────────────────────────────
	// Produce a student-friendly, step-by-step explanation of the verified solution.
	explanation := agents.ExplainSolution(r.llmHigh, parsed.ProblemText, solution)

	return Result{
		Status:      "success",
		Topic:       parsed.Topic,
		Solution:    &solution,
		Explanation: explanation,
		Confidence:  verification.Confidence,
		Issues:      verification.Issues,
		Retrieved:   retrieved,
	}
}
