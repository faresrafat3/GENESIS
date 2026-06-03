from __future__ import annotations

from typing import Any, Dict, List


def generate_theory_usage_report(task_results: List[dict]) -> Dict[str, Any]:
    total = len(task_results)
    tasks_with_theory = 0
    total_theories = 0

    for run in task_results:
        count = run.get("used_theories_count", 0) or 0
        if count > 0:
            tasks_with_theory += 1
            total_theories += count

    return {
        "task_count": total,
        "tasks_with_theory_hints": tasks_with_theory,
        "theory_hint_task_rate": (tasks_with_theory / total) if total else 0.0,
        "avg_theories_per_task": (total_theories / total) if total else 0.0,
    }
