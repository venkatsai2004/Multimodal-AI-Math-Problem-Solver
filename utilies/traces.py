# utils/trace.py  (new file - create this)
from typing import List, Dict, Any
import streamlit as st

class AgentTrace:
    """Simple in-memory trace logger for agent execution steps"""
    
    def __init__(self):
        if "agent_trace" not in st.session_state:
            st.session_state.agent_trace = []
    
    def add_step(self, agent_name: str, action: str, details: Any = None, status: str = "running"):
        """
        Add a trace entry
        - agent_name: e.g., "Parser Agent"
        - action: short description, e.g., "Cleaning input text"
        - details: optional dict or string with more info
        - status: "running" | "success" | "warning" | "error"
        """
        step = {
            "agent": agent_name,
            "action": action,
            "details": details,
            "status": status
        }
        st.session_state.agent_trace.append(step)
    
    def clear(self):
        st.session_state.agent_trace = []
    
    def get_trace(self) -> List[Dict]:
        return st.session_state.agent_trace.copy()