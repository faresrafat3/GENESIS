from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ...core.objects.task_case import TaskCase


@dataclass(slots=True)
class NormalizedTaskEnvelope:
    prompt_text: str
    raw_input_type: str
    expected_primary_family: str = "unknown"
    expected_secondary_families: List[str] = field(default_factory=list)
    required_properties: List[str] = field(default_factory=list)
    forbidden_shortcuts: List[str] = field(default_factory=list)
    required_structure: List[str] = field(default_factory=list)
    diagnostic_purpose: List[str] = field(default_factory=list)
    target_thesis: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)


def normalize_task_input(task_input: str | Dict[str, Any] | TaskCase) -> NormalizedTaskEnvelope:
    if isinstance(task_input, TaskCase):
        inherited_meta = dict(task_input.meta or {})
        inherited_meta.update(
            {
                "source_case_id": inherited_meta.get("source_case_id", task_input.id),
                "tags": task_input.tags,
                "family_overlap_type": task_input.family_overlap_type,
                "difficulty_class": task_input.difficulty_class,
                "criticality_class": task_input.criticality_class,
            }
        )
        return NormalizedTaskEnvelope(
            prompt_text=task_input.prompt_text,
            raw_input_type="task_case_object",
            expected_primary_family=task_input.expected_primary_family,
            expected_secondary_families=task_input.expected_secondary_families,
            required_properties=task_input.required_properties,
            forbidden_shortcuts=task_input.forbidden_shortcuts,
            required_structure=task_input.required_structure,
            diagnostic_purpose=task_input.diagnostic_purpose,
            target_thesis=task_input.target_thesis,
            meta=inherited_meta,
        )
    if isinstance(task_input, dict):
        inherited_meta = dict(task_input.get("meta", {}) or {})
        inherited_meta.update(
            {
                "source_case_id": task_input.get("case_id") or task_input.get("id"),
                "tags": task_input.get("tags", []),
                "family_overlap_type": task_input.get("family_overlap_type"),
                "difficulty_class": task_input.get("difficulty_class", "medium"),
                "criticality_class": task_input.get("criticality_class", "medium"),
            }
        )
        return NormalizedTaskEnvelope(
            prompt_text=task_input["prompt_text"],
            raw_input_type="task_case_dict",
            expected_primary_family=task_input.get("expected_primary_family", "unknown"),
            expected_secondary_families=task_input.get("expected_secondary_families", []),
            required_properties=task_input.get("required_properties", []),
            forbidden_shortcuts=task_input.get("forbidden_shortcuts", []),
            required_structure=task_input.get("required_structure", []),
            diagnostic_purpose=task_input.get("diagnostic_purpose", []),
            target_thesis=task_input.get("target_thesis", []),
            meta=inherited_meta,
        )
    return NormalizedTaskEnvelope(prompt_text=task_input, raw_input_type="raw_string")
