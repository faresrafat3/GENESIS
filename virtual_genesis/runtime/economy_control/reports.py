from __future__ import annotations

from typing import Any, Dict, List

from ...core.objects.ledger import LedgerEntry


def generate_economy_report(entries: List[LedgerEntry]) -> Dict[str, Any]:
    if not entries:
        return {
            "entry_count": 0,
            "premium_invocations": 0,
            "avg_estimated_cost": 0.0,
            "avg_actual_cost": 0.0,
        }

    premium_invocations = sum(1 for e in entries if e.tier_used == "tier_2")
    estimated_costs = [e.estimated_cost or 0.0 for e in entries]
    actual_costs = [
        (e.actual_cost_profile.estimated_cost_usd if e.actual_cost_profile else 0.0)
        for e in entries
    ]
    return {
        "entry_count": len(entries),
        "premium_invocations": premium_invocations,
        "avg_estimated_cost": sum(estimated_costs) / len(estimated_costs),
        "avg_actual_cost": sum(actual_costs) / len(actual_costs),
    }
