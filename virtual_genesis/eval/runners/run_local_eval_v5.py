from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ...runtime.task_ingress.service import ingest_task
from .compare_conditions import compare_conditions
from ..reports.summary import summarize_comparison
from ..task_sets.prototype_v5_cases import PROTOTYPE_V5_CASES

DEFAULT_CONDITIONS = [
    "baseline_0",
    "baseline_1",
    "baseline_2_premium_always",
    "condition_a_concept_ready",
    "condition_b_economy",
    "condition_c_combined",
]


def build_case_report(cases: List[object]) -> Dict[str, Any]:
    rows = []
    matches = 0
    top2_matches = 0
    ambiguity_count = 0
    for case in cases:
        task = ingest_task(case)
        env = (task.meta or {}).get("normalized_envelope", {})
        expected = env.get("expected_primary_family", "unknown")
        predicted = task.task_family
        ranked = (task.meta or {}).get("ranked_frames", [])
        ambiguity = bool((task.meta or {}).get("family_ambiguity", False))
        ok = expected == predicted
        top2 = expected in ranked[:2]
        matches += int(ok)
        top2_matches += int(top2)
        ambiguity_count += int(ambiguity)
        rows.append({
            "text": task.raw_text,
            "expected_family": expected,
            "predicted_family": predicted,
            "ranked_frames": ranked,
            "match": ok,
            "top2_contains_expected": top2,
            "ambiguity": ambiguity,
        })
    return {
        "case_count": len(cases),
        "match_rate": matches / len(cases) if cases else 0.0,
        "top2_match_rate": top2_matches / len(cases) if cases else 0.0,
        "ambiguity_rate": ambiguity_count / len(cases) if cases else 0.0,
        "rows": rows,
    }


def run_local_eval_v5(output_path: str = "virtual_genesis/eval/results/prototype_v5_summary.json") -> dict:
    classification_report = build_case_report(PROTOTYPE_V5_CASES)
    results = compare_conditions(DEFAULT_CONDITIONS, PROTOTYPE_V5_CASES, task_set_ref="prototype_v5")
    summary = summarize_comparison(results)
    payload = {
        "task_count": len(PROTOTYPE_V5_CASES),
        "conditions": DEFAULT_CONDITIONS,
        "classification_report": classification_report,
        "summary": summary,
        "raw_results": results,
    }
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


if __name__ == "__main__":
    payload = run_local_eval_v5()
    print(json.dumps(payload['summary']['thesis_signals'], indent=2, ensure_ascii=False))
