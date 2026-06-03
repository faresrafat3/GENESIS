from __future__ import annotations

import json
from pathlib import Path

from .compare_conditions import compare_conditions
from ..reports.curriculum_analytics import generate_curriculum_analytics
from ..reports.governance_curriculum_analytics import generate_governance_curriculum_analytics
from ..reports.summary import summarize_comparison
from ..task_sets.prototype_v3c_curriculum import PROTOTYPE_V3C_CURRICULUM

DEFAULT_CONDITIONS = [
    "baseline_1",
    "baseline_2_premium_always",
    "condition_a_concept_ready",
    "condition_b_economy",
    "condition_c_combined",
]


def run_local_eval_v3c_curriculum(output_path: str = "virtual_genesis/eval/results/prototype_v3c_curriculum_summary.json") -> dict:
    results = compare_conditions(DEFAULT_CONDITIONS, PROTOTYPE_V3C_CURRICULUM, task_set_ref="prototype_v3c_curriculum")
    summary = summarize_comparison(results)
    curriculum_reports = {
        cid: generate_curriculum_analytics(payload['task_results'])
        for cid, payload in results.items()
    }
    governance_reports = {
        cid: generate_governance_curriculum_analytics(payload['task_results'])
        for cid, payload in results.items()
    }
    payload = {
        "task_count": len(PROTOTYPE_V3C_CURRICULUM),
        "conditions": DEFAULT_CONDITIONS,
        "summary": summary,
        "curriculum_reports": curriculum_reports,
        "governance_reports": governance_reports,
        "raw_results": results,
    }
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


if __name__ == "__main__":
    payload = run_local_eval_v3c_curriculum()
    print(json.dumps(payload['summary']['thesis_signals'], indent=2, ensure_ascii=False))
