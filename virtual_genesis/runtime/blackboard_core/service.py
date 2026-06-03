from __future__ import annotations

from typing import Any

from ...core.objects.blackboard import (
    BlackboardContextSnapshot,
    BlackboardObject,
    BlackboardSnapshot,
    BlackboardTaskCore,
)
from ...core.objects.task import TaskObject


def create_blackboard(task: TaskObject) -> BlackboardObject:
    core = BlackboardTaskCore(
        task_id=task.id,
        task_family=task.task_family,
        criticality_level=task.criticality_level,
        difficulty_estimate=task.difficulty_estimate,
        success_criteria=task.success_criteria,
    )
    return BlackboardObject.create(task_ref=task.id, task_core=core)


def update_blackboard(blackboard: BlackboardObject, section_name: str, payload: Any) -> BlackboardObject:
    if not hasattr(blackboard, section_name):
        raise ValueError(f"Unknown blackboard section: {section_name}")
    setattr(blackboard, section_name, payload)
    blackboard.touch()
    return blackboard


def attach_context(blackboard: BlackboardObject, user_context_summary: str = "", tool_availability: list[str] | None = None, constraints: list[str] | None = None) -> BlackboardObject:
    blackboard.context_snapshot = BlackboardContextSnapshot(
        user_context_summary=user_context_summary,
        tool_availability=tool_availability or [],
        constraints=constraints or [],
    )
    blackboard.state = "contextualized"
    blackboard.touch()
    return blackboard


def snapshot_blackboard(blackboard: BlackboardObject, phase: str, reason: str) -> BlackboardSnapshot:
    snap = blackboard.snapshot(phase=phase, reason=reason)
    blackboard.touch()
    return snap


def close_blackboard(blackboard: BlackboardObject, outcome_summary: dict[str, Any]) -> BlackboardObject:
    blackboard.outcome_learning_hooks = outcome_summary
    blackboard.state = "closed"
    blackboard.touch()
    return blackboard
