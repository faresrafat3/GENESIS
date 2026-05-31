"""Real LLM evaluation runner using OpenRouter API.

WARNING: This module makes real API calls that cost money.
Run only via `if __name__ == '__main__'` block, NOT in automated tests.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from ...api.llm_reasoning import build_augmented_prompt, build_raw_prompt, _call_openrouter
from ...api.config import OPENROUTER_API_KEY, DEFAULT_MODEL
from ...core.objects.task_case import TaskCase
from ...runtime.verification_runtime.service import verify_output
from ..task_sets.prototype_v6_cases import PROTOTYPE_V6_CASES


def select_eval_tasks(count_per_family: int = 2) -> list[TaskCase]:
    """Select a small subset of tasks for real eval (2 per family)."""
    families: dict[str, list[TaskCase]] = {"comparison": [], "synthesis": [], "procedure": []}
    for case in PROTOTYPE_V6_CASES:
        family = case.expected_primary_family
        if family in families and len(families[family]) < count_per_family:
            families[family].append(case)
    result = []
    for family_cases in families.values():
        result.extend(family_cases)
    return result


def run_single_condition(
    task: TaskCase,
    condition: str,
    concept_hints: list[str] | None = None,
    theory_hints: list[str] | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Run a single task through one condition with real LLM."""
    resolved_key = api_key or os.environ.get("OPENROUTER_API_KEY") or OPENROUTER_API_KEY

    if condition == "A_raw":
        prompt = build_raw_prompt(task.prompt_text)
    elif condition == "B_concept":
        prompt = build_augmented_prompt(task.prompt_text, concept_hints)
    else:  # C_full
        prompt = build_augmented_prompt(task.prompt_text, concept_hints, theory_hints)

    # Call LLM directly with the locally-built prompt
    response = _call_openrouter(prompt, DEFAULT_MODEL, resolved_key)

    # Check for LLM errors before verification
    if response.startswith("[LLM_ERROR]"):
        return {
            "task_id": task.id,
            "task_family": task.expected_primary_family,
            "condition": condition,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "response_preview": response[:200],
            "error": response,
            "good_enough": False,
        }

    # Verify against contract
    task_contract = {
        "required_properties": task.required_properties,
        "forbidden_shortcuts": task.forbidden_shortcuts,
    }
    verification = verify_output(
        task.expected_primary_family,
        response,
        framing_candidates=[task.expected_primary_family] + task.expected_secondary_families,
        task_contract=task_contract,
    )

    return {
        "task_id": task.id,
        "task_family": task.expected_primary_family,
        "condition": condition,
        "prompt_length": len(prompt),
        "response_length": len(response),
        "response_preview": response[:200],
        "good_enough": verification["verification_summary"]["good_enough"],
        "property_checks": verification.get("property_checks", {}),
        "shortcut_checks": verification.get("shortcut_checks", {}),
    }


def run_real_llm_eval(api_key: str | None = None, delay_between_calls: float = 1.0) -> dict:
    """Run full real LLM evaluation comparing 3 conditions.

    Returns structured results with per-condition success rates.
    """
    tasks = select_eval_tasks(count_per_family=2)
    resolved_key = api_key or os.environ.get("OPENROUTER_API_KEY") or OPENROUTER_API_KEY

    # Define concept and theory hints for augmentation
    concept_hints = [
        "Evidence-grounded reasoning: conclusions must trace back to specific observations",
        "Structural completeness: outputs must satisfy all required properties in the contract",
        "Shortcut avoidance: generic summaries without specific evidence are forbidden",
    ]
    theory_hints = [
        "Complexity-accuracy tradeoff: harder tasks require more detailed reasoning",
        "Family-specific patterns: comparison tasks need explicit contrasts, synthesis needs integration, procedure needs structure",
        "Contract compliance: verification checks every required property individually",
    ]

    all_results: list[dict] = []
    conditions = ["A_raw", "B_concept", "C_full"]

    for task in tasks:
        for condition in conditions:
            try:
                result = run_single_condition(
                    task, condition,
                    concept_hints=concept_hints,
                    theory_hints=theory_hints,
                    api_key=resolved_key,
                )
                all_results.append(result)
            except Exception as e:
                all_results.append({
                    "task_id": task.id,
                    "task_family": task.expected_primary_family,
                    "condition": condition,
                    "error": str(e),
                    "good_enough": False,
                })
            time.sleep(delay_between_calls)  # Rate limiting

    # Compute summary
    summary = compute_eval_summary(all_results)

    # Save results
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    output_path = results_dir / "real_llm_eval_summary.json"
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    return summary


def compute_eval_summary(results: list[dict]) -> dict:
    """Compute aggregate metrics from evaluation results."""
    by_condition: dict[str, list[bool]] = {"A_raw": [], "B_concept": [], "C_full": []}
    by_family: dict[str, dict[str, list[bool]]] = {}

    for r in results:
        condition = r.get("condition", "unknown")
        family = r.get("task_family", "unknown")
        good = r.get("good_enough", False)

        if condition in by_condition:
            by_condition[condition].append(good)

        if family not in by_family:
            by_family[family] = {"A_raw": [], "B_concept": [], "C_full": []}
        if condition in by_family[family]:
            by_family[family][condition].append(good)

    def rate(lst: list[bool]) -> float:
        return sum(lst) / len(lst) if lst else 0.0

    return {
        "total_evaluations": len(results),
        "conditions": {
            cond: {"success_rate": rate(goods), "total": len(goods), "successes": sum(goods)}
            for cond, goods in by_condition.items()
        },
        "by_family": {
            family: {
                cond: {"success_rate": rate(goods), "total": len(goods)}
                for cond, goods in cond_data.items()
            }
            for family, cond_data in by_family.items()
        },
        "concept_lift": rate(by_condition["B_concept"]) - rate(by_condition["A_raw"]),
        "theory_lift": rate(by_condition["C_full"]) - rate(by_condition["B_concept"]),
        "total_lift": rate(by_condition["C_full"]) - rate(by_condition["A_raw"]),
        "model_used": DEFAULT_MODEL,
        "all_results": results,
    }


if __name__ == "__main__":
    print("Running Real LLM Evaluation with OpenRouter...")
    print(f"Model: {DEFAULT_MODEL}")
    print(f"API Key: {'set' if os.environ.get('OPENROUTER_API_KEY') or OPENROUTER_API_KEY else 'NOT SET'}")
    print("---")

    summary = run_real_llm_eval(delay_between_calls=1.5)

    print(f"\nTotal evaluations: {summary['total_evaluations']}")
    print(f"\nSuccess rates by condition:")
    for cond, data in summary["conditions"].items():
        print(f"  {cond}: {data['success_rate']:.2%} ({data['successes']}/{data['total']})")
    print(f"\nConcept lift: {summary['concept_lift']:+.2%}")
    print(f"Theory lift: {summary['theory_lift']:+.2%}")
    print(f"Total lift: {summary['total_lift']:+.2%}")
    print(f"\nResults saved to virtual_sia/eval/results/real_llm_eval_summary.json")
