from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .base import BaseObject, make_id
from .cost import CostProfile


@dataclass(slots=True)
class LedgerEntry(BaseObject):
    task_ref: str = ""
    phase: str = ""
    cognitive_action_type: str = ""
    tier_used: Optional[str] = None
    topology_used: Optional[str] = None
    estimated_immediate_gain: Optional[float] = None
    estimated_reuse_gain: Optional[float] = None
    estimated_learning_gain: Optional[float] = None
    estimated_cost: Optional[float] = None
    estimated_delay_penalty: Optional[float] = None
    estimated_noise_risk: Optional[float] = None
    actual_cost_profile: Optional[CostProfile] = None
    actual_immediate_effect: Optional[str] = None
    actual_reuse_effect: Optional[str] = None
    actual_learning_effect: Optional[str] = None
    would_repeat: Optional[bool] = None
    notes: Optional[str] = None

    @classmethod
    def create(cls, task_ref: str, phase: str, action_type: str) -> "LedgerEntry":
        return cls(
            id=make_id("ledger"),
            object_type="ledger_entry",
            task_ref=task_ref,
            phase=phase,
            cognitive_action_type=action_type,
        )
