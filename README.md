---
title: Math Mentor - Reliable Multimodal JEE Math Solver
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.52.2
app_file: app.py
pinned: false
license: apache-2.0
---

# 🧠 Math Mentor - Reliable Multimodal JEE Math Solver

[![Hugging Face Spaces](https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/Vsai2004/multimodal_ai_math_solver)

![App Preview](<img width="1919" height="969" alt="Screenshot 2026-01-09 161927" src="https://github.com/user-attachments/assets/39b91f32-05fd-4374-b00e-e8d4075ffb2a" />)  


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
