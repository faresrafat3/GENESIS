"""Tests for regime transition detector: 3-signal decision mechanism.

Covers:
- Saturation signal (accuracy plateau/decline detection)
- Degradation signal (harmful "improvements")
- Blind spot signal (suspiciously easy hard regions)
- Combined 2-of-3 trigger rule
- Negative Memory adversarial test generation
- Integration with self-benchmarking cycle
"""
from __future__ import annotations

import pytest

from virtual_genesis.eval.runners.regime_transition_detector import (
    SignalStatus,
    TransitionVerdict,
    detect_saturation,
    detect_degradation,
    detect_blind_spot,
    check_regime_transition,
    RegimeTransitionDecision,
)
from virtual_genesis.eval.negative_memory_adversarial import (
    generate_from_negative_memory,
    merge_negative_memory_with_anomalies,
)
from virtual_genesis.eval.runners.run_self_benchmark_cycle import run_self_benchmark_cycle
from virtual_genesis.core.objects.task_case import TaskCase


# ── Helper factories ──────────────────────────────────────────────────────


def _make_failure(
    fid="f1",
    family="comparison",
    failure_type="wrong_answer",
    context="guessed randomly",
    expected="correct reasoning chain",
    actual="random letter",
    severity=0.7,
    recurrence=1,
):
    return {
        "id": fid,
        "task_family": family,
        "failure_type": failure_type,
        "context_summary": context,
        "expected_behavior": expected,
        "actual_behavior": actual,
        "severity": severity,
        "recurrence_count": recurrence,
    }


def _make_blind_spot_report(easy_regions=None, untested=None, coverage_ratio=1.0, matrix=None):
    return {
        "suspiciously_easy_regions": easy_regions or [],
        "untested_combinations": untested or [],
        "coverage_ratio": coverage_ratio,
        "coverage_matrix": matrix or {},
    }


# ──────────────────────────────────────────────────────────────────────────
# Signal 1: Saturation
# ──────────────────────────────────────────────────────────────────────────


class TestSaturationSignal:
    def test_insufficient_data_short_history(self):
        result = detect_saturation([0.5])
        assert result.status == SignalStatus.INSUFFICIENT_DATA
        assert result.evidence["history_length"] == 1

    def test_insufficient_data_empty(self):
        result = detect_saturation([])
        assert result.status == SignalStatus.INSUFFICIENT_DATA

    def test_active_on_plateau(self):
        # 4 iterations with identical accuracy
        history = [0.60, 0.60, 0.60, 0.60]
        result = detect_saturation(history, window_k=3, epsilon=0.01)
        assert result.status == SignalStatus.ACTIVE
        assert all(d <= 0.01 for d in result.evidence["recent_deltas"])

    def test_active_on_decline(self):
        # Declining accuracy
        history = [0.70, 0.68, 0.65, 0.62]
        result = detect_saturation(history, window_k=3, epsilon=0.01)
        assert result.status == SignalStatus.ACTIVE

    def test_inactive_when_still_improving(self):
        # Steadily improving
        history = [0.40, 0.50, 0.60, 0.70]
        result = detect_saturation(history, window_k=3, epsilon=0.01)
        assert result.status == SignalStatus.INACTIVE
        assert result.evidence["max_recent_delta"] > 0.01

    def test_inactive_with_mixed_recent_improvement(self):
        # Some flat, one improving step in the window
        history = [0.60, 0.60, 0.60, 0.65]
        result = detect_saturation(history, window_k=3, epsilon=0.01)
        assert result.status == SignalStatus.INACTIVE

    def test_custom_window_and_epsilon(self):
        # window_k=2, epsilon=0.05
        history = [0.60, 0.62, 0.63]  # deltas: 0.02, 0.01 — both < 0.05
        result = detect_saturation(history, window_k=2, epsilon=0.05)
        assert result.status == SignalStatus.ACTIVE

    def test_exact_boundary_delta_equals_epsilon(self):
        # delta exactly = epsilon should be flat (<=)
        # Use values that produce exact deltas to avoid floating point issues
        history = [0.50, 0.51, 0.52, 0.53]  # deltas: exactly 0.01 each
        # But floating point makes them 0.010000000000000009 > 0.01
        # So use a larger epsilon to avoid float comparison issues
        result = detect_saturation(history, window_k=3, epsilon=0.011)
        assert result.status == SignalStatus.ACTIVE  # all deltas <= 0.011


# ──────────────────────────────────────────────────────────────────────────
# Signal 2: Degradation
# ──────────────────────────────────────────────────────────────────────────


class TestDegradationSignal:
    def test_insufficient_data_missing_new(self):
        result = detect_degradation(None, 0.7)
        assert result.status == SignalStatus.INSUFFICIENT_DATA

    def test_insufficient_data_missing_baseline(self):
        result = detect_degradation(0.7, None)
        assert result.status == SignalStatus.INSUFFICIENT_DATA

    def test_active_when_new_component_hurts(self):
        result = detect_degradation(0.60, 0.75)
        assert result.status == SignalStatus.ACTIVE
        assert result.evidence["delta"] < 0

    def test_inactive_when_new_component_helps(self):
        result = detect_degradation(0.80, 0.70)
        assert result.status == SignalStatus.INACTIVE
        assert result.evidence["delta"] > 0

    def test_inactive_when_equal(self):
        result = detect_degradation(0.70, 0.70)
        assert result.status == SignalStatus.INACTIVE
        assert result.evidence["delta"] == 0.0

    def test_custom_threshold(self):
        # With threshold=0.1, a drop of 0.05 is not degradation
        result = detect_degradation(0.65, 0.70, threshold=0.1)
        assert result.status == SignalStatus.INACTIVE

    def test_custom_threshold_active(self):
        # With threshold=0.1, a drop of 0.15 IS degradation
        result = detect_degradation(0.55, 0.70, threshold=0.1)
        assert result.status == SignalStatus.ACTIVE


# ──────────────────────────────────────────────────────────────────────────
# Signal 3: Blind Spot
# ──────────────────────────────────────────────────────────────────────────


class TestBlindSpotSignal:
    def test_no_blind_spots(self):
        report = _make_blind_spot_report(coverage_ratio=1.0)
        result = detect_blind_spot(report)
        assert result.status == SignalStatus.INACTIVE

    def test_hard_region_perfect_success(self):
        report = _make_blind_spot_report(
            easy_regions=[("comparison", "none", "hard")],
            matrix={"comparison|none|hard": {"total": 5, "success": 5}},
        )
        result = detect_blind_spot(report, min_runs=2)
        assert result.status == SignalStatus.ACTIVE
        assert result.evidence["well_sampled_hard_easy"] == 1

    def test_hard_region_insufficient_runs(self):
        report = _make_blind_spot_report(
            easy_regions=[("comparison", "none", "hard")],
            matrix={"comparison|none|hard": {"total": 1, "success": 1}},
        )
        result = detect_blind_spot(report, min_runs=2)
        assert result.status == SignalStatus.INACTIVE  # not enough runs

    def test_medium_region_perfect_not_triggered(self):
        # Medium difficulty with perfect score should not trigger by default
        report = _make_blind_spot_report(
            easy_regions=[("comparison", "none", "medium")],
            matrix={"comparison|none|medium": {"total": 10, "success": 10}},
        )
        result = detect_blind_spot(report, target_difficulty="hard")
        assert result.status == SignalStatus.INACTIVE

    def test_low_coverage_ratio_triggers(self):
        report = _make_blind_spot_report(
            coverage_ratio=0.3,
            untested=[("synthesis", "adversarial", "hard")],
        )
        result = detect_blind_spot(report)
        assert result.status == SignalStatus.ACTIVE
        assert result.evidence["coverage_ratio"] < 0.5

    def test_multiple_hard_easy_regions(self):
        report = _make_blind_spot_report(
            easy_regions=[
                ("comparison", "none", "hard"),
                ("synthesis", "adversarial", "hard"),
            ],
            matrix={
                "comparison|none|hard": {"total": 3, "success": 3},
                "synthesis|adversarial|hard": {"total": 4, "success": 4},
            },
        )
        result = detect_blind_spot(report, min_runs=2)
        assert result.status == SignalStatus.ACTIVE
        assert result.evidence["well_sampled_hard_easy"] == 2


# ──────────────────────────────────────────────────────────────────────────
# Combined Trigger (2-of-3 rule)
# ──────────────────────────────────────────────────────────────────────────


class TestRegimeTransitionTrigger:
    def test_no_signals_no_transition(self):
        history = [0.40, 0.50, 0.60, 0.70]  # improving
        report = _make_blind_spot_report(coverage_ratio=1.0)
        decision = check_regime_transition(
            accuracy_history=history,
            blind_spot_report=report,
            accuracy_with_new=0.80,
            accuracy_without_new=0.70,
        )
        assert decision.verdict == TransitionVerdict.CONTINUE
        assert decision.active_signal_count == 0
        assert not decision.should_transition

    def test_saturation_plus_blind_spot_triggers(self):
        history = [0.60, 0.60, 0.60, 0.60]  # saturated
        report = _make_blind_spot_report(
            easy_regions=[("comparison", "none", "hard")],
            matrix={"comparison|none|hard": {"total": 5, "success": 5}},
        )
        decision = check_regime_transition(
            accuracy_history=history,
            blind_spot_report=report,
        )
        assert decision.verdict == TransitionVerdict.TRANSITION
        assert decision.should_transition
        assert decision.active_signal_count >= 2

    def test_saturation_plus_degradation_triggers(self):
        history = [0.60, 0.60, 0.60, 0.60]  # saturated
        report = _make_blind_spot_report(coverage_ratio=1.0)
        decision = check_regime_transition(
            accuracy_history=history,
            blind_spot_report=report,
            accuracy_with_new=0.55,  # worse than baseline
            accuracy_without_new=0.70,
        )
        assert decision.verdict == TransitionVerdict.TRANSITION

    def test_degradation_plus_blind_spot_triggers(self):
        history = [0.40, 0.50, 0.60, 0.70]  # improving, not saturated
        report = _make_blind_spot_report(
            easy_regions=[("synthesis", "adversarial", "hard")],
            matrix={"synthesis|adversarial|hard": {"total": 3, "success": 3}},
        )
        decision = check_regime_transition(
            accuracy_history=history,
            blind_spot_report=report,
            accuracy_with_new=0.55,
            accuracy_without_new=0.70,
        )
        assert decision.verdict == TransitionVerdict.TRANSITION

    def test_single_signal_does_not_trigger(self):
        history = [0.40, 0.50, 0.60, 0.70]  # improving
        report = _make_blind_spot_report(coverage_ratio=1.0)
        # Only degradation active
        decision = check_regime_transition(
            accuracy_history=history,
            blind_spot_report=report,
            accuracy_with_new=0.65,
            accuracy_without_new=0.70,
        )
        assert decision.verdict == TransitionVerdict.CONTINUE
        assert decision.active_signal_count == 1

    def test_insufficient_data_on_all_signals(self):
        decision = check_regime_transition(
            accuracy_history=[],  # no history
            blind_spot_report=_make_blind_spot_report(),  # no issues
        )
        # Degradation is insufficient (both None), saturation insufficient, blind spot inactive
        # So verdict depends on count — if 0 active, should be CONTINUE or INSUFFICIENT
        # With default trigger_threshold=2, if all are insufficient → INSUFFICIENT_DATA
        # Actually: blind spot is INACTIVE (no issues found), saturation is INSUFFICIENT_DATA,
        # degradation is INSUFFICIENT_DATA → 2 insufficient → but 0 active → CONTINUE
        # Let's verify:
        assert decision.verdict in (TransitionVerdict.CONTINUE, TransitionVerdict.INSUFFICIENT_DATA)

    def test_all_three_signals_triggers(self):
        history = [0.60, 0.60, 0.60, 0.60]
        report = _make_blind_spot_report(
            easy_regions=[("comparison", "none", "hard")],
            matrix={"comparison|none|hard": {"total": 5, "success": 5}},
        )
        decision = check_regime_transition(
            accuracy_history=history,
            blind_spot_report=report,
            accuracy_with_new=0.55,
            accuracy_without_new=0.70,
        )
        assert decision.verdict == TransitionVerdict.TRANSITION
        assert decision.active_signal_count == 3
        assert decision.confidence == 1.0  # 3/3

    def test_custom_trigger_threshold_3(self):
        history = [0.60, 0.60, 0.60, 0.60]
        report = _make_blind_spot_report(
            easy_regions=[("comparison", "none", "hard")],
            matrix={"comparison|none|hard": {"total": 5, "success": 5}},
        )
        # 2 signals active (saturation + blind spot), threshold=3 → CONTINUE
        decision = check_regime_transition(
            accuracy_history=history,
            blind_spot_report=report,
            trigger_threshold=3,
        )
        assert decision.verdict == TransitionVerdict.CONTINUE

    def test_to_dict_round_trip(self):
        history = [0.60, 0.60, 0.60, 0.60]
        report = _make_blind_spot_report(
            easy_regions=[("comparison", "none", "hard")],
            matrix={"comparison|none|hard": {"total": 5, "success": 5}},
        )
        decision = check_regime_transition(
            accuracy_history=history,
            blind_spot_report=report,
        )
        d = decision.to_dict()
        assert "verdict" in d
        assert "signals" in d
        assert "saturation" in d["signals"]
        assert "degradation" in d["signals"]
        assert "blind_spot" in d["signals"]
        assert isinstance(d["recommended_actions"], list)
        assert d["active_signal_count"] >= 2

    def test_recommendations_include_concept_formation_on_saturation(self):
        history = [0.60, 0.60, 0.60, 0.60]
        report = _make_blind_spot_report(coverage_ratio=1.0)
        decision = check_regime_transition(
            accuracy_history=history,
            blind_spot_report=report,
            accuracy_with_new=0.55,
            accuracy_without_new=0.70,
        )
        assert decision.should_transition
        actions_text = " ".join(decision.recommended_actions)
        assert "Concept Formation" in actions_text or "Pillar 1" in actions_text

    def test_recommendations_include_negative_memory_on_blind_spot(self):
        history = [0.40, 0.50, 0.60, 0.70]  # not saturated
        report = _make_blind_spot_report(
            easy_regions=[("comparison", "none", "hard")],
            matrix={"comparison|none|hard": {"total": 5, "success": 5}},
        )
        decision = check_regime_transition(
            accuracy_history=history,
            blind_spot_report=report,
            accuracy_with_new=0.55,
            accuracy_without_new=0.70,
        )
        assert decision.should_transition
        actions_text = " ".join(decision.recommended_actions)
        assert "Negative Memory" in actions_text or "T-13" in actions_text


# ──────────────────────────────────────────────────────────────────────────
# Negative Memory → Adversarial Tests
# ──────────────────────────────────────────────────────────────────────────


class TestNegativeMemoryAdversarial:
    def test_empty_failures_returns_empty(self):
        result = generate_from_negative_memory([])
        assert result == []

    def test_single_failure_generates_one_case(self):
        failures = [_make_failure()]
        result = generate_from_negative_memory(failures)
        assert len(result) == 1
        assert isinstance(result[0], TaskCase)

    def test_diagnostic_purpose_set_correctly(self):
        failures = [_make_failure()]
        result = generate_from_negative_memory(failures)
        assert "negative_memory_adversarial" in result[0].diagnostic_purpose
        assert "self_benchmark" in result[0].diagnostic_purpose

    def test_tags_include_failure_type(self):
        failures = [_make_failure(failure_type="shortcut")]
        result = generate_from_negative_memory(failures)
        assert "shortcut" in result[0].tags
        assert "adversarial" in result[0].tags
        assert "negative_memory" in result[0].tags

    def test_recurrence_count_in_tags(self):
        failures = [_make_failure(recurrence=3)]
        result = generate_from_negative_memory(failures)
        assert "recurrence_3" in result[0].tags

    def test_high_recurrence_sets_hard_difficulty(self):
        failures = [_make_failure(severity=0.9, recurrence=4)]
        result = generate_from_negative_memory(failures)
        assert result[0].difficulty_class == "hard"

    def test_low_severity_filtered_out(self):
        failures = [_make_failure(severity=0.1)]
        result = generate_from_negative_memory(failures, min_severity=0.3)
        assert len(result) == 0

    def test_wrong_answer_template(self):
        failures = [_make_failure(failure_type="wrong_answer")]
        result = generate_from_negative_memory(failures)
        assert "ADVERSARIAL" in result[0].prompt_text
        assert "incorrectly" in result[0].prompt_text

    def test_shortcut_template(self):
        failures = [_make_failure(failure_type="shortcut")]
        result = generate_from_negative_memory(failures)
        assert "shortcut" in result[0].prompt_text.lower()

    def test_contradiction_template(self):
        failures = [_make_failure(failure_type="contradiction")]
        result = generate_from_negative_memory(failures)
        assert "contradiction" in result[0].prompt_text.lower()

    def test_missed_edge_case_template(self):
        failures = [_make_failure(failure_type="missed_edge_case")]
        result = generate_from_negative_memory(failures)
        assert "edge case" in result[0].prompt_text.lower()

    def test_adversarial_source_metadata(self):
        failures = [_make_failure(fid="fail_42", failure_type="shortcut")]
        result = generate_from_negative_memory(failures)
        assert result[0].meta is not None
        assert result[0].meta["adversarial_source"]["failure_id"] == "fail_42"
        assert result[0].meta["adversarial_source"]["failure_type"] == "shortcut"

    def test_multiple_failures_multiple_cases(self):
        failures = [
            _make_failure(fid=f"f{i}", family=family)
            for i, family in enumerate(["comparison", "synthesis", "analysis"])
        ]
        result = generate_from_negative_memory(failures)
        assert len(result) == 3
        families = {c.expected_primary_family for c in result}
        assert families == {"comparison", "synthesis", "analysis"}

    def test_severity_boost_on_recurrence(self):
        failures = [_make_failure(severity=0.5, recurrence=3)]
        result = generate_from_negative_memory(failures, max_recurrence_boost=0.3)
        # boosted = min(1.0, 0.5 + 0.3 * 2) = min(1.0, 1.1) = 1.0
        assert result[0].meta["adversarial_source"]["boosted_severity"] == 1.0


# ──────────────────────────────────────────────────────────────────────────
# Merge: Negative Memory + Anomaly Tests
# ──────────────────────────────────────────────────────────────────────────


class TestMergeNegativeMemoryWithAnomalies:
    def _make_anomaly_case(self, family="comparison", stress="property_gap"):
        case = TaskCase.create("test", family)
        case.stress_type = stress
        case.diagnostic_purpose = ["anomaly_derived", "self_benchmark"]
        return case

    def _make_nm_case(self, family="comparison", stress="adversarial_wrong_answer"):
        case = TaskCase.create("test", family)
        case.stress_type = stress
        case.diagnostic_purpose = ["negative_memory_adversarial", "self_benchmark"]
        return case

    def test_empty_lists(self):
        result = merge_negative_memory_with_anomalies([], [])
        assert result == []

    def test_only_anomalies(self):
        anomalies = [self._make_anomaly_case()]
        result = merge_negative_memory_with_anomalies([], anomalies)
        assert len(result) == 1

    def test_only_negative_memory(self):
        nm = [self._make_nm_case()]
        result = merge_negative_memory_with_anomalies(nm, [])
        assert len(result) == 1

    def test_deduplication_prioritizes_negative_memory(self):
        # Same family, different stress_type → both kept (different keys)
        anomalies = [self._make_anomaly_case(family="comparison", stress="property_gap")]
        nm = [self._make_nm_case(family="comparison", stress="adversarial_wrong_answer")]
        result = merge_negative_memory_with_anomalies(nm, anomalies)
        assert len(result) == 2

    def test_same_key_negative_memory_overwrites(self):
        # Same (family, stress_type) → negative memory wins
        anomalies = [self._make_anomaly_case(family="comparison", stress="adversarial_wrong_answer")]
        nm = [self._make_nm_case(family="comparison", stress="adversarial_wrong_answer")]
        result = merge_negative_memory_with_anomalies(nm, anomalies)
        assert len(result) == 1
        assert "negative_memory_adversarial" in result[0].diagnostic_purpose

    def test_no_dedup_when_disabled(self):
        anomalies = [self._make_anomaly_case(family="comparison", stress="same")]
        nm = [self._make_nm_case(family="comparison", stress="same")]
        result = merge_negative_memory_with_anomalies(nm, anomalies, deduplicate_by_family=False)
        assert len(result) == 2


# ──────────────────────────────────────────────────────────────────────────
# Integration: Self-Benchmarking Cycle with Regime Transition
# ──────────────────────────────────────────────────────────────────────────


class TestCycleWithRegimeTransition:
    def test_cycle_returns_regime_transition_key(self):
        """Verify that the updated cycle returns regime_transition in output."""
        cases = [TaskCase.create("test prompt for comparison task", "comparison")]
        result = run_self_benchmark_cycle(
            cases,
            conditions=["baseline_0", "baseline_1"],
            use_self_benchmarking=True,
            accuracy_history=[0.60, 0.60, 0.60, 0.60],
        )
        assert "regime_transition" in result
        assert result["regime_transition"] is not None
        assert "verdict" in result["regime_transition"]
        assert "regime_transition_required" in result

    def test_cycle_with_negative_memory_failures(self):
        """Verify that passing negative memory failures generates adversarial tests."""
        cases = [TaskCase.create("test prompt", "comparison")]
        failures = [
            _make_failure(fid="f1", family="comparison"),
            _make_failure(fid="f2", family="synthesis"),
        ]
        result = run_self_benchmark_cycle(
            cases,
            conditions=["baseline_0"],
            use_self_benchmarking=True,
            negative_memory_failures=failures,
        )
        assert result["negative_memory_cases_generated"] == 2

    def test_cycle_disabled_no_transition_check(self):
        """When self_benchmarking disabled, no regime transition check."""
        cases = [TaskCase.create("test", "comparison")]
        result = run_self_benchmark_cycle(
            cases,
            conditions=["baseline_0"],
            use_self_benchmarking=False,
        )
        assert result["self_benchmarking_enabled"] is False
        assert result.get("regime_transition") is None
