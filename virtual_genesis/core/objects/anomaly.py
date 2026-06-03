from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .base import BaseObject, make_id


@dataclass(slots=True)
class AnomalyCandidate(BaseObject):
    task_family: str = ""
    source_type: str = ""
    summary: str = ""
    supporting_refs: List[str] = field(default_factory=list)
    severity: Optional[float] = None
    recommended_action: Optional[str] = None

    @classmethod
    def create(
        cls,
        task_family: str,
        source_type: str,
        summary: str,
        *,
        supporting_refs: list[str] | None = None,
        severity: float | None = None,
        recommended_action: str | None = None,
    ) -> "AnomalyCandidate":
        return cls(
            id=make_id("anomaly_candidate"),
            object_type="anomaly_candidate",
            task_family=task_family,
            source_type=source_type,
            summary=summary,
            supporting_refs=supporting_refs or [],
            severity=severity,
            recommended_action=recommended_action,
        )
