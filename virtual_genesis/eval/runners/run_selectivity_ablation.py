from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from ...runtime.concept_engine import config as concept_config
from .compare_conditions import compare_conditions
from ..reports.summary import summarize_comparison
from ..task_sets.prototype_v3b_curriculum import PROTOTYPE_V3B_CURRICULUM


DEFAULT_CONDITIONS = [
    "baseline_1",
    "baseline_2_premium_always",
    "condition_a_concept_ready",
    "condition_b_economy",
    "condition_c_combined",
]


def _set_selectivity(max_active: int, min_score: int):
    concept_config.DEFAULT_GLOBAL_MAX_ACTIVE_CONCEPTS = max_active
    concept_config.DEFAULT_MIN_ACTIVATION_SCORE = min_score


def run_selectivity_ablation(output_path: str = "virtual_genesis/eval/results/selectivity_ablation_summary.json") -> dict:
    settings = [
        {"name": "top1_score6", "max_active": 1, "min_score": 6},
        {"name": "top2_score6", "max_active": 2, "min_score": 6},
        {"name": "top1_score7", "max_active": 1, "min_score": 7},
        {"name": "top2_score7", "max_active": 2, "min_score": 7},
    ]

    all_results: Dict[str, Any] = {}
    for cfg in settings:
        _set_selectivity(cfg["max_active"], cfg["min_score"])
        results = compare_conditions(DEFAULT_CONDITIONS, PROTOTYPE_V3B_CURRICULUM, task_set_ref=f"selectivity::{cfg['name']}")
        all_results[cfg["name"]] = {
            "config": cfg,
            "summary": summarize_comparison(results),
            "raw_results": results,
        }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8")
    return all_results


if __name__ == "__main__":
    payload = run_selectivity_ablation()
    compact = {k: v['summary']['thesis_signals'] for k, v in payload.items()}
    print(json.dumps(compact, indent=2, ensure_ascii=False))
