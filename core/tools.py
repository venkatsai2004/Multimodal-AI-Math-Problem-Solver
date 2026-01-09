# File: core/tools.py

"""
Tools for the Math Mentor application.
Currently provides a safe SymPy-based calculator tool using PythonAstREPLTool.
This allows symbolic mathematics without risking arbitrary code execution.
"""

import sympy as sp
from langchain_experimental.tools.python.tool import PythonAstREPLTool
from langchain_core.tools import Tool

# Safe SymPy calculator tool
# Uses PythonAstREPLTool which only evaluates expressions (no statements, no imports, no side effects)
# Locals pre-loaded with 'sp' = sympy
sympy_calculator = PythonAstREPLTool(
    name="sympy_calculator",
    description="""
    Evaluates a single Python expression using SymPy for symbolic and numerical mathematics.
    Use the prefix 'sp.' to access SymPy functions and symbols.
    
    Examples of valid input expressions:
    - sp.solve(sp.Eq(sp.symbols('x')**2 - 4, 0), sp.symbols('x'))
    - sp.diff(sp.sin(sp.symbols('x')), sp.symbols('x'))
    - sp.integrate(sp.exp(-sp.symbols('x')**2), (sp.symbols('x'), -sp.oo, sp.oo))
    - sp.simplify((sp.symbols('x')**2 + 2*sp.symbols('x') + 1)/(sp.symbols('x') + 1))
    - sp.Matrix([[1, 2], [3, 4]]).det()
    - sp.limit(sp.sin(sp.symbols('x')) / sp.symbols('x'), sp.symbols('x'), 0)
    
    The result is returned as a string representation.
    Use this tool whenever exact symbolic computation or verification is needed.
    """,
    locals={"sp": sp},
)

# List of available tools (can be extended later)
tools = [sympy_calculator]

# Optional: additional simple numerical tool if needed (sympy handles .evalf() for numerical)