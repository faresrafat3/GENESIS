from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..ontology.enums import BlackboardState
from .base import BaseObject, make_id, utc_now


@dataclass(slots=True)
class BlackboardTaskCore:
    task_id: str
    task_family: str
    criticality_level: str
    difficulty_estimate: str
    success_criteria: List[str] = field(default_factory=list)


@dataclass(slots=True)
class BlackboardContextSnapshot:
    user_context_summary: str = ""
    relevant_history_refs: List[str] = field(default_factory=list)
    tool_availability: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)


@dataclass(slots=True)
class BlackboardMemoryPack:
    episodic_refs: List[str] = field(default_factory=list)
    semantic_refs: List[str] = field(default_factory=list)
    procedural_refs: List[str] = field(default_factory=list)
    negative_refs: List[str] = field(default_factory=list)
    concept_refs: List[str] = field(default_factory=list)
    concept_hints: List[str] = field(default_factory=list)
    theory_refs: List[str] = field(default_factory=list)
    theory_hints: List[str] = field(default_factory=list)
    retrieval_rationale: str = ""
    memory_noise_risk: Optional[float] = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BlackboardSituationModel:
    knowns: List[str] = field(default_factory=list)
    unknowns: List[str] = field(default_factory=list)
    uncertainties: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    missing_information: List[str] = field(default_factory=list)
    candidate_frames: List[str] = field(default_factory=list)


@dataclass(slots=True)
class BlackboardSnapshot:
    snapshot_id: str
    blackboard_ref: str
    phase: str
    snapshot_time: datetime
    reason: str
    state_copy: Dict[str, Any]


@dataclass(slots=True)
class BlackboardObject(BaseObject):
    task_ref: str = ""
    state: str = BlackboardState.INITIALIZED.value
    task_core: Optional[BlackboardTaskCore] = None
    context_snapshot: BlackboardContextSnapshot = field(default_factory=BlackboardContextSnapshot)
    retrieved_memory_pack: BlackboardMemoryPack = field(default_factory=BlackboardMemoryPack)
    situation_model: BlackboardSituationModel = field(default_factory=BlackboardSituationModel)
    candidate_claims: List[Dict[str, Any]] = field(default_factory=list)
    verification_state: Dict[str, Any] = field(default_factory=dict)
    contradictions: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    outcome_learning_hooks: Dict[str, Any] = field(default_factory=dict)
    snapshot_refs: List[str] = field(default_factory=list)

    @classmethod
    def create(cls, task_ref: str, task_core: BlackboardTaskCore) -> "BlackboardObject":
        return cls(
            id=make_id("blackboard"),
            object_type="blackboard",
            task_ref=task_ref,
            task_core=task_core,
        )

    def snapshot(self, phase: str, reason: str) -> BlackboardSnapshot:
        snap = BlackboardSnapshot(
            snapshot_id=make_id("bbsnap"),
            blackboard_ref=self.id,
            phase=phase,
            snapshot_time=utc_now(),
            reason=reason,
            state_copy=self.to_dict(),
        )
        self.snapshot_refs.append(snap.snapshot_id)
        return snap
