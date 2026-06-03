from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

from ...runtime.concept_engine.config import FAMILY_SELECTIVITY_STRATEGY


def generate_family_selectivity_detail(task_results: List[dict]) -> Dict[str, Any]:
    """Generate a per-family breakdown of concept activation decisions.

    Returns per-family stats: avg_activation_score, selection_rate,
    avg_contract_fit, avg_semantic_fit, strategy_used.
    """
    family_data: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "total_decisions": 0,
            "selected_count": 0,
            "total_activation_score": 0.0,
            "total_contract_fit": 0.0,
            "total_semantic_fit": 0.0,
        }
    )

    for run in task_results:
        pack_meta = run['blackboard']['retrieved_memory_pack'].get('meta', {}) or {}
        decisions = pack_meta.get('concept_activation_decisions', []) or []
        for d in decisions:
            family = d.get('family', 'unknown')
            family_data[family]["total_decisions"] += 1
            family_data[family]["total_activation_score"] += d.get('activation_score', 0)
            family_data[family]["total_contract_fit"] += d.get('contract_fit', 0)
            family_data[family]["total_semantic_fit"] += d.get('semantic_fit', 0)
            if d.get('selected'):
                family_data[family]["selected_count"] += 1

    report: Dict[str, Any] = {}
    for family, data in family_data.items():
        total = data["total_decisions"]
        selected = data["selected_count"]
        report[family] = {
            "total_decisions": total,
            "avg_activation_score": (data["total_activation_score"] / total) if total else 0.0,
            "selection_rate": (selected / total) if total else 0.0,
            "avg_contract_fit": (data["total_contract_fit"] / total) if total else 0.0,
            "avg_semantic_fit": (data["total_semantic_fit"] / total) if total else 0.0,
            "strategy_used": FAMILY_SELECTIVITY_STRATEGY.get(family, 'unknown'),
        }

    return report
