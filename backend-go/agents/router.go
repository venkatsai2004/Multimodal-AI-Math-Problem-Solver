// router.go — Intent Router Agent.
// Reads the ParsedProblem and decides: confirmed topic, required tools, and RAG depth.
package agents

import (
	"encoding/json"
	"fmt"

	"github.com/math-mentor/backend/groq"
	"github.com/math-mentor/backend/prompts"
)

// RoutingResult is the structured output produced by the Router Agent.
type RoutingResult struct {
	Topic         string   `json:"topic"`          // Confirmed, supported topic
	RequiredTools []string `json:"required_tools"` // e.g. ["sympy_calculator"] or []
	RAGDepth      string   `json:"rag_depth"`      // "deep" | "shallow" | "none"
}

// knownTools is the set of tool names the system currently supports.
var knownTools = map[string]bool{"sympy_calculator": true}

// validRAGDepths is the set of accepted rag_depth values.
var validRAGDepths = map[string]bool{"deep": true, "shallow": true, "none": true}

// RouteProblem runs the Router Agent and returns a RoutingResult.
// Safe defaults are used if the LLM produces invalid or unexpected output.
func RouteProblem(client *groq.Client, parsed ParsedProblem) RoutingResult {
	// Serialise the parsed problem as JSON for the prompt.
	parsedJSON, err := json.MarshalIndent(parsed, "", "  ")
	if err != nil {
		return routerFallback(parsed.Topic, "Failed to marshal parsed problem")
	}

	systemPrompt := fmt.Sprintf(prompts.RouterSystem, prompts.TopicsCSV())
	userMessage := prompts.RouterUser(string(parsedJSON))

	reply, err := client.Complete(systemPrompt, userMessage)
	if err != nil {
		return routerFallback(parsed.Topic, fmt.Sprintf("Groq API error: %v", err))
	}

	var result RoutingResult
	if err := json.Unmarshal([]byte(stripCodeFences(reply)), &result); err != nil {
		return routerFallback(parsed.Topic, fmt.Sprintf("JSON parse error: %v", err))
	}

	// --- Validation & normalisation ---

	// Ensure topic is supported; fall back to whatever the parser decided.
	if !isSupportedTopic(result.Topic) {
		result.Topic = parsed.Topic
	}

	// Filter required_tools to only known tools.
	filtered := make([]string, 0, len(result.RequiredTools))
	seen := map[string]bool{}
	for _, t := range result.RequiredTools {
		if knownTools[t] && !seen[t] {
			filtered = append(filtered, t)
			seen[t] = true
		}
	}
	result.RequiredTools = filtered

	// Ensure rag_depth is valid.
	if !validRAGDepths[result.RAGDepth] {
		result.RAGDepth = "shallow"
	}

	return result
}

// routerFallback returns safe routing defaults when the agent fails.
func routerFallback(topic, _ string) RoutingResult {
	tools := []string{}
	// Default to sympy_calculator for symbolic topics.
	if topic == "algebra" || topic == "calculus" || topic == "linear_algebra" {
		tools = []string{"sympy_calculator"}
	}
	return RoutingResult{
		Topic:         topic,
		RequiredTools: tools,
		RAGDepth:      "shallow",
	}
}
