// solver.go — Math Solver Agent.
// Solves the math problem step-by-step using the Groq LLM, grounded on RAG context.
package agents

import (
	"encoding/json"
	"fmt"
	"strings"

	"github.com/math-mentor/backend/groq"
	"github.com/math-mentor/backend/prompts"
	"github.com/math-mentor/backend/rag"
)

// Solution is the structured output produced by the Solver Agent.
type Solution struct {
	Answer      string   `json:"answer"`       // The final mathematical answer
	Steps       []string `json:"steps"`        // Step-by-step working
	UsedSources []string `json:"used_sources"` // RAG source identifiers used (may be empty)
}

// SolveProblem runs the Solver Agent given the problem text and retrieved RAG context.
// It returns a Solution with the answer and all reasoning steps.
func SolveProblem(client *groq.Client, problemText string, retrieved []rag.Result) Solution {
	// Format retrieved context as a numbered list for the prompt.
	contextParts := make([]string, 0, len(retrieved))
	for i, r := range retrieved {
		contextParts = append(contextParts, fmt.Sprintf("%d. [%s] %s", i+1, r.Source, r.Content))
	}
	contextStr := "No additional context available."
	if len(contextParts) > 0 {
		contextStr = strings.Join(contextParts, "\n\n")
	}

	userMessage := prompts.SolverUser(problemText, contextStr)
	reply, err := client.Complete(prompts.SolverSystem, userMessage)
	if err != nil {
		return solverFallback(fmt.Sprintf("Groq API error: %v", err))
	}

	var sol Solution
	if err := json.Unmarshal([]byte(stripCodeFences(reply)), &sol); err != nil {
		// If JSON parsing fails, wrap the raw text as a single step.
		return Solution{
			Answer:      "See steps below",
			Steps:       []string{strings.TrimSpace(reply)},
			UsedSources: []string{},
		}
	}

	// Normalise nil slices.
	if sol.Steps == nil {
		sol.Steps = []string{}
	}
	if sol.UsedSources == nil {
		sol.UsedSources = []string{}
	}
	if sol.Answer == "" {
		sol.Answer = "No answer produced"
	}

	return sol
}

// solverFallback returns an error-state Solution.
func solverFallback(reason string) Solution {
	return Solution{
		Answer:      "Solver execution failed",
		Steps:       []string{"Error: " + reason},
		UsedSources: []string{},
	}
}
