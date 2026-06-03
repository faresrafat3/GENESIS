from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List


def generate_family_breakdown(task_results: List[dict]) -> Dict[str, Any]:
    grouped: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "success": 0, "cost": 0.0})
    for run in task_results:
        family = run["task"]["task_family"]
        grouped[family]["count"] += 1
        grouped[family]["success"] += int(run["blackboard"]["verification_state"]["verification_summary"]["good_enough"])
        grouped[family]["cost"] += run.get("ledger", {}).get("actual_cost_profile", {}).get("estimated_cost_usd", 0.0) or 0.0

    report: Dict[str, Any] = {}
    for family, data in grouped.items():
        report[family] = {
            "task_count": data["count"],
            "success_rate": data["success"] / data["count"] if data["count"] else 0.0,
            "avg_estimated_cost": data["cost"] / data["count"] if data["count"] else 0.0,
        }
    return report
