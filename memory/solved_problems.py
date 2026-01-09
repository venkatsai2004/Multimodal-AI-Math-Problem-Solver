# File: memory/solved_problems.py
"""
Memory module for storing solved/corrected problems and retrieving similar ones.

This is a thin wrapper around the hybrid RAG functions in core/rag_hybrid.py.
It provides higher-level functions tailored to the workflow:

- Store a complete solved session (after verification and optional feedback/HITL correction)
- The stored document includes:
  - Original extracted text (for OCR/ASR correction patterns indirectly via similarity)
  - Parsed problem
  - Retrieved context summary
  - Solution steps and answer
  - Verification outcome
  - User/reviewer feedback

Similarity search on problem_text enables reuse of solutions and patterns.
No separate OCR correction rules database — similarity on problematic raw_text handles common errors.
"""

from typing import Dict, List, Optional

from core.rag_hybrid import add_solved_problem_to_memory as _add_to_memory
from core.rag_hybrid import retrieve_similar_problems


def store_solved_problem(
    original_extraction: Dict,       # From multimodal: {"raw_text", "confidence", "source"}
    parsed_problem: Dict,
    retrieved_context: List[Dict],
    solution: Dict,                  # From solver: {"answer", "steps", "used_sources"}
    verification: Dict,              # From verifier: {"is_correct", "confidence", ...}
    user_feedback: Optional[str] = None,
    corrected_solution: Optional[Dict] = None  # If HITL provided correction
) -> None:
    """
    Store a complete solved problem in the memory vector store.
    Uses the parsed problem as base, appends full details for rich similarity.
    If corrected_solution provided (from HITL), store that instead of original solution.
    """
    effective_solution = corrected_solution or solution

    # Summary of retrieved context for storage (avoid storing huge text)
    retrieved_summary = "\n".join([
        f"Source {i}: {c.get('source', 'unknown')} ({c['type']})"
        for i, c in enumerate(retrieved_context)
    ]) if retrieved_context else "No retrieved context"

    feedback_str = user_feedback or "None"
    if verification.get("issues"):
        feedback_str += f" | Verifier issues: {'; '.join(verification['issues'])}"
    if corrected_solution:
        feedback_str += " | Corrected via HITL"

    # Pre-join steps to avoid backslash in f-string expression
    steps_str = "\n".join(effective_solution.get('steps', ['No steps']))

    content = f"""
Original extraction ({original_extraction['source']} input, confidence {original_extraction['confidence']:.2f}):
{original_extraction['raw_text']}

Parsed Problem:
{parsed_problem['problem_text']}
Topic: {parsed_problem['topic']}
Variables: {', '.join(parsed_problem['variables'])}
Constraints: {', '.join(parsed_problem['constraints'])}

Retrieved context summary:
{retrieved_summary}

Solution steps:
{steps_str}

Final answer:
{effective_solution.get('answer', 'None')}

Verification:
Correct: {verification['is_correct']} (confidence: {verification['confidence']:.2f})
Issues: {'; '.join(verification.get('issues', []))}

User feedback:
{feedback_str}
    """.strip()

    # Create a minimal parsed-like dict for the add function
    memory_parsed = parsed_problem.copy()

    # Use the low-level add function
    _add_to_memory(
        parsed_problem=memory_parsed,
        solution=effective_solution,
        feedback=feedback_str
    )

# Re-export retrieval for convenience
__all__ = [
    "store_solved_problem",
    "retrieve_similar_problems"
]

# Note: retrieve_similar_problems(query=parsed_problem['problem_text']) is called in hybrid_retrieval