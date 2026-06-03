from __future__ import annotations

from typing import Any, Dict, List


def generate_concept_utility_report(task_results: List[dict]) -> Dict[str, Any]:
    total = len(task_results)
    concept_used = 0
    concept_used_and_success = 0

    for run in task_results:
        used_count = run.get("used_concepts_count", 0)
        success = bool(run["blackboard"]["verification_state"]["verification_summary"]["good_enough"])
        if used_count > 0:
            concept_used += 1
            if success:
                concept_used_and_success += 1

    return {
        "task_count": total,
        "concept_used_count": concept_used,
        "concept_activation_rate": (concept_used / total) if total else 0.0,
        "concept_success_rate_when_used": (concept_used_and_success / concept_used) if concept_used else 0.0,
    }
