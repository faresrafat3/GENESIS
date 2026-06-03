from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .base import BaseObject, make_id


@dataclass(slots=True)
class AgentIdentityObject(BaseObject):
    commitments: List[str] = field(default_factory=list)
    self_model: Dict[str, Any] = field(default_factory=dict)
    lineage: List[str] = field(default_factory=list)
    drift_score: float = 0.0
    accountability_log: List[Dict] = field(default_factory=list)
    policy_signature: List[str] = field(default_factory=list)

    @classmethod
    def create(cls, commitments: List[str], self_model: Dict[str, Any]) -> "AgentIdentityObject":
        return cls(
            id=make_id("identity"),
            object_type="agent_identity",
            commitments=commitments,
            self_model=self_model,
        )
