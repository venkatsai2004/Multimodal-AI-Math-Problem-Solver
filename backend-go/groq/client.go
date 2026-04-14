// Package groq provides a lightweight HTTP client for the Groq Chat Completions API.
// It is intentionally minimal — no third-party SDK needed.
package groq

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

const groqAPIURL = "https://api.groq.com/openai/v1/chat/completions"

// Client holds the API key and model settings needed to make Groq API calls.
type Client struct {
	APIKey      string
	Model       string
	Temperature float64
	MaxTokens   int
	httpClient  *http.Client
}

// NewClient creates a Groq client with a 60-second HTTP timeout.
func NewClient(apiKey, model string, temperature float64, maxTokens int) *Client {
	return &Client{
		APIKey:      apiKey,
		Model:       model,
		Temperature: temperature,
		MaxTokens:   maxTokens,
		httpClient:  &http.Client{Timeout: 60 * time.Second},
	}
}

// ---- Request / Response types -----------------------------------------------

// chatMessage is a single message in the conversation (system or user role).
type chatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// chatRequest is the JSON body sent to the Groq completions endpoint.
type chatRequest struct {
	Model       string        `json:"model"`
	Messages    []chatMessage `json:"messages"`
	Temperature float64       `json:"temperature"`
	MaxTokens   int           `json:"max_tokens"`
}

// chatResponse mirrors the subset of the OpenAI-compatible response we need.
type chatResponse struct {
	Choices []struct {
		Message struct {
			Content string `json:"content"`
		} `json:"message"`
	} `json:"choices"`
	Error *struct {
		Message string `json:"message"`
	} `json:"error,omitempty"`
}

// ---- Public API -------------------------------------------------------------

// Complete sends a system prompt together with a user message to Groq and
// returns the assistant's plain-text reply.
//
// Usage:
//
//	reply, err := client.Complete("You are a math tutor.", "Solve x^2 - 4 = 0")
func (c *Client) Complete(systemPrompt, userMessage string) (string, error) {
	reqBody := chatRequest{
		Model: c.Model,
		Messages: []chatMessage{
			{Role: "system", Content: systemPrompt},
			{Role: "user", Content: userMessage},
		},
		Temperature: c.Temperature,
		MaxTokens:   c.MaxTokens,
	}

	bodyBytes, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("groq: failed to marshal request: %w", err)
	}

	req, err := http.NewRequest(http.MethodPost, groqAPIURL, bytes.NewReader(bodyBytes))
	if err != nil {
		return "", fmt.Errorf("groq: failed to build HTTP request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+c.APIKey)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return "", fmt.Errorf("groq: HTTP request failed: %w", err)
	}
	defer resp.Body.Close()

	respBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("groq: failed to read response body: %w", err)
	}

	var chatResp chatResponse
	if err := json.Unmarshal(respBytes, &chatResp); err != nil {
		return "", fmt.Errorf("groq: failed to parse response JSON: %w", err)
	}

	// Surface API-level errors (wrong key, rate limit, etc.)
	if chatResp.Error != nil {
		return "", fmt.Errorf("groq API error: %s", chatResp.Error.Message)
	}

	if len(chatResp.Choices) == 0 {
		return "", fmt.Errorf("groq: no choices returned in response")
	}

	return chatResp.Choices[0].Message.Content, nil
}
