"""Regime Transition Bridge — connects orchestrator loop to regime detector.

Provides a single function that the orchestrator calls at the end of each
generation. It:
1. Reads accuracy history from all previous generations
2. Extracts failures from evaluation results (Negative Memory)
3. Runs the conditions runner (if task cases available)
4. Produces a regime transition decision
5. Saves the report and returns it

This keeps the orchestrator injection minimal — one function call, one JSON
artifact per generation, zero side effects on the main loop.

Usage in orchestrator.py:
    from virtual_genesis.eval.runners.regime_orchestrator_bridge import (
        run_regime_check,
    )
    ...
    regime_report = run_regime_check(run_dir, current_gen, max_gen)
    if regime_report and regime_report.get("regime_transition_required"):
        ...
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from .failure_extractor import (
    build_accuracy_history,
    extract_failures_across_generations,
    extract_accuracy_from_gen,
)
from .regime_transition_detector import check_regime_transition
from ..reports.blind_spot_discovery import discover_blind_spots


def run_regime_check(
    run_dir: str,
    current_gen: int,
    max_gen: int = 10,
    *,
    saturation_window_k: int = 3,
    saturation_epsilon: float = 0.01,
    trigger_threshold: int = 2,
    save_report: bool = True,
) -> Optional[Dict[str, Any]]:
    """Run regime transition check for the current generation.

    This is the single entry point the orchestrator calls. It handles
    everything internally — no pre-processing needed.

    Args:
        run_dir: path to the run directory (e.g., runs/run_1)
        current_gen: current generation number (1-indexed)
        max_gen: maximum generation number for scanning
        saturation_window_k: consecutive flat iterations for saturation
        saturation_epsilon: minimum delta to count as improvement
        trigger_threshold: how many of 3 signals to trigger transition
        save_report: whether to save JSON report to gen directory

    Returns:
        Dict with regime transition info, or None if insufficient data.
    """
    current_gen_dir = os.path.join(run_dir, f"gen_{current_gen}")

    # 1. Build accuracy history from all generations so far
    accuracy_history = build_accuracy_history(run_dir, max_gen=current_gen)

    # 2. Extract failures from all previous generations (Negative Memory)
    failures, failure_stats = extract_failures_across_generations(
        run_dir, max_gen=current_gen - 1  # exclude current gen
    )

    # 3. Build blind spot report from available data
    #    (we don't have condition comparison data here, so use a minimal report)
    blind_spot_report = _build_minimal_blind_spot_report(run_dir, current_gen)

    # 4. Get accuracy for degradation signal
    current_accuracy = extract_accuracy_from_gen(current_gen_dir)
    prev_accuracy = None
    if current_gen > 1:
        prev_gen_dir = os.path.join(run_dir, f"gen_{current_gen - 1}")
        prev_accuracy = extract_accuracy_from_gen(prev_gen_dir)

    # 5. Run regime transition check
    decision = check_regime_transition(
        accuracy_history=accuracy_history,
        blind_spot_report=blind_spot_report,
        accuracy_with_new=current_accuracy,
        accuracy_without_new=prev_accuracy,
        saturation_window_k=saturation_window_k,
        saturation_epsilon=saturation_epsilon,
        trigger_threshold=trigger_threshold,
    )

    # 6. Build report
    report = {
        "generation": current_gen,
        "accuracy_history": [round(a, 4) for a in accuracy_history],
        "current_accuracy": round(current_accuracy, 4) if current_accuracy is not None else None,
        "prev_accuracy": round(prev_accuracy, 4) if prev_accuracy is not None else None,
        "failure_stats": failure_stats,
        "negative_memory_failures_count": len(failures),
        "regime_decision": decision.to_dict(),
        "regime_transition_required": decision.should_transition,
    }

    # 7. Save report
    if save_report:
        report_path = os.path.join(current_gen_dir, "regime_transition_report.json")
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        except Exception:
            pass  # non-critical — don't crash the main loop

    # 8. Update the run-level regime history file
    _update_regime_history(run_dir, current_gen, report)

    return report


def load_regime_history(run_dir: str) -> List[Dict[str, Any]]:
    """Load the accumulated regime history from a run directory.

    Returns:
        List of regime reports, one per generation that was checked.
    """
    history_path = os.path.join(run_dir, "regime_history.json")
    if not os.path.exists(history_path):
        return []
    try:
        with open(history_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


def get_regime_transition_generations(run_dir: str) -> List[int]:
    """Get the generation numbers where regime transitions were detected.

    Returns:
        List of generation numbers (1-indexed).
    """
    history = load_regime_history(run_dir)
    return [
        entry.get("generation", 0)
        for entry in history
        if entry.get("regime_transition_required", False)
    ]


# ── Internal helpers ──────────────────────────────────────────────────────


def _build_minimal_blind_spot_report(
    run_dir: str,
    current_gen: int,
) -> Dict[str, Any]:
    """Build a minimal blind spot report from available execution data.

    Since we don't have full condition comparison data in the orchestrator,
    we infer blind spots from accuracy patterns:
    - If accuracy dropped significantly from previous gen → blind spot signal
    """
    report = {
        "suspiciously_easy_regions": [],
        "untested_combinations": [],
        "coverage_ratio": 1.0,  # default: assume full coverage
        "coverage_matrix": {},
    }

    # Check for accuracy drop as a proxy for blind spots
    if current_gen > 1:
        prev_acc = extract_accuracy_from_gen(os.path.join(run_dir, f"gen_{current_gen - 1}"))
        curr_acc = extract_accuracy_from_gen(os.path.join(run_dir, f"gen_{current_gen}"))

        if prev_acc is not None and curr_acc is not None:
            if curr_acc < prev_acc - 0.05:  # >5% drop
                report["suspiciously_easy_regions"] = [
                    ("accuracy_regression", "gen_over_gen", "hard")
                ]
                # This also means coverage is misleading
                report["coverage_ratio"] = 0.5

    return report


def _update_regime_history(
    run_dir: str,
    gen_num: int,
    report: Dict[str, Any],
) -> None:
    """Append regime report to the run-level history file."""
    history_path = os.path.join(run_dir, "regime_history.json")

    history = []
    if os.path.exists(history_path):
        try:
            with open(history_path, encoding="utf-8") as f:
                history = json.load(f)
        except (json.JSONDecodeError, ValueError):
            history = []

    # Replace entry for this generation if it exists, else append
    entry = {"generation": gen_num, **{k: v for k, v in report.items() if k != "generation"}}
    found = False
    for i, existing in enumerate(history):
        if existing.get("generation") == gen_num:
            history[i] = entry
            found = True
            break
    if not found:
        history.append(entry)

    # Keep sorted by generation
    history.sort(key=lambda x: x.get("generation", 0))

    try:
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False, default=str)
    except Exception:
        pass  # non-critical
