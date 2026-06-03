from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .base import BaseObject, make_id


@dataclass(slots=True)
class ContradictionObject(BaseObject):
    contradiction_type: str = ""
    task_ref: str = ""
    elements_involved: List[str] = field(default_factory=list)
    summary: str = ""
    severity: Optional[float] = None
    status_label: str = "unresolved"

    @classmethod
    def create(
        cls,
        contradiction_type: str,
        task_ref: str,
        summary: str,
        *,
        elements_involved: list[str] | None = None,
        severity: float | None = None,
    ) -> "ContradictionObject":
        return cls(
            id=make_id("contradiction"),
            object_type="contradiction",
            contradiction_type=contradiction_type,
            task_ref=task_ref,
            summary=summary,
            elements_involved=elements_involved or [],
            severity=severity,
        )
