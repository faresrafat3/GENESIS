from __future__ import annotations

from typing import Any, Dict


def summarize_comparison(results: Dict[str, dict]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {"conditions": {}, "thesis_signals": {}}

    for condition_id, payload in results.items():
        aggregate = payload.get("aggregate_metrics", {})
        meta = payload.get("meta", {})
        summary["conditions"][condition_id] = {
            "success_rate": aggregate.get("success_rate", 0.0),
            "avg_estimated_cost": aggregate.get("avg_estimated_cost", 0.0),
            "concept_count": aggregate.get("concept_count", 0),
            "concept_activation_rate": aggregate.get("concept_activation_rate", 0.0),
            "premium_run_count": aggregate.get("premium_run_count", 0),
            "warmup_summary": meta.get("warmup_summary"),
        }

    b1 = summary["conditions"].get("baseline_1", {})
    ca = summary["conditions"].get("condition_a_concept_ready", {})
    b2 = summary["conditions"].get("baseline_2_premium_always", {})
    cb = summary["conditions"].get("condition_b_economy", {})
    cc = summary["conditions"].get("condition_c_combined", {})

    summary["thesis_signals"]["thesis_1_concept_vs_retrieval"] = {
        "baseline_success": b1.get("success_rate", 0.0),
        "concept_success": ca.get("success_rate", 0.0),
        "same_cost_order": abs((b1.get("avg_estimated_cost", 0.0) - ca.get("avg_estimated_cost", 0.0))) < 1e-9,
        "concept_activation_rate": ca.get("concept_activation_rate", 0.0),
    }

    summary["thesis_signals"]["thesis_2_economy_vs_premium_always"] = {
        "premium_success": b2.get("success_rate", 0.0),
        "economy_success": cb.get("success_rate", 0.0),
        "premium_avg_cost": b2.get("avg_estimated_cost", 0.0),
        "economy_avg_cost": cb.get("avg_estimated_cost", 0.0),
    }

    summary["thesis_signals"]["combined_condition"] = {
        "combined_success": cc.get("success_rate", 0.0),
        "combined_avg_cost": cc.get("avg_estimated_cost", 0.0),
        "combined_concept_activation_rate": cc.get("concept_activation_rate", 0.0),
    }

    return summary
