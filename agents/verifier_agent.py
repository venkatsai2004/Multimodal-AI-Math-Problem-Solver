# File: agents/verifier_agent.py

"""
Verifier / Critic Agent: Checks the solver's proposed solution for correctness.

Uses LangChain chain with Groq LLM and strict JSON output parsing.
Provides confidence score and issues list.
Low confidence triggers HITL in the main application.
"""

from typing import Dict

from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from core.config import Config
from core.prompts import VERIFIER_PROMPT

# Shared LLM
llm = ChatGroq(
    api_key=Config.GROQ_API_KEY,
    model_name=Config.LLM_MODEL,
    temperature=Config.LLM_TEMPERATURE,  # Low for consistent verification
    max_tokens=Config.LLM_MAX_TOKENS,
)

# JSON parser for strict structured output
json_parser = JsonOutputParser()

# Verifier chain
verifier_chain = VERIFIER_PROMPT | llm | json_parser

def verify_solution(
    problem_text: str,
    solution: Dict,  # From solver_agent: {"answer": ..., "steps": [...]}
) -> Dict:
    """
    Run the Verifier Agent.
    
    Returns:
    {
        "is_correct": bool,
        "confidence": float (0.0-1.0),
        "issues": list[str],
        "suggested_fix": str
    }
    
    On parsing failure, returns low-confidence result to trigger HITL.
    """
    final_answer = solution.get("answer", "Unknown")
    steps_str = "\n".join(solution.get("steps", ["No steps provided"]))
    
    try:
        verification_output = verifier_chain.invoke({
            "problem_text": problem_text,
            "solution_steps": steps_str,
            "final_answer": final_answer
        })
        
        # Validate required keys
        required_keys = ["is_correct", "confidence", "issues"]
        for key in required_keys:
            if key not in verification_output:
                raise ValueError(f"Missing key in verifier output: {key}")
        
        # Normalize types
        verification_output["is_correct"] = bool(verification_output["is_correct"])
        verification_output["confidence"] = float(verification_output.get("confidence", 0.5))
        verification_output["issues"] = list(verification_output.get("issues", []))
        verification_output.setdefault("suggested_fix", "")
        
        # Clamp confidence
        verification_output["confidence"] = max(0.0, min(1.0, verification_output["confidence"]))
        
        return verification_output
    
    except (OutputParserException, ValueError, KeyError) as e:
        # Fallback on parsing/validation error → low confidence, trigger HITL
        return {
            "is_correct": False,
            "confidence": 0.2,
            "issues": [f"Verifier parsing failed: {str(e)}"],
            "suggested_fix": "Manual review required due to internal verification error."
        }
    except Exception as e:
        # General error fallback
        return {
            "is_correct": False,
            "confidence": 0.1,
            "issues": [f"Unexpected verifier error: {str(e)}"],
            "suggested_fix": "System error during verification."
        }

# Local testing example
if __name__ == "__main__":
    sample_problem = "Solve x² - 5x + 6 = 0"
    sample_solution = {
        "answer": "\\boxed{2, 3}",
        "steps": [
            "Factor: (x-2)(x-3)=0",
            "Solutions: x=2 or x=3"
        ]
    }
    
    result = verify_solution(sample_problem, sample_solution)
    print(result)