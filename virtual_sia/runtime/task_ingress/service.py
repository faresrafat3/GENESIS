from __future__ import annotations

from typing import Dict, Optional

from ...core.objects.task import TaskObject
from .normalize import NormalizedTaskEnvelope, normalize_task_input


FAMILY_KEYWORDS = {
    "comparison": [
        "compare", "difference", "contrast", "vs", "better grounded", "which one", "which proposal", "which option",
        "decisive difference", "defensible", "stronger", "review the two", "judge which", "between the two",
        "choose the", "justify the choice", "more confidence", "deserves more confidence", "more credible",
        "safer proposal", "مقارنة", "فرق",
    ],
    "synthesis": [
        "synthesize", "merge", "combine", "summarize", "summary", "integrate", "incident update", "executive answer",
        "status explanation", "grounded answer", "coherent summary", "conclusion", "fragments", "findings",
        "observations", "supporting signals", "incident summary", "justifies", "produce a compact synthesis",
        "fact and inference", "blur fact and inference", "grounded summary", "write one concise", "لخص", "ادمج",
    ],
    "procedure": [
        "extract", "format", "reformat", "classify", "parse", "checklist", "fields", "attributes", "structured",
        "handoff", "layout", "operator", "labeled values", "field-oriented", "normalize", "نسق", "استخرج", "صنف",
    ],
    "analysis": [
        "root cause", "causal", "why did", "diagnose", "infer", "system failure", "contributing factor",
        "mechanism", "explain why", "analyze", "investigate", "underlying", "تحليل", "سبب",
    ],
    "extraction": [
        "extract structured", "pull out", "identify entities", "data points", "key information",
        "parse fields", "slot fill", "tabulate", "extract all", "structured output", "استخراج", "بيانات",
    ],
    "planning": [
        "plan", "steps to", "schedule", "sequence", "dependencies", "constraints", "milestones",
        "prioritize", "timeline", "roadmap", "multi-step", "تخطيط", "خطوات",
    ],
}


def ingest_task(raw_input: str | dict | object, optional_context: Optional[Dict] = None) -> TaskObject:
    envelope = normalize_task_input(raw_input)
    task = TaskObject.create(envelope.prompt_text)
    if optional_context:
        task.context_refs = list(optional_context.keys())
        task.meta = optional_context
    task.meta = task.meta or {}
    task.meta["normalized_envelope"] = {
        "raw_input_type": envelope.raw_input_type,
        "expected_primary_family": envelope.expected_primary_family,
        "expected_secondary_families": envelope.expected_secondary_families,
        "required_properties": envelope.required_properties,
        "forbidden_shortcuts": envelope.forbidden_shortcuts,
        "required_structure": envelope.required_structure,
        "diagnostic_purpose": envelope.diagnostic_purpose,
        "target_thesis": envelope.target_thesis,
        "meta": envelope.meta,
    }
    return estimate_task_properties(task, envelope)


def estimate_task_properties(task: TaskObject, envelope: NormalizedTaskEnvelope | None = None) -> TaskObject:
    text = task.normalized_text.lower()
    family, scores, ambiguity, ranked = classify_task_family(text)
    task.task_family = family
    task.difficulty_estimate = estimate_difficulty(text)
    task.criticality_level = estimate_criticality(text)
    task.failure_cost_class = "high" if task.criticality_level == "high" else "medium"
    task.success_criteria = default_success_criteria(task.task_family)
    task.meta = task.meta or {}
    task.meta["family_scores"] = scores
    task.meta["family_ambiguity"] = ambiguity
    task.meta["ranked_frames"] = ranked
    task.meta["primary_frame"] = ranked[0] if ranked else family
    task.meta["secondary_frames"] = ranked[1:3] if len(ranked) > 1 else []
    if envelope:
        task.meta["expected_primary_family"] = envelope.expected_primary_family
        task.meta["expected_secondary_families"] = envelope.expected_secondary_families
    task.touch()
    return task


def classify_task_family(text: str) -> tuple[str, dict[str, int], bool, list[str]]:
    scores: dict[str, int] = {}
    for family, keys in FAMILY_KEYWORDS.items():
        scores[family] = sum(1 for k in keys if k in text)

    ranked = [family for family, score in sorted(scores.items(), key=lambda item: item[1], reverse=True) if score > 0]
    if not ranked:
        return "unknown", scores, False, []

    best_family = ranked[0]
    best_score = scores[best_family]
    second_score = scores[ranked[1]] if len(ranked) > 1 else 0
    ambiguity = len(ranked) > 1 and second_score >= max(1, best_score - 1)
    return best_family, scores, ambiguity, ranked


def estimate_difficulty(text: str) -> str:
    if len(text) > 600:
        return "high"
    if len(text) > 180:
        return "medium"
    return "low"


def estimate_criticality(text: str) -> str:
    critical_words = ["critical", "production", "safety", "audit", "final release", "مهم", "خطر", "نهائي"]
    return "high" if any(w in text for w in critical_words) else "medium"


def default_success_criteria(task_family: str) -> list[str]:
    family_map = {
        "comparison": ["clear contrasts", "supported conclusion"],
        "synthesis": ["evidence coverage", "coherent merged answer"],
        "procedure": ["correct format", "rule compliance"],
        "analysis": ["causal chain identified", "root cause supported by evidence"],
        "extraction": ["all fields extracted", "structured output valid"],
        "planning": ["steps sequenced correctly", "constraints satisfied"],
        "unknown": ["reasonable answer", "format validity"],
    }
    return family_map.get(task_family, family_map["unknown"])
