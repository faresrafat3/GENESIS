from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List


def generate_curriculum_analytics(task_results: List[dict]) -> Dict[str, Any]:
    by_level: Dict[str, Dict[str, float]] = defaultdict(lambda: {"count": 0, "success": 0, "cost": 0.0})
    by_perturbation: Dict[str, Dict[str, float]] = defaultdict(lambda: {"count": 0, "success": 0, "cost": 0.0})

    for run in task_results:
        task_meta = run.get("task", {}).get("meta", {}) or {}
        env = task_meta.get("normalized_envelope", {}) or {}
        meta = env.get("meta", {}) or {}
        tags = meta.get("tags", []) or []
        level = str(meta.get("curriculum_level", "base"))
        perturb = meta.get("perturbation_type", "base")
        success = bool(run["blackboard"]["verification_state"]["verification_summary"]["good_enough"])
        cost = run.get("ledger", {}).get("actual_cost_profile", {}).get("estimated_cost_usd", 0.0) or 0.0

        by_level[level]["count"] += 1
        by_level[level]["success"] += int(success)
        by_level[level]["cost"] += cost

        by_perturbation[perturb]["count"] += 1
        by_perturbation[perturb]["success"] += int(success)
        by_perturbation[perturb]["cost"] += cost

    def _finalize(src: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for key, v in src.items():
            out[key] = {
                "task_count": int(v["count"]),
                "success_rate": (v["success"] / v["count"]) if v["count"] else 0.0,
                "avg_estimated_cost": (v["cost"] / v["count"]) if v["count"] else 0.0,
            }
        return out

    return {
        "by_level": _finalize(by_level),
        "by_perturbation": _finalize(by_perturbation),
    }
