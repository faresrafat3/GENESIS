from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .base import BaseObject, make_id
from .provenance import Provenance


@dataclass(slots=True)
class TaskCase(BaseObject):
    prompt_text: str = ""
    visible_context: List[str] = field(default_factory=list)
    attachments_refs: List[str] = field(default_factory=list)

    expected_primary_family: str = "unknown"
    expected_secondary_families: List[str] = field(default_factory=list)
    family_overlap_type: Optional[str] = None
    difficulty_class: str = "medium"
    criticality_class: str = "medium"

    required_properties: List[str] = field(default_factory=list)
    forbidden_shortcuts: List[str] = field(default_factory=list)
    required_structure: List[str] = field(default_factory=list)
    evaluation_notes: Optional[str] = None

    diagnostic_purpose: List[str] = field(default_factory=list)
    target_thesis: List[str] = field(default_factory=list)
    stress_type: Optional[str] = None
    known_risks: List[str] = field(default_factory=list)
    authoring_notes: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    provenance: Provenance | None = None

    @classmethod
    def create(cls, prompt_text: str, expected_primary_family: str) -> "TaskCase":
        return cls(
            id=make_id("task_case"),
            object_type="task_case",
            prompt_text=prompt_text,
            expected_primary_family=expected_primary_family,
            provenance=Provenance(source_kind="task_case_authoring"),
        )
