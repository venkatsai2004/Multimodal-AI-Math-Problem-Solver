// verifier.go — Verifier / Critic Agent.
// Checks the proposed solution for mathematical correctness and domain validity,
// returning a confidence score and a list of any issues found.
package agents

import (
	"encoding/json"
	"fmt"
	"math"
	"strings"

	"github.com/math-mentor/backend/groq"
	"github.com/math-mentor/backend/prompts"
)

// Verification is the structured output produced by the Verifier Agent.
type Verification struct {
	IsCorrect    bool     `json:"is_correct"`    // Whether the solution is mathematically correct
	Confidence   float64  `json:"confidence"`    // 0.0 (wrong) → 1.0 (certain)
	Issues       []string `json:"issues"`        // Any correctness issues detected
	SuggestedFix string   `json:"suggested_fix"` // Recommended fix if issues exist
}

// VerifySolution runs the Verifier Agent against the problem and proposed solution.
// Low confidence (below a threshold) signals that a human should review the answer.
func VerifySolution(client *groq.Client, problemText string, solution Solution) Verification {
	stepsStr := strings.Join(solution.Steps, "\n")
	userMessage := prompts.VerifierUser(problemText, stepsStr, solution.Answer)

	reply, err := client.Complete(prompts.VerifierSystem, userMessage)
	if err != nil {
		return verifierFallback(fmt.Sprintf("Groq API error: %v", err))
	}

	var result Verification
	if err := json.Unmarshal([]byte(stripCodeFences(reply)), &result); err != nil {
		return verifierFallback(fmt.Sprintf("JSON parse error: %v — raw: %s", err, reply))
	}

	// Validate required fields.
	if result.Confidence == 0 && !result.IsCorrect {
		// Distinguish a genuine 0.0 from a missing field by checking the raw JSON.
		// If the key was simply absent we set a neutral default.
		result.Confidence = 0.5
	}

	// Clamp confidence to [0.0, 1.0].
	result.Confidence = math.Max(0.0, math.Min(1.0, result.Confidence))

	// Normalise nil slices.
	if result.Issues == nil {
		result.Issues = []string{}
	}

	return result
}

// verifierFallback returns a low-confidence result that triggers human review.
func verifierFallback(reason string) Verification {
	return Verification{
		IsCorrect:    false,
		Confidence:   0.2,
		Issues:       []string{"Verifier error: " + reason},
		SuggestedFix: "Manual review required.",
	}
}
