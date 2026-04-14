// explainer.go — Explainer / Tutor Agent.
// Takes the verified solution and produces a clear, student-friendly explanation
// in plain text (not JSON) — suitable for JEE preparation.
package agents

import (
	"fmt"
	"strings"

	"github.com/math-mentor/backend/groq"
	"github.com/math-mentor/backend/prompts"
)

// ExplainSolution runs the Explainer Agent and returns a free-form tutorial string.
// The explanation is engaging, step-by-step, and highlights key concepts.
func ExplainSolution(client *groq.Client, problemText string, solution Solution) string {
	stepsStr := strings.Join(solution.Steps, "\n")
	userMessage := prompts.ExplainerUser(problemText, stepsStr, solution.Answer)

	reply, err := client.Complete(prompts.ExplainerSystem, userMessage)
	if err != nil {
		// Return a minimal fallback explanation.
		return explainerFallback(problemText, stepsStr, solution.Answer,
			fmt.Sprintf("Groq API error: %v", err))
	}

	explanation := strings.TrimSpace(reply)

	// If the model somehow forgot to box the final answer, append it manually.
	if !strings.Contains(explanation, "\\boxed") && solution.Answer != "" {
		explanation += fmt.Sprintf("\n\n**Final Answer:** \\boxed{%s}", solution.Answer)
	}

	return explanation
}

// explainerFallback returns a minimal structured explanation when the agent fails.
func explainerFallback(problem, steps, answer, reason string) string {
	return fmt.Sprintf(`**Problem:** %s

**Explanation** *(fallback — %s)*:

%s

**Final Answer:** %s`, problem, reason, steps, answer)
}
