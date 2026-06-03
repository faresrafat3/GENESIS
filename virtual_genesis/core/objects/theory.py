from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .base import BaseObject, make_id
from .scope import Scope


@dataclass(slots=True)
class LocalTheoryObject(BaseObject):
    name: str = ""
    core_question: str = ""
    scope: Scope = field(default_factory=Scope)
    concept_refs: List[str] = field(default_factory=list)
    contradiction_refs: List[str] = field(default_factory=list)
    anomaly_candidate_refs: List[str] = field(default_factory=list)
    mechanism_claims: List[str] = field(default_factory=list)
    predictive_claims: List[str] = field(default_factory=list)
    prescriptive_implications: List[str] = field(default_factory=list)
    confidence_score: Optional[float] = None
    predictive_value: float = 0.5
    prediction_count: int = 0
    correct_predictions: int = 0
    explanatory_power: float = 0.0

    @classmethod
    def create(cls, name: str, core_question: str) -> "LocalTheoryObject":
        return cls(
            id=make_id("theory"),
            object_type="local_theory",
            name=name,
            core_question=core_question,
        )
