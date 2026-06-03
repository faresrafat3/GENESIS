from __future__ import annotations

import json
from pathlib import Path

from .compare_conditions import compare_conditions
from ..reports.summary import summarize_comparison
from ..task_sets.prototype_v2 import PROTOTYPE_V2_TASKS


DEFAULT_CONDITIONS = [
    "baseline_0",
    "baseline_1",
    "baseline_2_premium_always",
    "condition_a_concept_ready",
    "condition_b_economy",
    "condition_c_combined",
]


def run_local_eval_v2(output_path: str = "virtual_genesis/eval/results/prototype_v2_summary.json") -> dict:
    results = compare_conditions(DEFAULT_CONDITIONS, PROTOTYPE_V2_TASKS, task_set_ref="prototype_v2")
    summary = summarize_comparison(results)
    payload = {
        "task_count": len(PROTOTYPE_V2_TASKS),
        "conditions": DEFAULT_CONDITIONS,
        "summary": summary,
        "raw_results": results,
    }
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


if __name__ == "__main__":
    payload = run_local_eval_v2()
    print(json.dumps(payload["summary"]["thesis_signals"], indent=2, ensure_ascii=False))
