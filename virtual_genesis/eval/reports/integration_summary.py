from __future__ import annotations

from typing import Any, Dict, List


def generate_integration_summary_report(
    all_flags_results: List[dict],
    concept_only_results: List[dict],
    combined_results: List[dict],
) -> Dict[str, Any]:
    """Generate a summary report comparing all-flags, concept-only, and combined conditions.

    Returns dict with governance_overhead, cumulative_benefit, interaction_effects,
    and per_condition_metrics.
    """
    def _metrics(results: List[dict]) -> Dict[str, float]:
        if not results:
            return {"success_rate": 0.0, "total_cost": 0.0, "avg_cost": 0.0}
        successes = sum(
            1 for r in results
            if r.get("blackboard", {}).get("verification_state", {}).get("verification_summary", {}).get("good_enough", False)
        )
        total_cost = sum(
            r.get("ledger", {}).get("actual_cost_profile", {}).get("estimated_cost_usd", 0.0) or 0.0
            for r in results
        )
        count = len(results)
        return {
            "success_rate": successes / count if count else 0.0,
            "total_cost": total_cost,
            "avg_cost": total_cost / count if count else 0.0,
        }

    all_flags_metrics = _metrics(all_flags_results)
    concept_only_metrics = _metrics(concept_only_results)
    combined_metrics = _metrics(combined_results)

    # governance_overhead: extra cost from all-flags vs combined baseline
    governance_overhead = all_flags_metrics["avg_cost"] - combined_metrics["avg_cost"]

    # cumulative_benefit: success_rate improvement of all-flags over concept-only
    cumulative_benefit = all_flags_metrics["success_rate"] - concept_only_metrics["success_rate"]

    # interaction_effects: synergy measure
    # Positive means mechanisms help each other (all-flags benefit > sum of individual deltas)
    individual_improvement = combined_metrics["success_rate"] - concept_only_metrics["success_rate"]
    all_flags_improvement = all_flags_metrics["success_rate"] - concept_only_metrics["success_rate"]
    synergy = all_flags_improvement - individual_improvement

    return {
        "governance_overhead": governance_overhead,
        "cumulative_benefit": cumulative_benefit,
        "interaction_effects": synergy,
        "per_condition_metrics": {
            "all_flags_enabled": {
                "success_rate": all_flags_metrics["success_rate"],
                "avg_cost": all_flags_metrics["avg_cost"],
                "total_cost": all_flags_metrics["total_cost"],
            },
            "concept_only": {
                "success_rate": concept_only_metrics["success_rate"],
                "avg_cost": concept_only_metrics["avg_cost"],
                "total_cost": concept_only_metrics["total_cost"],
            },
            "combined_baseline": {
                "success_rate": combined_metrics["success_rate"],
                "avg_cost": combined_metrics["avg_cost"],
                "total_cost": combined_metrics["total_cost"],
            },
        },
    }
