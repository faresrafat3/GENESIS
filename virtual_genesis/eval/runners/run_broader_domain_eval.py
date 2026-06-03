from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ...runtime.task_ingress.service import ingest_task
from .compare_conditions import compare_conditions
from ..reports.summary import summarize_comparison
from ..reports.perturbation_resistance import generate_perturbation_resistance_report
from ..reports.domain_transfer import generate_domain_transfer_report
from ..task_sets.prototype_v7_broader_domain import (
    PROTOTYPE_V7_BROADER_DOMAIN_CASES,
    build_v7_broader_domain_curriculum,
)

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


def run_broader_domain_eval(output_path: str = "virtual_genesis/eval/results/broader_domain_summary.json") -> dict:
    """Run broader domain evaluation: new family cases + curriculum variants across all conditions.

    Returns the combined payload with classification reports, condition comparisons,
    domain transfer analysis, and perturbation resistance analysis.
    """
    # Build curriculum from v7 broader domain cases (6 levels)
    curriculum_cases = build_v7_broader_domain_curriculum()

    # Classification report on base v7 broader domain cases
    classification_report = build_case_report(PROTOTYPE_V7_BROADER_DOMAIN_CASES)

    # Run conditions against base v7 cases
    results_base = compare_conditions(
        DEFAULT_CONDITIONS, PROTOTYPE_V7_BROADER_DOMAIN_CASES, task_set_ref="prototype_v7_broader_domain"
    )

    # Run conditions against curriculum-perturbed cases
    results_curriculum = compare_conditions(
        DEFAULT_CONDITIONS, curriculum_cases, task_set_ref="prototype_v7_broader_domain_curriculum"
    )

    summary_base = summarize_comparison(results_base)
    summary_curriculum = summarize_comparison(results_curriculum)

    # Generate perturbation resistance report from combined condition
    combined_curriculum_results = results_curriculum.get("condition_c_combined", {})
    task_results_curriculum = combined_curriculum_results.get("task_results", [])
    perturbation_report = generate_perturbation_resistance_report(task_results_curriculum, curriculum_cases)

    # Generate domain transfer report from combined condition base results
    combined_base_results = results_base.get("condition_c_combined", {})
    task_results_base = combined_base_results.get("task_results", [])
    domain_transfer_report = generate_domain_transfer_report(task_results_base + task_results_curriculum)

    payload = {
        "task_count": len(PROTOTYPE_V7_BROADER_DOMAIN_CASES),
        "curriculum_count": len(curriculum_cases),
        "conditions": DEFAULT_CONDITIONS,
        "classification_report": classification_report,
        "summary_base": summary_base,
        "summary_curriculum": summary_curriculum,
        "perturbation_resistance": perturbation_report,
        "domain_transfer": domain_transfer_report,
        "raw_results_base": results_base,
        "raw_results_curriculum": results_curriculum,
    }
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


if __name__ == "__main__":
    payload = run_broader_domain_eval()
    print(json.dumps(payload["domain_transfer"], indent=2, ensure_ascii=False))
