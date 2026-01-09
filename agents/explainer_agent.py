# File: agents/explainer_agent.py

"""
Explainer / Tutor Agent: Produces a clear, student-friendly, step-by-step explanation.

Uses a simple LangChain chain (no tools needed).
Takes the verified solution (steps + answer) and turns it into an engaging tutorial-style response.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from core.config import Config
from core.prompts import EXPLAINER_PROMPT

# Shared LLM (slightly higher temperature for more engaging explanations)
llm = ChatGroq(
    api_key=Config.GROQ_API_KEY,
    model_name=Config.LLM_MODEL,
    temperature=0.4,  # Slightly higher for natural, engaging tone
    max_tokens=Config.LLM_MAX_TOKENS,
)

# Explainer chain (no output parser needed – free-form text output)
explainer_chain = EXPLAINER_PROMPT | llm


def explain_solution(
    problem_text: str,
    solution: dict,  # From solver_agent: {"answer": ..., "steps": [...]}
) -> str:
    """
    Run the Explainer Agent.

    Returns a string with the full student-friendly explanation.
    Includes boxed final answer.
    """
    final_answer = solution.get("answer", "No answer provided")
    steps_str = "\n".join(solution.get("steps", ["No steps available"]))

    try:
        response = explainer_chain.invoke(
            {
                "problem_text": problem_text,
                "solution_steps": steps_str,
                "final_answer": final_answer,
            }
        )

        explanation = response.content.strip()

        # Optional post-processing: ensure boxed answer if missing
        if "\\boxed" not in explanation and final_answer:
            explanation += f"\n\n**Final Answer:** \\boxed{{{final_answer}}}"

        return explanation

    except Exception as e:
        # Fallback explanation
        return f"""
**Problem:** {problem_text}

**Explanation (fallback due to error: {str(e)}):**

The solution steps were:
{steps_str}

**Final Answer:** {final_answer}
"""


# Local testing example
if __name__ == "__main__":
    sample_problem = "Solve the quadratic equation x² - 5x + 6 = 0"
    sample_solution = {
        "answer": "2, 3",
        "steps": [
            "The equation is x² - 5x + 6 = 0",
            "Factorize: (x - 2)(x - 3) = 0",
            "Therefore, x = 2 or x = 3",
        ],
    }

    explanation = explain_solution(sample_problem, sample_solution)
    print(explanation)
