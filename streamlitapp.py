# File: app.py
"""
Main Streamlit application for Reliable Multimodal Math Mentor.

Orchestrates:
- Multimodal input (text / image / audio)
- Extraction preview + HITL edit
- Agent pipeline (Parser → Router → RAG + Solver → Verifier → Explainer)
- Shows agent trace, retrieved context, confidence
- Feedback buttons → store to memory (including corrections)
"""

import streamlit as st
from pathlib import Path

# Core components
from core.config import Config
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
from memory.solved_problems import store_solved_problem
from memory.chat_memory import (
    initialize_session_state,
    clear_current_problem_state,
    store_current_problem_state,
    add_agent_trace,
    get_current_problem_state
)

# -----------------------------
# Page Config & Setup
# -----------------------------
st.set_page_config(
    page_title="Math Mentor • Reliable JEE Math Helper",
    page_icon="🧠",
    layout="wide"
)

# Load config & initialize session
Config.ensure_directories()
initialize_session_state()

st.title("🧠 Math Mentor")
st.caption("Reliable multimodal math solver for JEE-style problems (Algebra, Probability, Calculus basics, Linear Algebra)")

# -----------------------------
# Sidebar – Input Mode Selector
# -----------------------------
st.sidebar.header("Input Mode")
input_mode = st.sidebar.radio(
    "Choose how to provide the problem:",
    ["Text", "Image (photo/screenshot)", "Audio (speak)"],
    index=0
)

# -----------------------------
# Main Area – Input Handling
# -----------------------------
extraction = None

if input_mode == "Text":
    problem_input = st.text_area(
        "Type your math problem here:",
        height=120,
        placeholder="e.g. Solve the equation x² - 5x + 6 = 0"
    )
    if problem_input:
        extraction = process_text_input(problem_input)

elif input_mode == "Image (photo/screenshot)":
    uploaded_file = st.file_uploader("Upload JPG/PNG image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        extraction = process_image_input(image_bytes)
        st.image(image_bytes, caption="Uploaded image", use_column_width=True)

elif input_mode == "Audio (speak)":
    st.info("Audio input via file upload (WAV/MP3/M4A/OGG supported)")
    audio_file = st.file_uploader("Upload audio file", type=["wav", "mp3", "m4a", "ogg"])
    if audio_file is not None:
        audio_bytes = audio_file.read()
        extraction = process_audio_input(audio_bytes)

# -----------------------------
# Extraction Preview + HITL Edit
# -----------------------------
if extraction is not None:
    confidence = extraction["confidence"]
    source = extraction["source"]
    
    st.subheader("Extracted Text Preview")
    col1, col2 = st.columns([6, 1])
    with col1:
        edited_text = st.text_area(
            f"Extracted from {source} (confidence: {confidence:.2%})",
            value=extraction["raw_text"],
            height=100,
            key="edit_extracted"
        )
    
    # Confidence-based warning
    if confidence < Config.OCR_CONFIDENCE_THRESHOLD and source in ["image", "audio"]:
        st.warning("Low confidence extraction. Please review and edit if needed.")
    
    # Proceed button
    if st.button("→ Solve this problem", type="primary"):
        final_raw_text = edited_text.strip()
        if not final_raw_text:
            st.error("No problem text provided.")
        else:
            with st.spinner("Processing problem..."):
                add_agent_trace("Starting new problem")
                add_agent_trace(f"Input mode: {source} • Confidence: {confidence:.2%}")
                
                # Step 1: Parser Agent
                add_agent_trace("Running Parser Agent...")
                parsed = parse_problem(final_raw_text)
                store_current_problem_state(parsed=parsed)
                add_agent_trace(f"Parser → Topic: {parsed['topic']}")
                
                if parsed.get("needs_clarification", False):
                    st.warning("Parser detected ambiguity:\n" + parsed.get("clarification_needed", ""))
                    st.info("You can edit the text above and try again.")
                else:
                    # Step 2: Router Agent
                    add_agent_trace("Running Router Agent...")
                    routing = route_problem(parsed)
                    store_current_problem_state(routing=routing)
                    add_agent_trace(f"Router → Tools: {routing.get('required_tools', [])} • RAG: {routing.get('rag_depth', 'shallow')}")
                    
                    # Step 3: Hybrid RAG Retrieval
                    add_agent_trace("Performing hybrid RAG retrieval...")
                    retrieved = hybrid_retrieval(parsed["problem_text"])
                    store_current_problem_state(retrieved=retrieved)
                    add_agent_trace(f"Retrieved {len(retrieved)} relevant chunks")
                    
                    # Step 4: Solver Agent
                    add_agent_trace("Running Solver Agent...")
                    solution = solve_problem(
                        problem_text=parsed["problem_text"],
                        retrieved=retrieved,
                        required_tools=routing.get("required_tools", [])
                    )
                    store_current_problem_state(solution=solution)
                    add_agent_trace("Solver completed")
                    
                    # Step 5: Verifier Agent
                    add_agent_trace("Running Verifier Agent...")
                    verification = verify_solution(parsed["problem_text"], solution)
                    store_current_problem_state(verification=verification)
                    add_agent_trace(f"Verifier confidence: {verification['confidence']:.2%}")
                    
                    # Step 6: Explainer Agent
                    add_agent_trace("Running Explainer Agent...")
                    explanation = explain_solution(parsed["problem_text"], solution)
                    store_current_problem_state(explanation=explanation)
                    add_agent_trace("Explanation ready")
                    
                    st.success("Processing complete!")
                    
                    # Display results
                    st.subheader("Solution & Explanation")
                    st.markdown(explanation)
                    
                    # Confidence indicator
                    st.markdown(f"**Verifier Confidence:** {verification['confidence']:.1%}")
                    if verification.get("issues"):
                        st.warning("Verifier found issues:\n" + "\n".join(verification["issues"]))
                    
                    # Retrieved sources panel
                    if retrieved:
                        with st.expander("Retrieved Context Sources"):
                            for i, ctx in enumerate(retrieved):
                                st.markdown(f"**Source {i}** [{ctx['type']}] (relevance: {ctx.get('relevance_score', 'N/A')})")
                                st.caption(ctx['content'])
                    
                    # Feedback buttons
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("✅ Correct", key="feedback_correct"):
                            store_solved_problem(
                                original_extraction=extraction,
                                parsed_problem=parsed,
                                retrieved_context=retrieved,
                                solution=solution,
                                verification=verification,
                                user_feedback="correct"
                            )
                            st.success("Thank you! Solution stored for future improvement.")
                            clear_current_problem_state()
                            st.rerun()
                    
                    with col_no:
                        incorrect_reason = st.text_input("What was wrong? (optional)", key="incorrect_reason")
                        if st.button("❌ Incorrect", key="feedback_incorrect"):
                            # Simple correction (you can expand this with edit boxes if needed)
                            store_solved_problem(
                                original_extraction=extraction,
                                parsed_problem=parsed,
                                retrieved_context=retrieved,
                                solution=solution,
                                verification=verification,
                                user_feedback=incorrect_reason or "incorrect"
                            )
                            st.success("Correction stored. Thank you for helping the system learn!")
                            clear_current_problem_state()
                            st.rerun()

# -----------------------------
# Agent Trace (collapsible)
# -----------------------------
if st.session_state.get("agent_trace"):
    with st.expander("Agent Execution Trace (for debugging)"):
        for step in st.session_state["agent_trace"]:
            st.write(f"• {step}")

# -----------------------------
# Clear button
# -----------------------------
if st.button("Clear & Start New Problem"):
    clear_current_problem_state()
    st.rerun()