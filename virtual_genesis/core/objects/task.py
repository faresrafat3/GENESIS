from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .base import BaseObject, make_id


@dataclass(slots=True)
class TaskObject(BaseObject):
    raw_text: str = ""
    normalized_text: str = ""
    task_family: str = "unknown"
    subtask_family: Optional[str] = None
    criticality_level: str = "medium"
    difficulty_estimate: str = "unknown"
    deadline_class: Optional[str] = None
    success_criteria: List[str] = field(default_factory=list)
    failure_cost_class: str = "medium"
    input_artifacts: List[str] = field(default_factory=list)
    context_refs: List[str] = field(default_factory=list)

    @classmethod
    def create(cls, raw_text: str) -> "TaskObject":
        return cls(
            id=make_id("task"),
            object_type="task",
            raw_text=raw_text,
            normalized_text=raw_text.strip(),
        )
