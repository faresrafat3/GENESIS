from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .base import BaseObject, make_id


@dataclass(slots=True)
class DecisionObject(BaseObject):
    decision_type: str = ""
    task_ref: str = ""
    blackboard_snapshot_ref: str = ""
    selected_option: str = ""
    used_argument_refs: List[str] = field(default_factory=list)
    used_policy_refs: List[str] = field(default_factory=list)
    expected_value: Optional[float] = None
    actual_outcome_summary: Optional[str] = None

    @classmethod
    def create(
        cls,
        decision_type: str,
        task_ref: str,
        blackboard_snapshot_ref: str,
        selected_option: str,
    ) -> "DecisionObject":
        return cls(
            id=make_id("decision"),
            object_type="decision",
            decision_type=decision_type,
            task_ref=task_ref,
            blackboard_snapshot_ref=blackboard_snapshot_ref,
            selected_option=selected_option,
        )


@dataclass(slots=True)
class TierDecisionObject(BaseObject):
    task_ref: str = ""
    chosen_tier: str = "tier_1"
    decision_reason: str = ""
    trigger_refs: List[str] = field(default_factory=list)
    expected_immediate_gain: Optional[float] = None
    expected_reuse_gain: Optional[float] = None
    expected_cost: Optional[float] = None
    expected_delay_penalty: Optional[float] = None
    confidence_in_decision: Optional[float] = None
    fallback_option: Optional[str] = None

    @classmethod
    def create(cls, task_ref: str, chosen_tier: str, reason: str) -> "TierDecisionObject":
        return cls(
            id=make_id("tier_decision"),
            object_type="tier_decision",
            task_ref=task_ref,
            chosen_tier=chosen_tier,
            decision_reason=reason,
        )
