# File: memory/chat_memory.py

"""
Simple chat memory layer for the Math Mentor application.

Since most interactions are single-turn (question → solution → feedback), 
we use a lightweight in-memory approach based on Streamlit session state.

This file provides:
- Helper functions to store/retrieve the current conversation state
- Basic conversation history (for potential future multi-turn clarification)
- No persistent storage here — persistence happens only via solved_problems vector store

For multi-turn support in the future (e.g., "explain step 3 again", "why not this method?"):
- We can later extend this with LangChain ConversationBufferMemory or similar
"""

from typing import List, Dict, Optional
import streamlit as st

# Session state keys
SESSION_KEY_HISTORY = "chat_history"
SESSION_KEY_CURRENT_INPUT = "current_input"
SESSION_KEY_CURRENT_EXTRACTION = "current_extraction"
SESSION_KEY_PARSED_PROBLEM = "parsed_problem"
SESSION_KEY_ROUTING = "routing_result"
SESSION_KEY_RETRIEVED = "retrieved_context"
SESSION_KEY_SOLUTION = "solution"
SESSION_KEY_VERIFICATION = "verification"
SESSION_KEY_EXPLANATION = "explanation"
SESSION_KEY_AGENT_TRACE = "agent_trace"

def initialize_session_state():
    """Initialize all required session state keys if they don't exist."""
    defaults = {
        SESSION_KEY_HISTORY: [],
        SESSION_KEY_CURRENT_INPUT: None,
        SESSION_KEY_CURRENT_EXTRACTION: None,
        SESSION_KEY_PARSED_PROBLEM: None,
        SESSION_KEY_ROUTING: None,
        SESSION_KEY_RETRIEVED: [],
        SESSION_KEY_SOLUTION: None,
        SESSION_KEY_VERIFICATION: None,
        SESSION_KEY_EXPLANATION: None,
        SESSION_KEY_AGENT_TRACE: []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_to_history(message: Dict):
    """
    Add a message to conversation history.
    Message format: {"role": "user"/"assistant", "content": str, "type": "text"/"solution"/"feedback"}
    """
    initialize_session_state()
    st.session_state[SESSION_KEY_HISTORY].append(message)


def get_conversation_history() -> List[Dict]:
    """Get full conversation history for current session."""
    initialize_session_state()
    return st.session_state[SESSION_KEY_HISTORY]


def clear_current_problem_state():
    """Reset state for a new problem (keep history)"""
    initialize_session_state()
    st.session_state[SESSION_KEY_CURRENT_INPUT] = None
    st.session_state[SESSION_KEY_CURRENT_EXTRACTION] = None
    st.session_state[SESSION_KEY_PARSED_PROBLEM] = None
    st.session_state[SESSION_KEY_ROUTING] = None
    st.session_state[SESSION_KEY_RETRIEVED] = []
    st.session_state[SESSION_KEY_SOLUTION] = None
    st.session_state[SESSION_KEY_VERIFICATION] = None
    st.session_state[SESSION_KEY_EXPLANATION] = None
    st.session_state[SESSION_KEY_AGENT_TRACE] = []


def store_current_problem_state(
    input_data: Dict = None,
    extraction: Dict = None,
    parsed: Dict = None,
    routing: Dict = None,
    retrieved: List = None,
    solution: Dict = None,
    verification: Dict = None,
    explanation: str = None,
    trace_entry: str = None
):
    """Update current problem state in session."""
    initialize_session_state()
    
    if input_data is not None:
        st.session_state[SESSION_KEY_CURRENT_INPUT] = input_data
    if extraction is not None:
        st.session_state[SESSION_KEY_CURRENT_EXTRACTION] = extraction
    if parsed is not None:
        st.session_state[SESSION_KEY_PARSED_PROBLEM] = parsed
    if routing is not None:
        st.session_state[SESSION_KEY_ROUTING] = routing
    if retrieved is not None:
        st.session_state[SESSION_KEY_RETRIEVED] = retrieved
    if solution is not None:
        st.session_state[SESSION_KEY_SOLUTION] = solution
    if verification is not None:
        st.session_state[SESSION_KEY_VERIFICATION] = verification
    if explanation is not None:
        st.session_state[SESSION_KEY_EXPLANATION] = explanation
    if trace_entry:
        st.session_state[SESSION_KEY_AGENT_TRACE].append(trace_entry)


def get_current_problem_state() -> Dict:
    """Get all current problem-related data as a dict."""
    initialize_session_state()
    return {
        "input": st.session_state[SESSION_KEY_CURRENT_INPUT],
        "extraction": st.session_state[SESSION_KEY_CURRENT_EXTRACTION],
        "parsed": st.session_state[SESSION_KEY_PARSED_PROBLEM],
        "routing": st.session_state[SESSION_KEY_ROUTING],
        "retrieved": st.session_state[SESSION_KEY_RETRIEVED],
        "solution": st.session_state[SESSION_KEY_SOLUTION],
        "verification": st.session_state[SESSION_KEY_VERIFICATION],
        "explanation": st.session_state[SESSION_KEY_EXPLANATION],
        "trace": st.session_state[SESSION_KEY_AGENT_TRACE]
    }


def add_agent_trace(step: str):
    """Add a line to the agent execution trace (for UI display)."""
    initialize_session_state()
    st.session_state[SESSION_KEY_AGENT_TRACE].append(step)