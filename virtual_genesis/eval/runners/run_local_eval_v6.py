from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ...runtime.task_ingress.service import ingest_task
from .compare_conditions import compare_conditions
from ..reports.summary import summarize_comparison
from ..reports.perturbation_resistance import generate_perturbation_resistance_report
from ..task_sets.prototype_v6_cases import PROTOTYPE_V6_CASES, build_v6_curriculum

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


def run_local_eval_v6(output_path: str = "virtual_genesis/eval/results/prototype_v6_summary.json") -> dict:
    """Run v6 evaluation: base cases + curriculum variants across all conditions.

    Returns the combined payload with classification reports, condition comparisons,
    and perturbation resistance analysis.
    """
    # Build curriculum from v6 cases (6 levels)
    curriculum_cases = build_v6_curriculum()

    # Classification report on base v6 cases
    classification_report = build_case_report(PROTOTYPE_V6_CASES)

    # Run conditions against base v6 cases
    results_base = compare_conditions(DEFAULT_CONDITIONS, PROTOTYPE_V6_CASES, task_set_ref="prototype_v6")

    # Run conditions against curriculum-perturbed cases
    results_curriculum = compare_conditions(DEFAULT_CONDITIONS, curriculum_cases, task_set_ref="prototype_v6_curriculum")

    summary_base = summarize_comparison(results_base)
    summary_curriculum = summarize_comparison(results_curriculum)

    # Generate perturbation resistance report from combined condition
    combined_curriculum_results = results_curriculum.get("condition_c_combined", {})
    task_results = combined_curriculum_results.get("task_results", [])
    perturbation_report = generate_perturbation_resistance_report(task_results, curriculum_cases)

    payload = {
        "task_count": len(PROTOTYPE_V6_CASES),
        "curriculum_count": len(curriculum_cases),
        "conditions": DEFAULT_CONDITIONS,
        "classification_report": classification_report,
        "summary_base": summary_base,
        "summary_curriculum": summary_curriculum,
        "perturbation_resistance": perturbation_report,
        "raw_results_base": results_base,
        "raw_results_curriculum": results_curriculum,
    }
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


if __name__ == "__main__":
    payload = run_local_eval_v6()
    print(json.dumps(payload["perturbation_resistance"], indent=2, ensure_ascii=False))
