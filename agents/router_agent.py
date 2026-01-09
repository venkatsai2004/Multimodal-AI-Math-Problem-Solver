# File: agents/router_agent.py

"""
Intent Router Agent: Classifies the structured problem, confirms topic, and routes the workflow.

Decides:
- Confirmed topic
- Required tools (e.g., "sympy_calculator" or "none")
- RAG depth ("deep", "shallow", "none") – influences how much context is used in solver

Uses LangChain chain with Groq LLM and strict JSON output parsing.
"""

from typing import Dict

from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from core.config import Config
from core.prompts import ROUTER_PROMPT

# Reuse the same LLM instance (or create new – but consistent)
llm = ChatGroq(
    api_key=Config.GROQ_API_KEY,
    model_name=Config.LLM_MODEL,
    temperature=Config.LLM_TEMPERATURE,
    max_tokens=Config.LLM_MAX_TOKENS,
)

# JSON parser for strict structured output
json_parser = JsonOutputParser()

# Router chain: prompt → LLM → JSON parse
router_chain = ROUTER_PROMPT | llm | json_parser

def route_problem(structured_problem: Dict) -> Dict[str, any]:
    """
    Run the Router Agent on the structured output from Parser Agent.
    
    Input: structured_problem dict from parser_agent.parse_problem()
    
    Returns:
    {
        "topic": str,                          # Confirmed topic (must be in SUPPORTED_TOPICS)
        "required_tools": list[str],           # e.g., ["sympy_calculator"] or []
        "rag_depth": "deep" | "shallow" | "none"
    }
    
    On failure, returns a safe fallback with algebra topic and basic settings.
    """
    try:
        # Convert structured_problem to JSON string for prompt
        import json
        structured_json = json.dumps(structured_problem, indent=2)
        
        routing_output = router_chain.invoke({"structured_json": structured_json})
        
        # Validate required keys
        required_keys = ["topic", "required_tools", "rag_depth"]
        for key in required_keys:
            if key not in routing_output:
                raise ValueError(f"Missing key in router output: {key}")
        
        # Ensure topic is supported – if not, fallback
        if routing_output["topic"] not in Config.SUPPORTED_TOPICS:
            routing_output["topic"] = "algebra"  # safe default
        
        # Normalize tools
        routing_output["required_tools"] = list(set(routing_output.get("required_tools", [])))
        # Ensure only known tools (currently only sympy_calculator)
        known_tools = ["sympy_calculator"]
        routing_output["required_tools"] = [
            t for t in routing_output["required_tools"] if t in known_tools
        ]
        
        # Validate rag_depth
        valid_rag_depths = ["deep", "shallow", "none"]
        if routing_output["rag_depth"] not in valid_rag_depths:
            routing_output["rag_depth"] = "shallow"  # default
        
        return routing_output
    
    except OutputParserException as e:
        # Fallback on parsing error
        return {
            "topic": structured_problem.get("topic", "algebra"),
            "required_tools": ["sympy_calculator"] if structured_problem.get("topic") in ["algebra", "calculus", "linear_algebra"] else [],
            "rag_depth": "shallow",
            "error": f"Router parsing failed: {str(e)}. Using defaults."
        }
    except Exception as e:
        # General fallback
        return {
            "topic": structured_problem.get("topic", "algebra"),
            "required_tools": ["sympy_calculator"] if structured_problem.get("topic") in ["algebra", "calculus", "linear_algebra"] else [],
            "rag_depth": "shallow",
            "error": f"Unexpected error in routing: {str(e)}"
        }

# Example usage (for local testing)
if __name__ == "__main__":
    sample_structured = {
        "problem_text": "Solve the quadratic equation x² - 5x + 6 = 0",
        "topic": "algebra",
        "variables": ["x"],
        "constraints": [],
        "needs_clarification": False,
        "clarification_needed": ""
    }
    result = route_problem(sample_structured)
    print(result)