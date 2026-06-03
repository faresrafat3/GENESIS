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


def _apply_family_policy(overrides: Dict[str, Dict[str, int]]) -> None:
    concept_config.DEFAULT_FAMILY_SELECTIVITY.clear()
    concept_config.DEFAULT_FAMILY_SELECTIVITY.update(
        {
            "comparison": {"max_active": 1, "min_score": 7},
            "synthesis": {"max_active": 1, "min_score": 7},
            "procedure": {"max_active": 0, "min_score": 99},
        }
    )
    for family, cfg in overrides.items():
        concept_config.DEFAULT_FAMILY_SELECTIVITY[family] = cfg


def run_family_selectivity_ablation(
    output_path: str = "virtual_genesis/eval/results/family_selectivity_ablation_summary.json",
) -> dict:
    settings = [
        {
            "name": "current_default",
            "overrides": {},
            "notes": "comparison top1/7, synthesis top1/7, procedure top0",
        },
        {
            "name": "synthesis_top2",
            "overrides": {"synthesis": {"max_active": 2, "min_score": 7}},
            "notes": "allow a second concept for synthesis only",
        },
        {
            "name": "procedure_top1",
            "overrides": {"procedure": {"max_active": 1, "min_score": 7}},
            "notes": "allow concepts for procedure tasks",
        },
        {
            "name": "synthesis_top2_procedure_top1",
            "overrides": {
                "synthesis": {"max_active": 2, "min_score": 7},
                "procedure": {"max_active": 1, "min_score": 7},
            },
            "notes": "more permissive policy for synthesis and procedure",
        },
    ]

    all_results: Dict[str, Any] = {}
    for setting in settings:
        _apply_family_policy(setting["overrides"])
        raw = compare_conditions(DEFAULT_CONDITIONS, PROTOTYPE_V3B_CURRICULUM, task_set_ref=f"family_selectivity::{setting['name']}")
        all_results[setting["name"]] = {
            "config": setting,
            "summary": summarize_comparison(raw),
            "raw_results": raw,
        }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8")
    return all_results


if __name__ == "__main__":
    payload = run_family_selectivity_ablation()
    compact = {k: v['summary']['thesis_signals'] for k, v in payload.items()}
    print(json.dumps(compact, indent=2, ensure_ascii=False))
