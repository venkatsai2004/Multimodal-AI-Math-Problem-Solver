# agents/solver_agent.py (simplified & robust for 70B models)

from typing import Dict, List
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from core.config import Config
from core.tools import tools as available_tools

llm = ChatGroq(
    api_key=Config.GROQ_API_KEY,
    model_name=Config.LLM_MODEL,
    temperature=0.0,  # Critical for JSON compliance
    max_tokens=Config.LLM_MAX_TOKENS,
)

parser = JsonOutputParser()

def create_solver_agent(bound_tools: List) -> AgentExecutor:
    system_prompt = """
You are an expert Math Solver Agent.
Solve the problem step-by-step.
Use tools when needed for exact computation.
Use retrieved context only if relevant.
You MUST output ONLY valid JSON in this exact format (no extra text):
{format_instructions}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Problem:\n{problem_text}\n\nContext:\n{retrieved_context}"),
        ("placeholder", "{agent_scratchpad}"),
    ]).partial(format_instructions=parser.get_format_instructions())

    agent = create_tool_calling_agent(llm, bound_tools, prompt)
    return AgentExecutor(agent=agent, tools=bound_tools, verbose=False, max_iterations=12)

def solve_problem(problem_text: str, retrieved: List[Dict], required_tools: List[str]) -> Dict:
    bound_tools = [t for t in available_tools if t.name in required_tools]

    context_str = "\n\n".join(
        f"{i}. {c['content']}" for i, c in enumerate(retrieved)
    ) if retrieved else "No context."

    executor = create_solver_agent(bound_tools)

    try:
        response = executor.invoke({
            "problem_text": problem_text,
            "retrieved_context": context_str
        })
        raw = response["output"]
        structured = parser.parse(raw)
        return {
            "answer": structured.get("answer", "No answer"),
            "steps": structured.get("steps", ["No steps"]),
            "used_sources": structured.get("used_sources", [])
        }
    except Exception as e:
        return {
            "answer": "Solver execution failed",
            "steps": [f"Error: {str(e)}"],
            "used_sources": []
        }