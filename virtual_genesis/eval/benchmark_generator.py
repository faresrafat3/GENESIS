from __future__ import annotations

from typing import List

from ..core.objects.task_case import TaskCase


_SOURCE_TYPE_PROMPTS = {
    "property_gap": "Reproduce a scenario where required properties are not met despite task completion attempt, targeting {family} family: {summary}",
    "shortcut_pattern": "Reproduce a scenario where forbidden shortcuts are triggered in {family} family: {summary}",
    "contradiction_pattern": "Reproduce a scenario where contradictions emerge during processing in {family} family: {summary}",
}

_DEFAULT_PROMPT = "Reproduce anomaly scenario in {family} family: {summary}"


def generate_from_anomaly_candidates(anomalies: list[dict]) -> list:
    """Generate TaskCase objects from anomaly candidates.

    Each anomaly has: source_type, summary, severity, task_family.
    Map each to a diagnostic TaskCase targeting that anomaly pattern.
    Set diagnostic_purpose=["anomaly_derived", "self_benchmark"].
    """
    if not anomalies:
        return []

    cases: List[TaskCase] = []
    for anomaly in anomalies:
        source_type = anomaly.get("source_type", "unknown")
        summary = anomaly.get("summary", "")
        severity = anomaly.get("severity", 0.5) or 0.5
        task_family = anomaly.get("task_family", "unknown")

        template = _SOURCE_TYPE_PROMPTS.get(source_type, _DEFAULT_PROMPT)
        prompt_text = template.format(family=task_family, summary=summary)

        difficulty_class = "hard" if severity >= 0.7 else "medium"

        case = TaskCase.create(
            prompt_text=prompt_text,
            expected_primary_family=task_family,
        )
        case.diagnostic_purpose = ["anomaly_derived", "self_benchmark"]
        case.tags = [source_type, "auto_generated"]
        case.difficulty_class = difficulty_class
        case.stress_type = source_type

        cases.append(case)

    return cases
