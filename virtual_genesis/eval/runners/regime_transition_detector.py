"""Regime Transition Detector — the missing piece from Wang & Buehler (2026).

This module implements the 3-signal decision mechanism that replaces the
external physics simulator in the Builder/Breaker framework.  Instead of
a simulator telling the system "your model is wrong", the system uses
internal performance contradictions to decide when the current schema
has reached its ceiling and a regime transition is necessary.

The Three Signals:
    1. Saturation   — accuracy plateau or decline despite iteration
    2. Degradation  — "improvements" that actually harm performance
    3. Blind Spot   — suspiciously easy regions (shortcuts, not mastery)

Trigger Rule: 2-of-3 signals active → INITIATE_REGIME_TRANSITION

Reference: GENESIS/PAPER/analysis/SELF_BENCHMARKING_AS_REGIME_DETECTOR.md
Theory:    Anti-Antifragility (AAS=1.0), Theory-14
Theft:     arXiv:2606.01444 Observation 1 + 3, Definition 6
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ── Constants ──────────────────────────────────────────────────────────────

# How many consecutive iterations with near-zero or negative delta
# before we declare saturation.
DEFAULT_SATURATION_WINDOW_K = 3

# Minimum absolute accuracy delta to count as "improvement".
# Below this → effectively flat (saturated).
DEFAULT_SATURATION_EPSILON = 0.01  # 1%

# Minimum accuracy drop to count as degradation when adding a new component.
DEFAULT_DEGRADATION_THRESHOLD = 0.0  # any drop counts

# Success rate that triggers blind-spot suspicion for "hard" regions.
DEFAULT_BLIND_SPOT_SUCCESS_RATE = 1.0

# Minimum number of runs in a region before we evaluate its success rate
# (avoids false positives from n=1).
DEFAULT_BLIND_SPOT_MIN_RUNS = 2


# ── Data Structures ───────────────────────────────────────────────────────


class SignalStatus(str, Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    INSUFFICIENT_DATA = "insufficient_data"


class TransitionVerdict(str, Enum):
    CONTINUE = "continue"              # stay in current regime
    TRANSITION = "transition"           # 2-of-3 signals fired
    INSUFFICIENT_DATA = "insufficient_data"  # not enough history yet


@dataclass
class SignalResult:
    """Detailed result for a single signal."""
    signal_name: str
    status: SignalStatus
    evidence: Dict[str, Any] = field(default_factory=dict)
    message: str = ""


@dataclass
class RegimeTransitionDecision:
    """Full decision from the regime transition detector."""
    verdict: TransitionVerdict
    signals: Dict[str, SignalResult] = field(default_factory=dict)
    active_signal_count: int = 0
    confidence: float = 0.0   # 0..1 — how confident in the verdict
    recommended_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def should_transition(self) -> bool:
        return self.verdict == TransitionVerdict.TRANSITION

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "active_signal_count": self.active_signal_count,
            "confidence": round(self.confidence, 3),
            "should_transition": self.should_transition,
            "signals": {
                name: {
                    "status": s.status.value,
                    "evidence": s.evidence,
                    "message": s.message,
                }
                for name, s in self.signals.items()
            },
            "recommended_actions": self.recommended_actions,
            "metadata": self.metadata,
        }


# ── Signal Detectors ──────────────────────────────────────────────────────


def detect_saturation(
    accuracy_history: List[float],
    *,
    window_k: int = DEFAULT_SATURATION_WINDOW_K,
    epsilon: float = DEFAULT_SATURATION_EPSILON,
) -> SignalResult:
    """Signal 1: Saturation — accuracy plateau or decline.

    Active when the last `window_k` accuracy deltas are all ≤ epsilon.
    This means: more iteration is not producing meaningful improvement.

    Args:
        accuracy_history: chronological list of accuracy values per iteration.
        window_k: how many consecutive flat/declining steps to require.
        epsilon: minimum delta to count as "improvement".

    Returns:
        SignalResult with status and evidence.
    """
    if len(accuracy_history) < window_k + 1:
        return SignalResult(
            signal_name="saturation",
            status=SignalStatus.INSUFFICIENT_DATA,
            evidence={"history_length": len(accuracy_history), "required": window_k + 1},
            message=f"Need at least {window_k + 1} data points, have {len(accuracy_history)}",
        )

    # Compute deltas: accuracy[i] - accuracy[i-1]
    deltas = [
        accuracy_history[i] - accuracy_history[i - 1]
        for i in range(1, len(accuracy_history))
    ]

    # Check the last `window_k` deltas
    recent_deltas = deltas[-window_k:]
    all_flat_or_declining = all(d <= epsilon for d in recent_deltas)

    avg_recent_delta = sum(recent_deltas) / len(recent_deltas) if recent_deltas else 0.0
    max_recent_delta = max(recent_deltas) if recent_deltas else 0.0

    if all_flat_or_declining:
        return SignalResult(
            signal_name="saturation",
            status=SignalStatus.ACTIVE,
            evidence={
                "recent_deltas": [round(d, 4) for d in recent_deltas],
                "avg_recent_delta": round(avg_recent_delta, 4),
                "max_recent_delta": round(max_recent_delta, 4),
                "window_k": window_k,
                "epsilon": epsilon,
                "latest_accuracy": round(accuracy_history[-1], 4),
            },
            message=(
                f"Accuracy saturated: last {window_k} deltas all ≤ {epsilon}. "
                f"Average recent delta: {avg_recent_delta:.4f}"
            ),
        )

    return SignalResult(
        signal_name="saturation",
        status=SignalStatus.INACTIVE,
        evidence={
            "recent_deltas": [round(d, 4) for d in recent_deltas],
            "avg_recent_delta": round(avg_recent_delta, 4),
            "max_recent_delta": round(max_recent_delta, 4),
        },
        message=f"Accuracy still improving. Best recent delta: {max_recent_delta:.4f}",
    )


def detect_degradation(
    accuracy_with_new: Optional[float],
    accuracy_without_new: Optional[float],
    *,
    threshold: float = DEFAULT_DEGRADATION_THRESHOLD,
) -> SignalResult:
    """Signal 2: Degradation — "improvements" that harm performance.

    Active when adding a new component/pipeline/capability *reduces* accuracy
    compared to the baseline without it.

    This is the A3 ablation signal: removing the pipeline improved accuracy +5.

    Args:
        accuracy_with_new: accuracy when new component is active.
        accuracy_without_new: accuracy when new component is absent.
        threshold: minimum accuracy drop to count as degradation.

    Returns:
        SignalResult with status and evidence.
    """
    if accuracy_with_new is None or accuracy_without_new is None:
        return SignalResult(
            signal_name="degradation",
            status=SignalStatus.INSUFFICIENT_DATA,
            evidence={
                "accuracy_with_new": accuracy_with_new,
                "accuracy_without_new": accuracy_without_new,
            },
            message="Missing one or both accuracy measurements",
        )

    delta = accuracy_with_new - accuracy_without_new

    if delta < -threshold:
        return SignalResult(
            signal_name="degradation",
            status=SignalStatus.ACTIVE,
            evidence={
                "accuracy_with_new": round(accuracy_with_new, 4),
                "accuracy_without_new": round(accuracy_without_new, 4),
                "delta": round(delta, 4),
                "threshold": threshold,
            },
            message=(
                f"Degradation detected: new component reduced accuracy by "
                f"{abs(delta):.4f} ({accuracy_with_new:.4f} vs {accuracy_without_new:.4f})"
            ),
        )

    return SignalResult(
        signal_name="degradation",
        status=SignalStatus.INACTIVE,
        evidence={
            "accuracy_with_new": round(accuracy_with_new, 4),
            "accuracy_without_new": round(accuracy_without_new, 4),
            "delta": round(delta, 4),
        },
        message=f"No degradation. Delta: {delta:+.4f}",
    )


def detect_blind_spot(
    blind_spot_report: dict,
    *,
    min_runs: int = DEFAULT_BLIND_SPOT_MIN_RUNS,
    target_success_rate: float = DEFAULT_BLIND_SPOT_SUCCESS_RATE,
    target_difficulty: str = "hard",
) -> SignalResult:
    """Signal 3: Blind Spot — suspiciously easy regions on hard difficulty.

    Active when the blind spot report contains regions classified as "hard"
    but with 100% success rate. This indicates the system is taking shortcuts,
    not genuinely mastering difficult content.

    Also active when there are many untested combinations (coverage gaps).

    Args:
        blind_spot_report: output from discover_blind_spots().
        min_runs: minimum runs in a region before evaluating.
        target_success_rate: success rate that triggers suspicion.
        target_difficulty: which difficulty class to check for blind spots.
    """
    suspiciously_easy = blind_spot_report.get("suspiciously_easy_regions", [])
    untested = blind_spot_report.get("untested_combinations", [])
    coverage_ratio = blind_spot_report.get("coverage_ratio", 1.0)
    coverage_matrix = blind_spot_report.get("coverage_matrix", {})

    # Filter suspiciously easy regions that are "hard" difficulty
    hard_easy_regions = [
        combo for combo in suspiciously_easy
        if len(combo) >= 3 and combo[2] == target_difficulty
    ]

    # Also check for suspiciously easy regions with enough runs
    well_sampled_hard_easy = 0
    for combo in hard_easy_regions:
        key = f"{combo[0]}|{combo[1]}|{combo[2]}"
        stats = coverage_matrix.get(key, {})
        if stats.get("total", 0) >= min_runs:
            well_sampled_hard_easy += 1

    # Check untested count relative to total
    untested_count = len(untested)

    evidence = {
        "suspiciously_easy_count": len(suspiciously_easy),
        "hard_easy_regions": len(hard_easy_regions),
        "well_sampled_hard_easy": well_sampled_hard_easy,
        "untested_combinations_count": untested_count,
        "coverage_ratio": round(coverage_ratio, 3),
        "target_difficulty": target_difficulty,
    }

    # Signal is active if:
    # 1. There are well-sampled hard regions with 100% success (shortcuts), OR
    # 2. Coverage ratio is below 50% (massive blind spots)
    if well_sampled_hard_easy > 0:
        return SignalResult(
            signal_name="blind_spot",
            status=SignalStatus.ACTIVE,
            evidence=evidence,
            message=(
                f"Found {well_sampled_hard_easy} hard-difficulty region(s) with "
                f"{target_success_rate*100:.0f}% success rate — likely shortcuts"
            ),
        )

    if coverage_ratio < 0.5 and untested_count > 0:
        return SignalResult(
            signal_name="blind_spot",
            status=SignalStatus.ACTIVE,
            evidence=evidence,
            message=(
                f"Coverage ratio {coverage_ratio:.1%} with {untested_count} "
                f"untested combination(s) — massive blind spots"
            ),
        )

    return SignalResult(
        signal_name="blind_spot",
        status=SignalStatus.INACTIVE,
        evidence=evidence,
        message=f"No blind spots detected. Coverage: {coverage_ratio:.1%}",
    )


# ── Main Detector ─────────────────────────────────────────────────────────


def check_regime_transition(
    accuracy_history: List[float],
    blind_spot_report: dict,
    *,
    accuracy_with_new: Optional[float] = None,
    accuracy_without_new: Optional[float] = None,
    # Tuning knobs
    saturation_window_k: int = DEFAULT_SATURATION_WINDOW_K,
    saturation_epsilon: float = DEFAULT_SATURATION_EPSILON,
    degradation_threshold: float = DEFAULT_DEGRADATION_THRESHOLD,
    blind_spot_min_runs: int = DEFAULT_BLIND_SPOT_MIN_RUNS,
    # Trigger config
    trigger_threshold: int = 2,  # how many of 3 signals needed
) -> RegimeTransitionDecision:
    """Check whether the system should initiate a regime transition.

    This is the main entry point. It runs all 3 signal detectors and
    applies the trigger rule (default: 2-of-3 signals active → transition).

    Args:
        accuracy_history: chronological accuracy values per iteration.
        blind_spot_report: output from discover_blind_spots().
        accuracy_with_new: accuracy with new component (for degradation signal).
        accuracy_without_new: accuracy without new component (for degradation signal).
        trigger_threshold: how many active signals needed to trigger transition.

    Returns:
        RegimeTransitionDecision with verdict, signals, and recommended actions.
    """
    # Run all 3 detectors
    saturation = detect_saturation(
        accuracy_history,
        window_k=saturation_window_k,
        epsilon=saturation_epsilon,
    )
    degradation = detect_degradation(
        accuracy_with_new,
        accuracy_without_new,
        threshold=degradation_threshold,
    )
    blind_spot = detect_blind_spot(
        blind_spot_report,
        min_runs=blind_spot_min_runs,
    )

    signals = {
        "saturation": saturation,
        "degradation": degradation,
        "blind_spot": blind_spot,
    }

    # Count active signals (excluding insufficient_data)
    active_signals = [
        name for name, sig in signals.items()
        if sig.status == SignalStatus.ACTIVE
    ]
    insufficient_signals = [
        name for name, sig in signals.items()
        if sig.status == SignalStatus.INSUFFICIENT_DATA
    ]

    active_count = len(active_signals)

    # Determine verdict
    if active_count >= trigger_threshold:
        verdict = TransitionVerdict.TRANSITION
        confidence = active_count / 3.0
    elif len(insufficient_signals) == 3:
        verdict = TransitionVerdict.INSUFFICIENT_DATA
        confidence = 0.0
    else:
        verdict = TransitionVerdict.CONTINUE
        confidence = 1.0 - (active_count / 3.0)

    # Recommended actions based on which signals fired
    recommended = _generate_recommendations(active_signals, verdict)

    return RegimeTransitionDecision(
        verdict=verdict,
        signals=signals,
        active_signal_count=active_count,
        confidence=round(confidence, 3),
        recommended_actions=recommended,
        metadata={
            "trigger_threshold": trigger_threshold,
            "insufficient_data_signals": insufficient_signals,
            "accuracy_history_length": len(accuracy_history),
            "latest_accuracy": accuracy_history[-1] if accuracy_history else None,
        },
    )


def _generate_recommendations(
    active_signals: List[str],
    verdict: TransitionVerdict,
) -> List[str]:
    """Generate specific recommended actions based on which signals fired."""
    actions: List[str] = []

    if verdict == TransitionVerdict.TRANSITION:
        actions.append("INITIATE_REGIME_TRANSITION: freeze current schema")

        if "saturation" in active_signals:
            actions.append(
                "Pillar 1 (Concept Formation): build new vocabulary — "
                "current schema has no room for improvement via iteration"
            )

        if "degradation" in active_signals:
            actions.append(
                "Productive Forgetting: remove components that degrade performance — "
                "this matches Wang & Buehler's ΔL_model < 0 observation"
            )

        if "blind_spot" in active_signals:
            actions.append(
                "T-13 (Negative Memory): generate adversarial tests from blind spots — "
                "test coverage is lying about system competence"
            )

        actions.append("H8: re-run self-benchmarking in new regime after transition")
        actions.append("H9: evaluate whether agent identity needs recommitment")

    elif verdict == TransitionVerdict.CONTINUE:
        if "saturation" in active_signals:
            actions.append("Watch: saturation detected but alone — monitor next iteration")
        if "degradation" in active_signals:
            actions.append("Investigate: degradation detected — consider ablation of new component")
        if "blind_spot" in active_signals:
            actions.append("Expand: generate tests for untested regions")

    else:  # INSUFFICIENT_DATA
        actions.append("Collect more data: run additional self-benchmarking cycles")

    return actions
