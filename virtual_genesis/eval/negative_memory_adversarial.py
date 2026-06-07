"""Adversarial test generation from Negative Memory (Theory-13).

This bridges the gap between T-13 (Negative Memory) and H8 (Self-Benchmarking).
Every failure stored in Negative Memory becomes an adversarial test case
for the next self-benchmarking cycle. This is *generative* negative memory —
not just archiving failures, but weaponizing them as tests.

The key insight from Fares:
    "كل مرة يرتكب فيها النظام خطأ، يجب أن يُضاف ليس كـ 'تذكرة'
    بل كـ اختبار خصم جديد (Adversarial Test) لـ Self-Benchmarking."

Reference: GENESIS/PAPER/analysis/SELF_BENCHMARKING_AS_REGIME_DETECTOR.md
Theory:    T-13 Negative Memory + H8 Self-Benchmarking
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core.objects.task_case import TaskCase


# ── Negative Memory Record ────────────────────────────────────────────────


@dataclass
class NegativeMemoryRecord:
    """A single failure record from Negative Memory."""
    id: str
    task_family: str
    failure_type: str       # "wrong_answer", "shortcut", "contradiction", "missed_edge_case"
    context_summary: str    # brief description of what went wrong
    expected_behavior: str  # what should have happened
    actual_behavior: str    # what actually happened
    severity: float = 0.7  # 0-1, default high since it's a failure
    recurrence_count: int = 1  # how many times this pattern has been seen
    metadata: Dict[str, Any] = field(default_factory=dict)


# ── Prompt Templates for Adversarial Tests ────────────────────────────────

_FAILURE_TYPE_TEMPLATES = {
    "wrong_answer": (
        "ADVERSARIAL: The system previously answered incorrectly on a {family} task. "
        "Create a variant that tests: {expected}. "
        "Context of failure: {context}"
    ),
    "shortcut": (
        "ADVERSARIAL: The system exploited a shortcut in {family} tasks. "
        "Create a test that blocks this shortcut: {context}. "
        "Expected genuine reasoning: {expected}"
    ),
    "contradiction": (
        "ADVERSARIAL: The system produced contradictory outputs in {family}. "
        "Create a test that exposes this contradiction: {context}. "
        "Expected consistent behavior: {expected}"
    ),
    "missed_edge_case": (
        "ADVERSARIAL: The system missed an edge case in {family}. "
        "Edge case details: {context}. "
        "Expected handling: {expected}"
    ),
}

_DEFAULT_TEMPLATE = (
    "ADVERSARIAL from Negative Memory: {family} failure — {context}. "
    "Expected: {expected}"
)


# ── Main Generator ────────────────────────────────────────────────────────


def generate_from_negative_memory(
    failures: List[Dict[str, Any]],
    *,
    max_recurrence_boost: float = 0.3,
    min_severity: float = 0.3,
) -> List[TaskCase]:
    """Convert Negative Memory failure records into adversarial TaskCase objects.

    Each failure becomes a targeted test case designed to verify the system
    no longer makes the same mistake. Failures that recur more frequently
    get higher difficulty_class and severity.

    Args:
        failures: list of failure dicts with keys:
            - id: unique identifier
            - task_family: e.g., "comparison", "synthesis"
            - failure_type: "wrong_answer", "shortcut", etc.
            - context_summary: what went wrong
            - expected_behavior: what should happen
            - actual_behavior: what happened
            - severity: 0-1 (optional, default 0.7)
            - recurrence_count: how many times seen (optional, default 1)
        max_recurrence_boost: max severity boost for recurring failures.
        min_severity: minimum severity to generate a test from.

    Returns:
        List of TaskCase objects with adversarial test specifications.
    """
    if not failures:
        return []

    cases: List[TaskCase] = []

    for failure in failures:
        severity = failure.get("severity", 0.7) or 0.7
        if severity < min_severity:
            continue

        failure_type = failure.get("failure_type", "unknown")
        task_family = failure.get("task_family", "unknown")
        context = failure.get("context_summary", "")
        expected = failure.get("expected_behavior", "")
        recurrence = failure.get("recurrence_count", 1) or 1

        # Boost severity for recurring failures
        boosted_severity = min(1.0, severity + max_recurrence_boost * (recurrence - 1))

        # Build prompt from template
        template = _FAILURE_TYPE_TEMPLATES.get(failure_type, _DEFAULT_TEMPLATE)
        prompt_text = template.format(
            family=task_family,
            context=context,
            expected=expected,
        )

        # Determine difficulty
        if boosted_severity >= 0.8 or recurrence >= 3:
            difficulty_class = "hard"
        elif boosted_severity >= 0.5:
            difficulty_class = "medium"
        else:
            difficulty_class = "easy"

        case = TaskCase.create(
            prompt_text=prompt_text,
            expected_primary_family=task_family,
        )
        case.diagnostic_purpose = ["negative_memory_adversarial", "self_benchmark"]
        case.tags = [
            failure_type,
            "adversarial",
            f"recurrence_{recurrence}",
            "negative_memory",
        ]
        case.difficulty_class = difficulty_class
        case.stress_type = f"adversarial_{failure_type}"

        # Store failure metadata for traceability in the built-in meta dict
        case.meta = case.meta or {}
        case.meta["adversarial_source"] = {
            "failure_id": failure.get("id", "unknown"),
            "failure_type": failure_type,
            "original_severity": severity,
            "boosted_severity": round(boosted_severity, 3),
            "recurrence_count": recurrence,
            "actual_behavior": failure.get("actual_behavior", ""),
        }

        cases.append(case)

    return cases


def merge_negative_memory_with_anomalies(
    negative_memory_cases: List[TaskCase],
    anomaly_cases: List[TaskCase],
    *,
    deduplicate_by_family: bool = True,
) -> List[TaskCase]:
    """Merge adversarial tests from Negative Memory with anomaly-derived tests.

    Deduplication: if both sources produce a test for the same (family, stress_type),
    keep the one with higher diagnostic potential (negative memory cases get priority
    since they target known failures).

    Args:
        negative_memory_cases: output of generate_from_negative_memory().
        anomaly_cases: output of generate_from_anomaly_candidates().
        deduplicate_by_family: whether to deduplicate by (family, stress_type).

    Returns:
        Merged, deduplicated list of TaskCase objects.
    """
    if not deduplicate_by_family:
        return negative_memory_cases + anomaly_cases

    seen: Dict[tuple, TaskCase] = {}

    # Add anomaly cases first (lower priority)
    for case in anomaly_cases:
        key = (case.expected_primary_family, case.stress_type)
        if key not in seen:
            seen[key] = case

    # Add negative memory cases (higher priority — overwrites anomalies)
    for case in negative_memory_cases:
        key = (case.expected_primary_family, case.stress_type)
        seen[key] = case  # always overwrites

    return list(seen.values())
