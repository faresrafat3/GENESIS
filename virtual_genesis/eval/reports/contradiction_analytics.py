from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List


def generate_contradiction_analytics(task_results: List[dict]) -> Dict[str, Any]:
    total = len(task_results)
    tasks_with_contradictions = 0
    by_type = defaultdict(lambda: {"count": 0})

    for run in task_results:
        contradictions = run.get("blackboard", {}).get("contradictions", []) or []
        if contradictions:
            tasks_with_contradictions += 1
        for c in contradictions:
            ctype = c.get("contradiction_type", "unknown")
            by_type[ctype]["count"] += 1

    return {
        "task_count": total,
        "tasks_with_contradictions": tasks_with_contradictions,
        "contradiction_task_rate": (tasks_with_contradictions / total) if total else 0.0,
        "by_type": {k: dict(v) for k, v in by_type.items()},
    }
