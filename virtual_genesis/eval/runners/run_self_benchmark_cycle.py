from __future__ import annotations

from typing import Dict, List, Optional

from .compare_conditions import compare_conditions
from .regime_transition_detector import check_regime_transition, RegimeTransitionDecision
from ..reports.anomaly_candidates import generate_anomaly_candidate_report
from ..reports.blind_spot_discovery import discover_blind_spots
from ..reports.diagnostic_value import compute_diagnostic_value_report
from ..benchmark_generator import generate_from_anomaly_candidates
from ..negative_memory_adversarial import (
    generate_from_negative_memory,
    merge_negative_memory_with_anomalies,
)


_DEFAULT_CONDITIONS = ["baseline_0", "baseline_1", "condition_c_combined"]

# Baseline condition IDs used to extract "with/without" accuracy for
# the degradation signal.  baseline_0 = no memory/economy/concepts,
# condition_c_combined = full pipeline.
_BASELINE_CONDITION = "baseline_0"
_FULL_CONDITION = "condition_c_combined"


def _extract_success_rate(condition_result: dict) -> float:
    """Extract success rate from a condition result dict."""
    agg = condition_result.get("aggregate_metrics", {})
    return agg.get("success_rate", 0.0)


def run_self_benchmark_cycle(
    task_cases: list,
    conditions: list[str] | None = None,
    use_self_benchmarking: bool = True,
    *,
    # ── Regime Transition Detector inputs ──
    accuracy_history: List[float] | None = None,
    negative_memory_failures: List[dict] | None = None,
    saturation_window_k: int = 3,
    saturation_epsilon: float = 0.01,
    trigger_threshold: int = 2,
) -> dict:
    """Run a self-benchmarking cycle with regime transition detection.

    Steps 1-6: Original self-benchmarking (anomaly → blind spots → generate → re-eval)
    Step 7:   Compute diagnostic values
    Step 8:   [NEW] Check for regime transition signals
    Step 9:   Return combined report with transition decision

    Args:
        task_cases: TaskCase objects to evaluate.
        conditions: condition IDs to compare (default: 3 standard conditions).
        use_self_benchmarking: master switch (False → skip everything).
        accuracy_history: chronological accuracy values for saturation detection.
        negative_memory_failures: failure records from T-13 for adversarial test gen.
        saturation_window_k: consecutive flat iterations before saturation signal.
        saturation_epsilon: minimum accuracy delta to count as improvement.
        trigger_threshold: how many of 3 signals needed to trigger transition.
    """
    condition_ids = conditions or _DEFAULT_CONDITIONS

    # Step 1: Run current eval
    base_results = compare_conditions(condition_ids, task_cases)

    if not use_self_benchmarking:
        return {
            "base_results": base_results,
            "self_benchmarking_enabled": False,
        }

    # Step 2: Analyze for anomaly candidates
    # Collect all task results across conditions
    all_task_results: List[dict] = []
    all_results_by_condition: Dict[str, list] = {}
    for cond_id, cond_result in base_results.items():
        task_results = cond_result.get("task_results", [])
        all_task_results.extend(task_results)
        all_results_by_condition[cond_id] = task_results

    anomaly_report = generate_anomaly_candidate_report(all_task_results)

    # Collect individual anomaly candidate dicts
    anomaly_candidates: List[dict] = []
    for result in all_task_results:
        for candidate in result.get("anomaly_candidates", []) or []:
            anomaly_candidates.append(candidate)

    # Step 3: Discover blind spots
    blind_spot_report = discover_blind_spots(all_task_results, task_cases)

    # Step 4: Generate new benchmark cases
    # 4a: From anomalies (existing path)
    anomaly_cases = generate_from_anomaly_candidates(anomaly_candidates)

    # 4b: [NEW] From Negative Memory failures (T-13 → H8 bridge)
    negative_memory_cases = []
    if negative_memory_failures:
        negative_memory_cases = generate_from_negative_memory(negative_memory_failures)

    # 4c: Merge with priority to negative memory cases (known failures > generic anomalies)
    new_cases = merge_negative_memory_with_anomalies(
        negative_memory_cases, anomaly_cases,
    )

    # Step 5: Run conditions against new cases (if any were generated)
    new_results = {}
    if new_cases:
        new_results = compare_conditions(condition_ids, new_cases)

    # Step 6: Compute diagnostic values for all cases
    # Combine base and new results by condition
    combined_by_condition: Dict[str, list] = {}
    for cond_id in condition_ids:
        combined_by_condition[cond_id] = list(
            base_results.get(cond_id, {}).get("task_results", [])
        )
        if new_results:
            combined_by_condition[cond_id].extend(
                new_results.get(cond_id, {}).get("task_results", [])
            )

    diagnostic_report = compute_diagnostic_value_report(combined_by_condition)

    # ── Step 7 (was 8): [NEW] Regime Transition Detection ──
    transition_decision: Optional[RegimeTransitionDecision] = None

    # Extract accuracy_with_new / accuracy_without_new from conditions
    acc_with_new = None
    acc_without_new = None
    if _BASELINE_CONDITION in base_results:
        acc_without_new = _extract_success_rate(base_results[_BASELINE_CONDITION])
    if _FULL_CONDITION in base_results:
        acc_with_new = _extract_success_rate(base_results[_FULL_CONDITION])

    transition_decision = check_regime_transition(
        accuracy_history=accuracy_history or [],
        blind_spot_report=blind_spot_report,
        accuracy_with_new=acc_with_new,
        accuracy_without_new=acc_without_new,
        saturation_window_k=saturation_window_k,
        saturation_epsilon=saturation_epsilon,
        trigger_threshold=trigger_threshold,
    )

    # Step 8 (was 9): Return combined report
    result = {
        "self_benchmarking_enabled": True,
        "base_results": base_results,
        "anomaly_report": anomaly_report,
        "anomaly_candidates_count": len(anomaly_candidates),
        "blind_spot_report": blind_spot_report,
        "negative_memory_cases_generated": len(negative_memory_cases),
        "new_cases_generated": len(new_cases),
        "new_results": new_results,
        "diagnostic_report": diagnostic_report,
        # ── NEW: Regime Transition Decision ──
        "regime_transition": transition_decision.to_dict() if transition_decision else None,
    }

    if transition_decision and transition_decision.should_transition:
        result["regime_transition_required"] = True
        result["recommended_actions"] = transition_decision.recommended_actions
    else:
        result["regime_transition_required"] = False

    return result
