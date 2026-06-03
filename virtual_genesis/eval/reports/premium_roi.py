from __future__ import annotations

from typing import Any, Dict, List


def generate_premium_roi_report(task_results: List[dict]) -> Dict[str, Any]:
    premium_runs = []
    premium_success = 0
    total_premium_cost = 0.0

    for run in task_results:
        tier = run.get("ledger", {}).get("tier_used")
        if tier == "tier_2":
            premium_runs.append(run)
            if run["blackboard"]["verification_state"]["verification_summary"]["good_enough"]:
                premium_success += 1
            total_premium_cost += run.get("ledger", {}).get("actual_cost_profile", {}).get("estimated_cost_usd", 0.0) or 0.0

    return {
        "premium_run_count": len(premium_runs),
        "premium_success_rate": (premium_success / len(premium_runs)) if premium_runs else 0.0,
        "total_premium_cost": total_premium_cost,
        "avg_premium_cost": (total_premium_cost / len(premium_runs)) if premium_runs else 0.0,
    }
