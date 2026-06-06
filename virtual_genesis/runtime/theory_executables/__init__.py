"""
Theory Executables — GENESIS
==============================
Converts the four internal theories (T07/T08/T09/T10) from Markdown files
into executable Python objects with:
    - Formal axioms
    - Testable predictions
    - Falsification conditions
    - Scope constraints

This is the missing piece: theories were text files. Now they are code.

From the Ninja Excavation Report:
    "النظرية في LEAP = lemma في Lean (قابل للتحقق آلياً).
     النظرية في GENESIS = نص في ملف."

Not anymore.
"""

from .theories import (
    Theory07_PipelineMemoryVsInjection,
    Theory08_FeedbackValueMatrix,
    Theory09_AnticipatoryConcepts,
    Theory10_ReasoningSaturation,
    get_all_executable_theories,
    register_theories_with_falsification_engine,
)

__all__ = [
    "Theory07_PipelineMemoryVsInjection",
    "Theory08_FeedbackValueMatrix",
    "Theory09_AnticipatoryConcepts",
    "Theory10_ReasoningSaturation",
    "get_all_executable_theories",
    "register_theories_with_falsification_engine",
]
