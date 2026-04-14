// Package rag provides a lightweight, filesystem-based retrieval module.
// On startup it loads all markdown files from the knowledge/ directory,
// splits them into overlapping chunks, and stores them in memory.
// Retrieval uses simple TF-IDF-style term-frequency scoring (BM25-lite)
// — no external vector database required.
package rag

import (
	"math"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

// Result is one retrieved knowledge chunk returned to the pipeline.
type Result struct {
	Content string  `json:"content"` // The text of the chunk
	Source  string  `json:"source"`  // Relative path of the source .md file
	Type    string  `json:"type"`    // "knowledge_base" or "solved_problem"
	Score   float64 `json:"score"`   // Relevance score (higher = better match)
}

// chunk is an internal representation of a split knowledge document.
type chunk struct {
	content string
	source  string
	terms   map[string]int // term → raw frequency within the chunk
}

// Store holds all loaded knowledge chunks and a term frequency index.
type Store struct {
	chunks []chunk
	idf    map[string]float64 // inverse document frequency per term
}

// ---- Public API -------------------------------------------------------------

// New creates a Store by loading all .md files from knowledgeDir recursively.
// Call once at startup. Panics if the directory cannot be read.
func New(knowledgeDir string) *Store {
	s := &Store{idf: map[string]float64{}}
	s.load(knowledgeDir)
	s.buildIDF()
	return s
}

// Retrieve returns the top-k most relevant chunks for the given query string.
// Results are sorted descending by score. If the store is empty, returns nil.
func (s *Store) Retrieve(query string, k int) []Result {
	if len(s.chunks) == 0 {
		return nil
	}

	queryTerms := tokenise(query)
	type scored struct {
		idx   int
		score float64
	}

	scores := make([]scored, len(s.chunks))
	for i, c := range s.chunks {
		scores[i] = scored{idx: i, score: s.tfidfScore(queryTerms, c)}
	}

	// Sort descending by score.
	sort.Slice(scores, func(a, b int) bool {
		return scores[a].score > scores[b].score
	})

	if k > len(scores) {
		k = len(scores)
	}

	results := make([]Result, 0, k)
	for _, sc := range scores[:k] {
		if sc.score == 0 {
			break // No matches at all
		}
		c := s.chunks[sc.idx]
		results = append(results, Result{
			Content: c.content,
			Source:  c.source,
			Type:    "knowledge_base",
			Score:   math.Round(sc.score*10000) / 10000,
		})
	}
	return results
}

// ---- Internal helpers -------------------------------------------------------

const chunkSize = 800    // characters per chunk
const chunkOverlap = 150 // character overlap between consecutive chunks

// load walks the knowledge directory and splits each .md file into chunks.
func (s *Store) load(dir string) {
	_ = filepath.WalkDir(dir, func(path string, d os.DirEntry, err error) error {
		if err != nil || d.IsDir() || !strings.HasSuffix(d.Name(), ".md") {
			return nil
		}
		data, err := os.ReadFile(path)
		if err != nil {
			return nil
		}
		rel, _ := filepath.Rel(dir, path)
		s.splitAndStore(string(data), rel)
		return nil
	})
}

// splitAndStore breaks a document into overlapping chunks and adds them.
func (s *Store) splitAndStore(content, source string) {
	runes := []rune(content)
	for start := 0; start < len(runes); start += chunkSize - chunkOverlap {
		end := start + chunkSize
		if end > len(runes) {
			end = len(runes)
		}
		text := strings.TrimSpace(string(runes[start:end]))
		if text == "" {
			break
		}
		s.chunks = append(s.chunks, chunk{
			content: text,
			source:  source,
			terms:   termFreq(text),
		})
		if end == len(runes) {
			break
		}
	}
}

// buildIDF computes the inverse document frequency for every term across all chunks.
func (s *Store) buildIDF() {
	df := map[string]int{} // number of chunks containing each term
	for _, c := range s.chunks {
		for term := range c.terms {
			df[term]++
		}
	}
	n := float64(len(s.chunks))
	for term, freq := range df {
		s.idf[term] = math.Log(1 + n/float64(freq))
	}
}

// tfidfScore computes a simple TF-IDF similarity between a query and a chunk.
func (s *Store) tfidfScore(queryTerms []string, c chunk) float64 {
	score := 0.0
	total := 0
	for _, t := range c.terms {
		total += t
	}
	if total == 0 {
		return 0
	}
	for _, qt := range queryTerms {
		tf := float64(c.terms[qt]) / float64(total)
		idf := s.idf[qt]
		score += tf * idf
	}
	return score
}

// tokenise splits text into lowercase tokens, stripping punctuation.
func tokenise(text string) []string {
	text = strings.ToLower(text)
	var tokens []string
	var cur strings.Builder
	for _, r := range text {
		if isAlphanumeric(r) {
			cur.WriteRune(r)
		} else if cur.Len() > 0 {
			tokens = append(tokens, cur.String())
			cur.Reset()
		}
	}
	if cur.Len() > 0 {
		tokens = append(tokens, cur.String())
	}
	return tokens
}

// termFreq returns a map of token → frequency for the given text.
func termFreq(text string) map[string]int {
	freq := map[string]int{}
	for _, t := range tokenise(text) {
		freq[t]++
	}
	return freq
}

func isAlphanumeric(r rune) bool {
	return (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9')
}
