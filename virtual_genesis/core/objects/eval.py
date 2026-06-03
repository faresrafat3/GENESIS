from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .base import BaseObject, make_id


@dataclass(slots=True)
class EvaluationResult(BaseObject):
    run_id: str = ""
    condition_id: str = ""
    task_set_ref: str = ""
    task_results: List[Dict] = field(default_factory=list)
    aggregate_metrics: Dict[str, float] = field(default_factory=dict)
    notes: Optional[str] = None

    @classmethod
    def create(cls, condition_id: str, task_set_ref: str) -> "EvaluationResult":
        return cls(
            id=make_id("eval"),
            object_type="evaluation_result",
            run_id=make_id("run"),
            condition_id=condition_id,
            task_set_ref=task_set_ref,
        )
