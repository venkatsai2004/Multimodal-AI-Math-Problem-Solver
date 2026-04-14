// Package agents contains the five AI agents that form the Math Mentor pipeline.
// parser.go: converts raw text (from OCR, ASR, or direct input) into a structured
// ParsedProblem by calling the Groq LLM with a strict JSON schema prompt.
package agents

import (
	"encoding/json"
	"fmt"
	"strings"

	"github.com/math-mentor/backend/groq"
	"github.com/math-mentor/backend/prompts"
)

// ParsedProblem is the structured output produced by the Parser Agent.
// It mirrors the JSON schema defined in prompts.ParserSystem.
type ParsedProblem struct {
	ProblemText          string   `json:"problem_text"`           // Cleaned, full problem statement
	Topic                string   `json:"topic"`                  // algebra | probability | calculus | linear_algebra
	Variables            []string `json:"variables"`              // Variable names, e.g. ["x", "y"]
	Constraints          []string `json:"constraints"`            // e.g. ["x > 0", "n is integer"]
	NeedsClarification   bool     `json:"needs_clarification"`    // True if problem is ambiguous
	ClarificationNeeded  string   `json:"clarification_needed"`   // Explanation when ambiguous
}

// supportedTopics is the authoritative list used for validation fallbacks.
var supportedTopics = []string{"algebra", "probability", "calculus", "linear_algebra"}

// isSupportedTopic returns true if the given topic is in the supported list.
func isSupportedTopic(topic string) bool {
	for _, t := range supportedTopics {
		if t == topic {
			return true
		}
	}
	return false
}

// ParseProblem runs the Parser Agent on the given raw text and returns a
// structured ParsedProblem. It validates required fields and normalises types.
// On any error, it returns a safe fallback that marks the problem as needing
// clarification so the calling code can handle it gracefully.
func ParseProblem(client *groq.Client, rawText string) ParsedProblem {
	// Build the prompt — inject supported topics into the system message.
	systemPrompt := fmt.Sprintf(prompts.ParserSystem, prompts.TopicsCSV())
	userMessage := prompts.ParserUser(rawText)

	// Call Groq — the model replies with a JSON string.
	reply, err := client.Complete(systemPrompt, userMessage)
	if err != nil {
		return parserFallback(rawText, fmt.Sprintf("Groq API error: %v", err))
	}

	// Strip any markdown code fences the model may have added (```json ... ```)
	cleaned := stripCodeFences(reply)

	// Parse the JSON response.
	var parsed ParsedProblem
	if err := json.Unmarshal([]byte(cleaned), &parsed); err != nil {
		return parserFallback(rawText, fmt.Sprintf("JSON parse error: %v — raw reply: %s", err, reply))
	}

	// Validate required fields.
	if parsed.ProblemText == "" {
		return parserFallback(rawText, "Parser returned empty problem_text")
	}

	// Normalise topic — fall back to algebra if unrecognised.
	if !isSupportedTopic(parsed.Topic) {
		parsed.Topic = "algebra"
		parsed.NeedsClarification = true
		parsed.ClarificationNeeded = fmt.Sprintf(
			"Topic '%s' is not recognised. Defaulted to algebra. Please confirm.", parsed.Topic)
	}

	// Ensure slices are never nil (simplifies downstream marshalling).
	if parsed.Variables == nil {
		parsed.Variables = []string{}
	}
	if parsed.Constraints == nil {
		parsed.Constraints = []string{}
	}

	return parsed
}

// parserFallback returns a safe ParsedProblem that signals clarification is
// needed, preserving the original raw text as the problem statement.
func parserFallback(rawText, reason string) ParsedProblem {
	return ParsedProblem{
		ProblemText:         strings.TrimSpace(rawText),
		Topic:               "unknown",
		Variables:           []string{},
		Constraints:         []string{},
		NeedsClarification:  true,
		ClarificationNeeded: reason,
	}
}

// stripCodeFences removes optional ```json ... ``` wrapper that some models add.
func stripCodeFences(s string) string {
	s = strings.TrimSpace(s)
	if strings.HasPrefix(s, "```") {
		// Remove first line (```json or ```)
		if idx := strings.Index(s, "\n"); idx != -1 {
			s = s[idx+1:]
		}
		// Remove trailing ```
		if idx := strings.LastIndex(s, "```"); idx != -1 {
			s = s[:idx]
		}
		s = strings.TrimSpace(s)
	}
	return s
}
