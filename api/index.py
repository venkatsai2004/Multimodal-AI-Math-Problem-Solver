from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Optional

# Your existing imports
from core.multimodal import (
    process_text_input,
    process_image_input,
    process_audio_input
)
from agents.parser_agent import parse_problem
from agents.router_agent import route_problem
from core.rag_hybrid import hybrid_retrieval
from agents.solver_agent import solve_problem
from agents.verifier_agent import verify_solution
from agents.explainer_agent import explain_solution

app = FastAPI()

# -----------------------------
# Request Schema
# -----------------------------
class TextRequest(BaseModel):
    problem: str


# -----------------------------
# Core Pipeline Function
# -----------------------------
def run_pipeline(raw_text: str):
    parsed = parse_problem(raw_text)

    if parsed.get("needs_clarification", False):
        return {
            "status": "clarification_needed",
            "message": parsed.get("clarification_needed", "")
        }

    routing = route_problem(parsed)
    retrieved = hybrid_retrieval(parsed["problem_text"])

    solution = solve_problem(
        problem_text=parsed["problem_text"],
        retrieved=retrieved,
        required_tools=routing.get("required_tools", [])
    )

    verification = verify_solution(parsed["problem_text"], solution)
    explanation = explain_solution(parsed["problem_text"], solution)

    return {
        "status": "success",
        "topic": parsed.get("topic"),
        "solution": solution,
        "explanation": explanation,
        "confidence": verification.get("confidence"),
        "issues": verification.get("issues", []),
        "retrieved": retrieved
    }


# -----------------------------
# TEXT API
# -----------------------------
@app.post("/solve/text")
def solve_text(request: TextRequest):
    extraction = process_text_input(request.problem)
    return run_pipeline(extraction["raw_text"])


# -----------------------------
# IMAGE API
# -----------------------------
@app.post("/solve/image")
async def solve_image(file: UploadFile = File(...)):
    content = await file.read()
    extraction = process_image_input(content)
    return run_pipeline(extraction["raw_text"])


# -----------------------------
# AUDIO API
# -----------------------------
@app.post("/solve/audio")
async def solve_audio(file: UploadFile = File(...)):
    content = await file.read()
    extraction = process_audio_input(content)
    return run_pipeline(extraction["raw_text"])


# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/")
def root():
    return {"message": "Math Mentor API running 🚀"}