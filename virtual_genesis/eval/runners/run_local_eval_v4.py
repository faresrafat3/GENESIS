from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ...runtime.task_ingress.service import ingest_task
from .compare_conditions import compare_conditions
from ..reports.summary import summarize_comparison
from ..task_sets.prototype_v4_cases import PROTOTYPE_V4_CASES


DEFAULT_CONDITIONS = [
    "baseline_0",
    "baseline_1",
    "baseline_2_premium_always",
    "condition_a_concept_ready",
    "condition_b_economy",
    "condition_c_combined",
]


def build_classification_report(cases: List[object]) -> Dict[str, Any]:
    rows = []
    matches = 0
    top2_matches = 0
    ambiguity_count = 0
    family_counts: Dict[str, int] = {}
    predicted_counts: Dict[str, int] = {}
    for case in cases:
        task = ingest_task(case)
        env = (task.meta or {}).get("normalized_envelope", {})
        expected = env.get("expected_primary_family", "unknown")
        predicted = task.task_family
        ambiguity = bool((task.meta or {}).get("family_ambiguity", False))
        ranked = (task.meta or {}).get("ranked_frames", [])
        ok = expected == predicted
        top2 = expected in ranked[:2]
        matches += int(ok)
        top2_matches += int(top2)
        ambiguity_count += int(ambiguity)
        family_counts[expected] = family_counts.get(expected, 0) + 1
        predicted_counts[predicted] = predicted_counts.get(predicted, 0) + 1
        rows.append(
            {
                "text": task.raw_text,
                "expected_family": expected,
                "predicted_family": predicted,
                "top2_contains_expected": top2,
                "match": ok,
                "ambiguity": ambiguity,
                "family_scores": (task.meta or {}).get("family_scores", {}),
                "ranked_frames": ranked,
            }
        )
    return {
        "case_count": len(cases),
        "match_rate": matches / len(cases) if cases else 0.0,
        "top2_match_rate": top2_matches / len(cases) if cases else 0.0,
        "ambiguity_rate": ambiguity_count / len(cases) if cases else 0.0,
        "expected_family_counts": family_counts,
        "predicted_family_counts": predicted_counts,
        "rows": rows,
    }


def run_local_eval_v4(output_path: str = "virtual_genesis/eval/results/prototype_v4_summary.json") -> dict:
    classification_report = build_classification_report(PROTOTYPE_V4_CASES)
    results = compare_conditions(DEFAULT_CONDITIONS, PROTOTYPE_V4_CASES, task_set_ref="prototype_v4")
    summary = summarize_comparison(results)
    payload = {
        "task_count": len(PROTOTYPE_V4_CASES),
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
    payload = run_local_eval_v4()
    print(json.dumps(payload["classification_report"], indent=2, ensure_ascii=False))
    print(json.dumps(payload["summary"]["thesis_signals"], indent=2, ensure_ascii=False))
