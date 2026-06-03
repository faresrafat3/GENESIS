from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List


def generate_anomaly_candidate_report(task_results: List[dict]) -> Dict[str, Any]:
    task_count = len(task_results)
    tasks_with_candidates = 0
    by_source = defaultdict(lambda: {"count": 0})

    for run in task_results:
        candidates = run.get("anomaly_candidates", []) or []
        if candidates:
            tasks_with_candidates += 1
        for c in candidates:
            by_source[c.get("source_type", "unknown")]["count"] += 1

    return {
        "task_count": task_count,
        "tasks_with_candidates": tasks_with_candidates,
        "anomaly_candidate_task_rate": (tasks_with_candidates / task_count) if task_count else 0.0,
        "by_source": {k: dict(v) for k, v in by_source.items()},
    }
