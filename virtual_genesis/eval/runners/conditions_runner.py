"""Conditions Runner — Standard vs Ablation with Signal Extraction.

The missing link between raw condition comparisons and regime transition
detection.  Instead of the orchestrator calling compare_conditions and then
manually extracting success_rate deltas, this module provides a single call
that:

1. Runs the system under Standard and Ablation conditions
2. Extracts success_rate deltas (the Degradation signal)
3. Accumulates accuracy_history across iterations (the Saturation signal)
4. Generates blind_spot_report from coverage analysis (the Blind Spot signal)
5. Feeds everything to regime_transition_detector
6. Returns a clean ConditionsRunnerResult

This is the "signal generator" that makes the regime detector work.
Without it, regime_transition_detector is blind.

Ablation configurations available:
    - standard_vs_bare:         Full pipeline vs nothing
    - standard_vs_memory_only:  Full pipeline vs memory only (no economy/concepts)
    - standard_vs_no_concepts:  Full pipeline vs economy+memory (no concepts)
    - standard_vs_no_economy:   Full pipeline vs concepts+memory (no economy)

Reference: GENESIS/PAPER/analysis/REGIME_TRANSITION_INJECTION_ROADMAP.md
Phase:    1 (Conditions Runner) — the first step before orchestrator integration
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .compare_conditions import compare_conditions
from .regime_transition_detector import (
    RegimeTransitionDecision,
    TransitionVerdict,
    check_regime_transition,
)
from ..reports.blind_spot_discovery import discover_blind_spots
from ..reports.diagnostic_value import compute_diagnostic_value_report
from ..reports.summary import summarize_comparison


# ── Condition Profiles ────────────────────────────────────────────────────


@dataclass(slots=True)
class ConditionProfile:
    """A named, documented configuration for a single condition."""
    condition_id: str
    label: str           # Human-readable: "Standard (Full Pipeline)"
    description: str     # What this condition tests
    what_enabled: str    # What subsystems are active
    what_disabled: str   # What subsystems are disabled (empty if standard)

    def to_dict(self) -> dict:
        return {
            "condition_id": self.condition_id,
            "label": self.label,
            "description": self.description,
            "what_enabled": self.what_enabled,
            "what_disabled": self.what_disabled,
        }


# ── Predefined Profiles ──────────────────────────────────────────────────

STANDARD = ConditionProfile(
    condition_id="condition_c_combined",
    label="Standard (Full Pipeline)",
    description="All subsystems active — the default operating configuration",
    what_enabled="memory, economy, concepts, auto-tier",
    what_disabled="",
)

ABLATION_BARE = ConditionProfile(
    condition_id="baseline_0",
    label="Ablation: Bare Baseline",
    description="No subsystems — pure reasoning without any cognitive scaffolding",
    what_enabled="tier_1 (forced)",
    what_disabled="memory, economy, concepts",
)

ABLATION_MEMORY_ONLY = ConditionProfile(
    condition_id="baseline_1",
    label="Ablation: Memory Only",
    description="Memory retrieval active but no economy routing or concept leverage",
    what_enabled="memory, tier_1 (forced)",
    what_disabled="economy, concepts",
)

ABLATION_PREMIUM_ALWAYS = ConditionProfile(
    condition_id="baseline_2_premium_always",
    label="Ablation: Premium Always",
    description="Memory + forced premium tier — tests whether economy routing saves cost",
    what_enabled="memory, tier_2 (forced)",
    what_disabled="economy, concepts",
)

ABLATION_NO_CONCEPTS = ConditionProfile(
    condition_id="condition_b_economy",
    label="Ablation: No Concepts",
    description="Memory + economy routing but no concept formation or application",
    what_enabled="memory, economy, auto-tier",
    what_disabled="concepts",
)

ABLATION_NO_ECONOMY = ConditionProfile(
    condition_id="condition_a_concept_ready",
    label="Ablation: No Economy",
    description="Memory + concepts but no economy-aware tier routing",
    what_enabled="memory, concepts, tier_1 (forced)",
    what_disabled="economy, auto-tier",
)


# ── Comparison Configurations ─────────────────────────────────────────────


@dataclass(slots=True)
class ComparisonConfig:
    """A pair of profiles to compare: standard vs ablation."""
    comparison_id: str
    standard: ConditionProfile
    ablation: ConditionProfile
    description: str

    def to_dict(self) -> dict:
        return {
            "comparison_id": self.comparison_id,
            "description": self.description,
            "standard": self.standard.to_dict(),
            "ablation": self.ablation.to_dict(),
        }


# Predefined comparison configurations
COMPARISON_CONFIGS: Dict[str, ComparisonConfig] = {
    "standard_vs_bare": ComparisonConfig(
        comparison_id="standard_vs_bare",
        standard=STANDARD,
        ablation=ABLATION_BARE,
        description="Full pipeline vs bare baseline — measures total cognitive scaffolding value",
    ),
    "standard_vs_memory_only": ComparisonConfig(
        comparison_id="standard_vs_memory_only",
        standard=STANDARD,
        ablation=ABLATION_MEMORY_ONLY,
        description="Full pipeline vs memory only — isolates economy + concept contribution",
    ),
    "standard_vs_no_concepts": ComparisonConfig(
        comparison_id="standard_vs_no_concepts",
        standard=STANDARD,
        ablation=ABLATION_NO_CONCEPTS,
        description="Full pipeline vs economy+memory — isolates concept formation contribution",
    ),
    "standard_vs_no_economy": ComparisonConfig(
        comparison_id="standard_vs_no_economy",
        standard=STANDARD,
        ablation=ABLATION_NO_ECONOMY,
        description="Full pipeline vs concepts+memory — isolates economy routing contribution",
    ),
    "standard_vs_premium_always": ComparisonConfig(
        comparison_id="standard_vs_premium_always",
        standard=STANDARD,
        ablation=ABLATION_PREMIUM_ALWAYS,
        description="Full pipeline vs forced premium — measures economy cost optimization",
    ),
}

DEFAULT_COMPARISON = "standard_vs_bare"


# ── Result Dataclass ──────────────────────────────────────────────────────


@dataclass(slots=True)
class ConditionsRunnerResult:
    """Complete output of a conditions comparison run.

    Contains everything the orchestrator needs to decide whether to
    initiate a regime transition.
    """
    # Identification
    comparison_id: str
    iteration: int

    # Profiles used
    standard_profile_id: str
    ablation_profile_id: str

    # Core metrics
    standard_success_rate: float
    ablation_success_rate: float
    delta: float                    # standard - ablation (positive = pipeline helps)
    task_count: int

    # Cost metrics
    standard_avg_cost: float
    ablation_avg_cost: float
    cost_delta: float               # standard - ablation

    # Signal data for regime detector
    accuracy_history: List[float]   # accumulated across iterations
    blind_spot_report: Dict[str, Any]
    diagnostic_value_avg: float

    # The regime transition decision
    regime_decision: Optional[RegimeTransitionDecision] = None

    # Raw comparison data (for detailed analysis)
    summary: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "comparison_id": self.comparison_id,
            "iteration": self.iteration,
            "standard_profile_id": self.standard_profile_id,
            "ablation_profile_id": self.ablation_profile_id,
            "standard_success_rate": round(self.standard_success_rate, 4),
            "ablation_success_rate": round(self.ablation_success_rate, 4),
            "delta": round(self.delta, 4),
            "task_count": self.task_count,
            "standard_avg_cost": round(self.standard_avg_cost, 6),
            "ablation_avg_cost": round(self.ablation_avg_cost, 6),
            "cost_delta": round(self.cost_delta, 6),
            "accuracy_history": [round(a, 4) for a in self.accuracy_history],
            "blind_spot_report": self.blind_spot_report,
            "diagnostic_value_avg": round(self.diagnostic_value_avg, 4),
            "regime_decision": self.regime_decision.to_dict() if self.regime_decision else None,
            "should_transition": self.regime_decision.should_transition if self.regime_decision else False,
            "summary": self.summary,
            "meta": self.meta,
        }

    @property
    def should_transition(self) -> bool:
        return self.regime_decision.should_transition if self.regime_decision else False

    @property
    def pipeline_helps(self) -> bool:
        """True if standard (full pipeline) outperforms ablation."""
        return self.delta > 0

    @property
    def pipeline_hurts(self) -> bool:
        """True if adding pipeline subsystems reduces performance.

        This is exactly the Degradation signal — when it fires, the system
        is in Anti-Antifragile territory (AAS=1.0).
        """
        return self.delta < 0


# ── Main Runner ───────────────────────────────────────────────────────────


def run_conditions_comparison(
    task_cases: list,
    *,
    comparison_id: str = DEFAULT_COMPARISON,
    accuracy_history: List[float] | None = None,
    negative_memory_failures: List[dict] | None = None,
    iteration: int = 0,
    run_regime_check: bool = True,
    saturation_window_k: int = 3,
    saturation_epsilon: float = 0.01,
    trigger_threshold: int = 2,
) -> ConditionsRunnerResult:
    """Run Standard vs Ablation comparison and extract regime transition signals.

    This is the main entry point for Phase 1 (Conditions Runner).
    It produces the accuracy_history, delta, and blind_spot_report that
    regime_transition_detector needs.

    Args:
        task_cases: TaskCase objects to evaluate under both conditions.
        comparison_id: which ComparisonConfig to use (default: standard_vs_bare).
        accuracy_history: previous iterations' success rates (for saturation detection).
        negative_memory_failures: T-13 failures for adversarial test generation.
        iteration: current iteration number (for tracking).
        run_regime_check: whether to run regime transition detection.
        saturation_window_k: consecutive flat iterations for saturation signal.
        saturation_epsilon: minimum delta to count as improvement.
        trigger_threshold: how many of 3 signals needed to trigger.

    Returns:
        ConditionsRunnerResult with all metrics and regime decision.
    """
    config = COMPARISON_CONFIGS[comparison_id]

    # Run both conditions
    condition_ids = [config.standard.condition_id, config.ablation.condition_id]
    raw_results = compare_conditions(condition_ids, task_cases)

    # Extract metrics from results
    standard_data = raw_results.get(config.standard.condition_id, {})
    ablation_data = raw_results.get(config.ablation.condition_id, {})

    standard_agg = standard_data.get("aggregate_metrics", {})
    ablation_agg = ablation_data.get("aggregate_metrics", {})

    standard_success_rate = standard_agg.get("success_rate", 0.0)
    ablation_success_rate = ablation_agg.get("success_rate", 0.0)
    delta = standard_success_rate - ablation_success_rate

    standard_avg_cost = standard_agg.get("avg_estimated_cost", 0.0)
    ablation_avg_cost = ablation_agg.get("avg_estimated_cost", 0.0)

    # Build accuracy history (append current standard success rate)
    history = list(accuracy_history or [])
    history.append(standard_success_rate)

    # Extract all task results for blind spot analysis
    all_task_results = []
    for cond_data in [standard_data, ablation_data]:
        all_task_results.extend(cond_data.get("task_results", []))

    blind_spot_report = discover_blind_spots(all_task_results, task_cases)

    # Compute diagnostic value across conditions
    results_by_condition = {
        config.standard.condition_id: standard_data.get("task_results", []),
        config.ablation.condition_id: ablation_data.get("task_results", []),
    }
    diagnostic_report = compute_diagnostic_value_report(results_by_condition)
    diagnostic_value_avg = diagnostic_report.get("avg_diagnostic_value", 0.0)

    # Generate summary using existing report module
    summary = summarize_comparison(raw_results)

    # Run regime transition check
    regime_decision = None
    if run_regime_check:
        regime_decision = check_regime_transition(
            accuracy_history=history,
            blind_spot_report=blind_spot_report,
            accuracy_with_new=standard_success_rate,
            accuracy_without_new=ablation_success_rate,
            saturation_window_k=saturation_window_k,
            saturation_epsilon=saturation_epsilon,
            trigger_threshold=trigger_threshold,
        )

    return ConditionsRunnerResult(
        comparison_id=comparison_id,
        iteration=iteration,
        standard_profile_id=config.standard.condition_id,
        ablation_profile_id=config.ablation.condition_id,
        standard_success_rate=standard_success_rate,
        ablation_success_rate=ablation_success_rate,
        delta=delta,
        task_count=len(task_cases),
        standard_avg_cost=standard_avg_cost,
        ablation_avg_cost=ablation_avg_cost,
        cost_delta=standard_avg_cost - ablation_avg_cost,
        accuracy_history=history,
        blind_spot_report=blind_spot_report,
        diagnostic_value_avg=diagnostic_value_avg,
        regime_decision=regime_decision,
        summary=summary,
        meta={
            "negative_memory_failures_count": len(negative_memory_failures) if negative_memory_failures else 0,
            "comparison_description": config.description,
            "history_length": len(history),
        },
    )


def run_multi_ablation(
    task_cases: list,
    *,
    accuracy_history: List[float] | None = None,
    iteration: int = 0,
    run_regime_check: bool = True,
) -> Dict[str, ConditionsRunnerResult]:
    """Run ALL predefined ablation comparisons in one call.

    Useful for comprehensive diagnostics: compare standard against every
    possible ablation to identify which subsystem contributes what.

    Args:
        task_cases: TaskCase objects to evaluate.
        accuracy_history: previous iterations' success rates.
        iteration: current iteration number.
        run_regime_check: whether to run regime transition detection.

    Returns:
        Dict mapping comparison_id → ConditionsRunnerResult.
    """
    results = {}
    for comp_id in COMPARISON_CONFIGS:
        results[comp_id] = run_conditions_comparison(
            task_cases,
            comparison_id=comp_id,
            accuracy_history=accuracy_history,
            iteration=iteration,
            run_regime_check=run_regime_check,
        )
    return results


def extract_signal_deltas(
    results: Dict[str, ConditionsRunnerResult],
) -> Dict[str, Dict[str, float]]:
    """Extract a compact summary of all signal deltas from multi-ablation run.

    Returns dict mapping comparison_id → {delta, cost_delta, ...}.
    """
    deltas = {}
    for comp_id, result in results.items():
        deltas[comp_id] = {
            "delta": round(result.delta, 4),
            "cost_delta": round(result.cost_delta, 6),
            "standard_success_rate": round(result.standard_success_rate, 4),
            "ablation_success_rate": round(result.ablation_success_rate, 4),
            "pipeline_helps": result.pipeline_helps,
            "pipeline_hurts": result.pipeline_hurts,
            "diagnostic_value_avg": round(result.diagnostic_value_avg, 4),
            "should_transition": result.should_transition,
        }
    return deltas
