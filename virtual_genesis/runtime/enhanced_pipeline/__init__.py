"""
Enhanced Pipeline — GENESIS
=============================
Pipeline that uses ALL new Ninja Excavator bridges:
    - Semantic Grounding (existing)
    - Ladder Ascent Engine
    - Semantic Verifier
    - Value Computation
    - Theory Executables

This replaces keyword-based verification with semantic verification,
adds economic decision-making with real numbers, and tracks
ladder-level phase transitions.
"""

from .enhanced_run import run_enhanced_pipeline

__all__ = ["run_enhanced_pipeline"]
