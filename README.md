# 🧠 Math Mentor - Reliable Multimodal JEE Math Solver

[![Hugging Face Spaces](https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/Vsai2004/multimodal_ai_math_solver)

## 📸 App Preview
<img src="Screenshot 2026-01-09 161927.png" alt="MAth Mentor App Preview" width="900"/>


## About


This is a **Reliable Multimodal Math Mentor** built for the AI Engineer Assignment.

The app solves JEE-style math problems (algebra, probability, basic calculus, linear algebra) using:

- **Multimodal Input**: Text, Image (photo/screenshot), Audio (spoken)
- **RAG**: Curated knowledge base + memory of solved problems
- **Multi-Agent System**: Parser → Router → Solver → Verifier → Explainer
- **Human-in-the-Loop (HITL)**: Preview & edit extracted text when confidence low
- **Memory & Self-Learning**: Stores solved/corrected problems for reuse

**Assignment Compliance**: Fully meets all mandatory requirements (multimodal, RAG, agents, HITL, memory, deployed app).

## Live Demo

Try the app here:[(https://huggingface.co/spaces/Vsai2004/multimodal_ai_math_solve)](https://huggingface.co/spaces/Vsai2004/multimodal_ai_math_solver)

## How It Works (Workflow)
When you submit a problem, this is what happens behind the scenes:

Multimodal Processing: Your input (text, image, or audio) is converted to clean text with confidence scores
Parser Agent: Structures the raw text into a formal problem with topic, variables, and constraints
Router Agent: Analyzes the problem and decides which tools and knowledge depth to use
RAG Retrieval: Searches the knowledge base for relevant formulas and solution patterns
Solver Agent: Uses the retrieved knowledge plus SymPy tools to solve the problem step-by-step
Verifier Agent: Checks if the solution is mathematically correct and identifies any issues
Explainer Agent: Transforms the solution into a clear, student-friendly explanation
Memory Storage: Saves the solved problem so similar future problems can reuse the pattern

If at any step the confidence is too low, the Human-in-the-Loop (HITL) system asks for your input to correct or clarify.
Architecture Diagram
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE (Streamlit)                   │
│  Text / Image / Audio Input → Preview & Edit → Solve Button    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │    MULTIMODAL INPUT PROCESSING        │
        ├──────────────────────────────────────┤
        │ • Text: passthrough                   │
        │ • Image: EasyOCR                      │
        │ • Audio: faster-whisper (ASR)         │
        │ Output: raw_text + confidence         │
        └──────────────────┬───────────────────┘
                           │
                           ▼
     ┌─────────────────────────────────────────────┐
     │      PARSER AGENT (core/prompts.py)          │
     │ Input: raw text with noise/OCR errors        │
     ├─────────────────────────────────────────────┤
     │ • Clean & normalize text                     │
     │ • Identify topic (algebra/probability/...)   │
     │ • Extract variables & constraints            │
     │ • Detect ambiguity → trigger HITL if needed  │
     │ Output: structured problem                   │
     └────────────────┬────────────────────────────┘
                      │
                      ▼
    ┌──────────────────────────────────────────────┐
    │     ROUTER AGENT (agents/router_agent.py)     │
    │ Input: structured problem                     │
    ├──────────────────────────────────────────────┤
    │ • Confirm topic classification                │
    │ • Decide required tools (sympy_calculator)    │
    │ • Set RAG depth (deep/shallow/none)           │
    │ Output: routing decision                      │
    └──────────────┬───────────────────────────────┘
                   │
         ┌─────────┴──────────┐
         │                    │
         ▼                    ▼
   ┌──────────────┐   ┌──────────────────────┐
   │ HYBRID RAG   │   │  SOLVER AGENT        │
   │              │   │                      │
   │ 1. KB Retrieval  │ • Use retrieved RAG  │
   │ 2. Memory   │   │ • Call sympy tools   │
   │    Retrieval │   │ • Reason step-by-step│
   │              │   │ Output: steps +answer│
   │ Returns:    │   └──────────┬───────────┘
   │ Relevant    │              │
   │ chunks with │              ▼
   │ sources     │   ┌──────────────────────┐
   └──────────────┘   │  VERIFIER AGENT      │
                      │                      │
                      │ • Check correctness  │
                      │ • Verify domain      │
                      │ • Test edge cases    │
                      │ • Confidence score   │
                      │                      │
                      │ If low confidence    │
                      │ → trigger HITL       │
                      │                      │
                      │ Output: is_correct,  │
                      │ confidence, issues   │
                      └──────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  EXPLAINER AGENT       │
                    │                        │
                    │ Make solution clear    │
                    │ for students           │
                    │ Step-by-step style     │
                    │ Highlight concepts     │
                    │                        │
                    │ Output: explanation    │
                    └──────────┬─────────────┘
                               │
                               ▼
        ┌──────────────────────────────────────┐
        │  MEMORY & LEARNING LAYER              │
        ├──────────────────────────────────────┤
        │ • Store solved problem in vector DB   │
        │ • Track user feedback (correct/fix)   │
        │ • Store HITL corrections              │
        │ • Enable pattern reuse for similar    │
        │   future problems                     │
        └──────────────────────────────────────┘
                               │
                               ▼
        ┌──────────────────────────────────────┐
        │   DISPLAY RESULTS TO USER             │
        ├──────────────────────────────────────┤
        │ • Final solution & explanation        │
        │ • Step-by-step breakdown              │
        │ • Retrieved sources with citations    │
        │ • Complete agent trace (transparency) │
        │ • Confidence indicators               │
        │ • Feedback buttons                    │
        └──────────────────────────────────────┘


**Note**: First load may take 10–20 minutes (model downloads). Use a Groq API key in Space secrets for full functionality.

## Features

- Type, upload image, or speak a math problem
- OCR (EasyOCR) for images, ASR (faster-whisper) for audio
- Extracted text preview with confidence + manual edit (HITL)
- Step-by-step solution + student-friendly explanation
- Verifier confidence + feedback buttons (Correct/Incorrect)
- Agent execution trace for debugging
- Memory reuse on similar problems

## How to Use

1. Select input mode (Text / Image / Audio)
2. Enter your math problem
3. Review extracted text (edit if needed)
4. Click "Solve this problem"
5. Read the explanation
6. Give feedback to help the system learn

**Tip**: For best results, use clear images/speech and the 70B model (set via `LLM_MODEL` secret).

## Tech Stack

- **UI**: Streamlit
- **LLM**: Groq (Llama3-70B recommended)
- **OCR**: EasyOCR
- **ASR**: faster-whisper
- **RAG/Vector Store**: Chroma + sentence-transformers
- **Agents**: LangChain
- **Math Tool**: SymPy

## Local Development

```bash
git clone https://github.com/[YOUR-USERNAME]/math-mentor.git
cd math-mentor

python -m venv .venv
. .venv/Scripts/activate  # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt

cp .env.example .env
# Add your GROQ_API_KEY to .env
# Optional: LLM_MODEL=llama3-70b-8192

streamlit run app.py
