<<<<<<< HEAD
# Math Mentor - Multimodal AI Math Problem Solver

A reliable AI-powered math mentor that solves JEE-style math problems with step-by-step explanations. The system accepts math problems in multiple formats (text, images, or audio), uses retrieval-augmented generation (RAG) to find relevant knowledge, and includes human-in-the-loop feedback for continuous learning.

## Features

- **Multimodal Input**: Solve problems by typing text, uploading images (OCR), or speaking (speech-to-text)
- **Structured Problem Parsing**: Automatically cleans and structures raw input into clear math problems
- **RAG Pipeline**: Retrieves relevant formulas, solution patterns, and common mistakes from a knowledge base
- **Multi-Agent System**: Specialized agents for parsing, routing, solving, verification, and explanation
- **Intelligent Verification**: Checks solutions for correctness, domain validity, and edge cases
- **Human-in-the-Loop (HITL)**: When confidence is low, the system asks for human review and learns from corrections
- **Memory & Learning**: Stores solved problems and reuses patterns from similar past solutions
- **Agent Trace**: Shows exactly what each agent did and why - full transparency in reasoning
- **Beautiful UI**: Clean Streamlit interface with organized tabs for solutions, steps, sources, and agent trace

## Supported Math Topics

- Algebra (quadratic equations, polynomials, logarithms, sequences)
- Probability (permutations, combinations, conditional probability, Bayes' theorem)
- Calculus (limits, derivatives, integrals, optimization)
- Linear Algebra (matrices, determinants, eigenvalues, systems of equations)

## Project Structure

```
math-mentor/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration template
├── README.md                  # This file
│
├── agents/                    # Multi-agent system
│   ├── __init__.py
│   ├── parser_agent.py        # Structures raw input → clean problem
│   ├── router_agent.py        # Classifies topic and routes workflow
│   ├── solver_agent.py        # Solves using RAG + tools
│   ├── verifier_agent.py      # Checks correctness and confidence
│   └── explainer_agent.py     # Creates student-friendly explanations
│
├── core/                      # Core functionality
│   ├── __init__.py
│   ├── config.py              # Central configuration (API keys, thresholds)
│   ├── prompts.py             # All LLM prompts for agents
│   ├── multimodal.py          # Image OCR, Audio ASR, Text processing
│   ├── rag_hybrid.py          # Retrieval-augmented generation pipeline
│   └── tools.py               # SymPy calculator and other tools
│
├── memory/                    # Memory and learning systems
│   ├── __init__.py
│   ├── chat_memory.py         # Conversation history within a session
│   └── solved_problems.py     # Vector storage of solved problems
│
├── knowledge/                 # Knowledge base (markdown files)
│   ├── formulas.md            # Comprehensive formula reference
│   ├── common_mistakes.md     # Frequent errors and how to avoid them
│   └── solution_patterns/
│       ├── quadratic.md       # 6 approaches to solving quadratics
│       └── probability_conditional.md  # Conditional probability patterns
│
└── data/                      # Generated at runtime
    ├── vector_store/          # Chroma vector database for knowledge base
    ├── solved_problems_vector_store/  # Vector database of learned problems
    └── sessions/              # Saved session data
    
    
## Architecture (High-Level)
User Input (Text/Image/Audio)
↓
Multimodal Processing → Extracted Text + Confidence
↓
Parser Agent → Structured Problem (topic, variables, etc.)
↓
Router Agent → Choose tools + RAG depth
↓
Hybrid RAG (Knowledge Base + Solved Problems Memory)
↓
Solver Agent (with SymPy tool) → Solution steps + answer
↓
Verifier Agent → Check correctness + confidence
↓
Explainer Agent → Student-friendly explanation
↓
Display + Feedback → Store in memory if corrected




## Tech Stack

- **Frontend**: Streamlit
- **LLM**: Groq (Llama-3.1-70B recommended for reliability)
- **OCR**: EasyOCR
- **ASR**: faster-whisper
- **RAG/Vector Store**: Chroma + sentence-transformers
- **Agents**: LangChain (tool-calling agents)
- **Math Tool**: SymPy (symbolic calculation)
- **Memory**: Chroma vector store for solved problems


```

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/venkatsai2004/-Multimodal-AI-Math-Problem-Solver.git
cd math-mentor
```

### 2. Create a Python Virtual Environment

Recommend using a virtual environment to avoid conflicts with other packages.

```bash
# On Windows
Python 3.12 (recommended)
python -m venv venv
venv\Scripts\activate

# On macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages including LangChain, Groq, Streamlit, EasyOCR, faster-whisper, SymPy, and vector databases.

### 4. Get Groq API Key

The system uses Groq for fast, reliable LLM inference (free tier available).

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Create a new API key
4. Copy the key

### 5. Configure Environment Variables

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env and add your Groq API key
# On Windows: notepad .env
# On macOS/Linux: nano .env
```

Your `.env` file should look like:

```
GROQ_API_KEY="your_actual_api_key_here"
LLM_MODEL=llama3-70b-8192
EMBEDDING_MODEL=all-MiniLM-L6-v2
OCR_CONFIDENCE_THRESHOLD=0.75
ASR_CONFIDENCE_THRESHOLD=0.75
VERIFIER_CONFIDENCE_THRESHOLD=0.85
```


### 6. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## How to Use

### Solving a Math Problem

1. **Choose Input Mode** (Sidebar): Select whether you'll enter text, upload an image, or record audio
2. **Provide Your Problem**: Type the problem, upload an image of it, or speak it out
3. **Review Extraction**: If OCR or speech confidence is low, you can edit the extracted text
4. **Click "Solve Problem"**: The system runs the full workflow
5. **Review Results**: Check the solution, explanation, steps, and sources used
6. **Provide Feedback**: Mark as correct/incorrect so the system learns

### Input Examples

**Text Input:**
```
Solve the quadratic equation x^2 - 5x + 6 = 0
```

**Image Input:**
Upload a screenshot or photo of a handwritten or printed math problem.

**Audio Input:**
Record yourself saying: "Find the probability of getting exactly two heads when flipping a fair coin three times"


### Deployment
Easy deployment options:

Streamlit Community Cloud (free): Connect your GitHub repo
Hugging Face Spaces (free tier works)

### Known Limitations & Improvements

OCR sometimes misreads superscripts (e.g., "x2" instead of "x²") → use HITL edit
Audio works best with clear English speech
For best accuracy, use 70B model (8B is faster but less reliable)

## How It Works (Workflow)

When you submit a problem, this is what happens behind the scenes:

1. **Multimodal Processing**: Your input (text, image, or audio) is converted to clean text with confidence scores
2. **Parser Agent**: Structures the raw text into a formal problem with topic, variables, and constraints
3. **Router Agent**: Analyzes the problem and decides which tools and knowledge depth to use
4. **RAG Retrieval**: Searches the knowledge base for relevant formulas and solution patterns
5. **Solver Agent**: Uses the retrieved knowledge plus SymPy tools to solve the problem step-by-step
6. **Verifier Agent**: Checks if the solution is mathematically correct and identifies any issues
7. **Explainer Agent**: Transforms the solution into a clear, student-friendly explanation
8. **Memory Storage**: Saves the solved problem so similar future problems can reuse the pattern

If at any step the confidence is too low, the Human-in-the-Loop (HITL) system asks for your input to correct or clarify.

## Architecture Diagram

```
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
```

## Configuration

All configurable settings are in `core/config.py` and can be overridden via environment variables in `.env`:

- **GROQ_API_KEY**: Your Groq API key (required)
- **LLM_MODEL**: Which Groq model to use (default: llama3-70b-8192)
- **OCR_CONFIDENCE_THRESHOLD**: When to show OCR preview for editing (default: 0.75)
- **VERIFIER_CONFIDENCE_THRESHOLD**: When to trigger HITL review (default: 0.85)
- **TOP_K_RETRIEVAL**: How many knowledge sources to retrieve (default: 5)

See `.env.example` for complete list and explanations.

## Knowledge Base

The system comes with a curated knowledge base in the `knowledge/` directory:

- **formulas.md**: 100+ formulas across all supported topics
- **common_mistakes.md**: Frequent errors and how to avoid them
- **solution_patterns/quadratic.md**: 6 different approaches to solving quadratics
- **solution_patterns/probability_conditional.md**: 6 patterns for conditional probability

When you solve your first problem, the system automatically:
1. Loads all markdown files from `knowledge/`
2. Chunks them into ~1000 character pieces
3. Embeds them using sentence-transformers (local, no API needed)
4. Stores them in Chroma vector database (`data/vector_store/`)
5. Retrieves relevant chunks for each new problem

You can add more knowledge files - just create new `.md` files in the `knowledge/` directory and they'll be indexed automatically on the next run.

## Human-in-the-Loop (HITL)

The system triggers a human review when:

1. **OCR/ASR Low Confidence**: Image or speech extraction uncertainty high → shows extracted text for you to edit
2. **Parser Ambiguity**: Problem statement is unclear or incomplete → asks you to clarify
3. **Verifier Low Confidence**: Solution might be wrong → explains issues and asks for confirmation
4. **User Feedback**: You mark a solution as incorrect → system learns the correction

When HITL is triggered, you can:
- Edit the problem statement for clarity
- Confirm or correct the solution
- Provide the right answer
- Add comments explaining what was wrong

All corrections are stored in memory and used to improve future similar problems.

## Memory & Self-Learning

The system builds a growing knowledge base from your interactions:

1. **Solved Problems Database**: Every completed problem is stored with its solution and feedback
2. **Pattern Reuse**: When you solve a similar problem, the system retrieves solutions to previous similar problems
3. **Correction Learning**: When you correct a solution via HITL, the system stores this correction and reuses the pattern
4. **No Retraining Required**: All learning happens through vector similarity search - no model retraining needed

Vector databases are stored in:
- `data/vector_store/` - original knowledge base
- `data/solved_problems_vector_store/` - learned problems

## Deployment

### Streamlit Cloud Or HuggingFace (Recommended for demo)

1. Push your code to GitHub
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Click "New app" and select your repository
4. Set environment variables in Streamlit Cloud dashboard
5. Deploy!

### Other Platforms

- **Hugging Face Spaces**: Use the Streamlit template
- **Render**: Create a `render.yaml` with `streamlit run app.py`
- **Railway**: Similar to Render, specify startup command

All require you to set `GROQ_API_KEY` as a secret environment variable.

## Example Usage

### Example 1: Solve a quadratic equation (text input)

```
Input: "Solve x^2 - 5x + 6 = 0"

Workflow:
1. Parser recognizes this as algebra, quadratic equation
2. Router decides to use sympy_calculator
3. RAG retrieves quadratic formula and factorization patterns
4. Solver uses factorization: (x-2)(x-3)=0
5. Verifier confirms: x=2 and x=3 satisfy original equation ✓
6. Explainer provides step-by-step solution
7. Memory stores this solved problem

Output:
Problem: Solve x² - 5x + 6 = 0
Solution: We can factor this as (x - 2)(x - 3) = 0
Therefore: x = 2 or x = 3
Confidence: 99%
```

### Example 2: Upload a handwritten problem (image input)

```
Input: [Upload photo of handwritten problem from textbook]

Workflow:
1. OCR extracts text (may have errors/low confidence)
2. User reviews and corrects extracted text (HITL)
3. Rest of workflow proceeds as above
4. Solution stored with note: "OCR from handwritten source"

Output:
Extracted: "Find the probability that..."
[User corrects if needed]
Solution: [Probability calculation with explanation]
```

### Example 3: Probability problem with HITL

```
Input: "In a bag there are 3 red and 2 blue balls. Find P(both red) without replacement"

Workflow:
1. Parser identifies as probability, conditional probability
2. Router sets RAG depth to "deep" (probability needs careful handling)
3. RAG retrieves conditional probability patterns
4. Solver calculates: P(both red) = (3/5) × (2/4) = 3/10
5. Verifier checks: probability between 0-1 ✓, sample space correct ✓
6. Explainer shows complete solution with tree diagram concept

Output:
Step 1: Probability first ball is red = 3/5
Step 2: If first is red, probability second is red = 2/4 = 1/2
Step 3: P(both red) = 3/5 × 1/2 = 3/10 = 0.3
Confidence: 98%
```

## Troubleshooting

### "GROQ_API_KEY not found"
Make sure you've created `.env` file and added your actual Groq API key.

### "OCR confidence very low"
This might happen with low-quality images. Try:
- Taking a clearer photo
- Using better lighting
- Manually typing the problem instead

### "Solution seems incorrect"
Click "Incorrect" feedback button and provide the correct answer. The system learns from corrections.

### "Audio transcription is garbled"
Speak clearly and slowly. The Whisper model handles math terms well but struggles with fast speech.

## Contributing

To improve the knowledge base:

1. Create new `.md` files in `knowledge/solution_patterns/`
2. Document solution approaches with examples
3. The system will automatically index them on next run

To improve prompts:
1. Edit prompts in `core/prompts.py`
2. Test with sample problems
3. Share improvements!

## License

MIT License - feel free to use and modify for educational purposes.

## Support

- **Issues**: Open a GitHub issue with details about your problem
- **Questions**: Check the documentation above first
- **Feedback**: Use the feedback buttons in the app - they help the system learn!

## Roadmap

Future improvements planned:

- More math topics (trigonometry, complex numbers, statistics)
- Better OCR with handwriting recognition
- LaTeX input support
- Multi-language support
- Mobile app version
- Integration with popular online judges
- Batch problem solving

## Acknowledgments

Built with:
- LangChain for agent orchestration
- Groq for fast LLM inference
- Streamlit for the beautiful UI
- Chroma for vector storage
- EasyOCR and faster-whisper for multimodal input
=======
---
title: Multimodal Ai Math Problem Solver
emoji: 🚀
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
tags:
- streamlit
pinned: false
short_description: A multimodal AI assistant that solves complex math problems
license: mit
---

# Welcome to Streamlit!

Edit `/src/streamlit_app.py` to customize this app to your heart's desire. :heart:

If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).
>>>>>>> 06e8cac20a376cb8ee7f5b959134b0f513f67ab2
