# File: agents/parser_agent.py

"""
Parser Agent: Converts raw extracted text (from OCR, ASR, or direct text) into a structured math problem.

Uses LangChain chain with Groq LLM and strict JSON output parsing.
Cleans noise and detects ambiguity for potential HITL trigger.
"""

from typing import Dict

from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from core.config import Config
from core.prompts import PARSER_PROMPT

# Initialize LLM
llm = ChatGroq(
    api_key=Config.GROQ_API_KEY,
    model_name=Config.LLM_MODEL,
    temperature=Config.LLM_TEMPERATURE,
    max_tokens=Config.LLM_MAX_TOKENS,
)

# JSON parser for strict structured output
json_parser = JsonOutputParser()

# Parser chain: prompt → LLM → JSON parse
parser_chain = PARSER_PROMPT | llm | json_parser

def parse_problem(raw_text: str) -> Dict[str, any]:
    """
    Run the Parser Agent on raw extracted text.
    
    Returns structured dictionary as defined in the prompt schema.
    Raises exception if JSON parsing fails (can be caught in app for HITL).
    """
    try:
        structured_output = parser_chain.invoke({"raw_text": raw_text})
        
        # Validate required keys and types
        required_keys = ["problem_text", "topic", "variables", "constraints", "needs_clarification", "clarification_needed"]
        for key in required_keys:
            if key not in structured_output:
                raise ValueError(f"Missing key in parser output: {key}")
        
        # Ensure topic is supported
        if structured_output["topic"] not in Config.SUPPORTED_TOPICS:
            # Fallback to most likely or trigger clarification
            structured_output["topic"] = "algebra"  # default fallback
            structured_output["needs_clarification"] = True
            structured_output["clarification_needed"] = f"Topic '{structured_output['topic']}' not recognized. Classified as algebra."
        
        # Ensure types
        structured_output["variables"] = list(structured_output.get("variables", []))
        structured_output["constraints"] = list(structured_output.get("constraints", []))
        structured_output["needs_clarification"] = bool(structured_output.get("needs_clarification", False))
        
        return structured_output
    
    except OutputParserException as e:
        # If JSON parsing fails → treat as ambiguity → HITL
        return {
            "problem_text": raw_text.strip(),
            "topic": "unknown",
            "variables": [],
            "constraints": [],
            "needs_clarification": True,
            "clarification_needed": f"Parser failed to produce valid output: {str(e)}. Please review the problem statement."
        }
    except Exception as e:
        # General fallback
        return {
            "problem_text": raw_text.strip(),
            "topic": "unknown",
            "variables": [],
            "constraints": [],
            "needs_clarification": True,
            "clarification_needed": f"Unexpected error in parsing: {str(e)}"
        }

# Example usage (for local testing)
if __name__ == "__main__":
    sample_raw = "Find the probability that when a fair coin is tossed three times, we get exactly two heads."
    result = parse_problem(sample_raw)
    print(result)