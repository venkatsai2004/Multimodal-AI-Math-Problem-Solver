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

```mermaid
flowchart TD

%% UI
A[User Input: Text / Image / Audio] --> B[Streamlit UI]
B --> C[Preview & Edit]
C --> D[Solve Button]

%% Input Processing
D --> E[Multimodal Processing]
E --> E1[Text: passthrough]
E --> E2[Image: OCR (EasyOCR)]
E --> E3[Audio: Whisper ASR]
E --> F[Raw Text + Confidence]

%% Parser
F --> G[Parser Agent]
G --> G1[Clean & Normalize Text]
G --> G2[Extract Variables & Constraints]
G --> G3[Detect Ambiguity]
G --> H[Structured Problem]

%% Router
H --> I[Router Agent]
I --> I1[Topic Classification]
I --> I2[Select Tools]
I --> I3[Set RAG Depth]

%% RAG + Solver
I --> J[Hybrid RAG System]
J --> J1[Knowledge Base Retrieval]
J --> J2[Memory Retrieval]

J --> K[Solver Agent]
K --> K1[Step-by-step Reasoning]
K --> K2[Use SymPy Tools]
K --> L[Solution + Answer]

%% Verification
L --> M[Verifier Agent]
M --> M1[Check Correctness]
M --> M2[Test Edge Cases]
M --> M3[Confidence Score]

%% HITL
M -->|Low Confidence| N[Human-in-the-Loop]

%% Explanation
M --> O[Explainer Agent]
O --> P[Student-friendly Explanation]

%% Output
P --> Q[Final Output to UI]
```**Note**: First load may take 10–20 minutes (model downloads). Use a Groq API key in Space secrets for full functionality.

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
