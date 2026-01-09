from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
# File: core/config.py

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Central configuration class for the Math Mentor application.
    All configurable values (API keys, thresholds, paths, model names) are defined here.
    Values are loaded from environment variables where possible, with sensible defaults.
    """

    # -----------------------------
    # LLM Configuration (Groq recommended for speed and cost)
    # -----------------------------
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is required in .env")

    LLM_MODEL: str = os.getenv("LLM_MODEL", "meta-llama/llama-4-maverick-17b-128e-instruct")  # Fast and capable for math reasoning
    LLM_TEMPERATURE: float = 0.2  # Low temperature for consistent, deterministic reasoning
    LLM_MAX_TOKENS: int = 2048

    # -----------------------------
    # Embedding Model (local, no API key needed)
    # -----------------------------
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Small, fast, good for semantic similarity

    # -----------------------------
    # Thresholds for HITL triggers
    # -----------------------------
    OCR_CONFIDENCE_THRESHOLD: float = 0.75   # Below this → show preview + allow edit (HITL possible)
    ASR_CONFIDENCE_THRESHOLD: float = 0.75   # Below this → show preview + allow edit
    PARSER_AMBIGUITY_THRESHOLD: float = 0.8  # Parser confidence below this → needs_clarification = True
    VERIFIER_CONFIDENCE_THRESHOLD: float = 0.85  # Below this → trigger HITL

    # -----------------------------
    # RAG Configuration
    # -----------------------------
    VECTOR_STORE_PATH: Path = Path("data/vector_store")
    SOLVED_PROBLEMS_VECTOR_STORE_PATH: Path = Path("data/solved_problems_vector_store")
    KNOWLEDGE_BASE_DIR: Path = Path("knowledge")
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 5
    TOP_K_MEMORY_RETRIEVAL: int = 3  # For similar solved problems

    # -----------------------------
    # Topics supported (for routing and classification)
    # -----------------------------
    SUPPORTED_TOPICS = [
        "algebra",
        "probability",
        "calculus",
        "linear_algebra"
    ]

    # -----------------------------
    # File/Directory Paths
    # -----------------------------
    DATA_DIR: Path = Path("data")
    SESSIONS_DIR: Path = DATA_DIR / "sessions"

    # Ensure required directories exist
    @classmethod
    def ensure_directories(cls):
        cls.VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
        cls.SOLVED_PROBLEMS_VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

# Create directories on import
Config.ensure_directories()
OPENAI_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"