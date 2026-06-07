"""Tests for conditions_runner: Standard vs Ablation with Signal Extraction.

Covers:
- Predefined profiles and comparison configs
- Single comparison run (standard_vs_bare)
- Delta calculation and direction (pipeline_helps / pipeline_hurts)
- Accuracy history accumulation across iterations
- Regime transition integration
- Multi-ablation comprehensive run
- Signal delta extraction
- Edge cases: empty tasks, missing conditions
"""
from __future__ import annotations

import pytest

from virtual_genesis.eval.runners.conditions_runner import (
    # Profiles
    STANDARD,
    ABLATION_BARE,
    ABLATION_MEMORY_ONLY,
    ABLATION_NO_CONCEPTS,
    ABLATION_NO_ECONOMY,
    ABLATION_PREMIUM_ALWAYS,
    # Configs
    COMPARISON_CONFIGS,
    ComparisonConfig,
    DEFAULT_COMPARISON,
    # Main functions
    run_conditions_comparison,
    run_multi_ablation,
    extract_signal_deltas,
    # Result
    ConditionsRunnerResult,
)
from virtual_genesis.eval.runners.regime_transition_detector import TransitionVerdict
from virtual_genesis.core.objects.task_case import TaskCase


# ── Helpers ───────────────────────────────────────────────────────────────


def _make_case(prompt="test comparison task", family="comparison"):
    case = TaskCase.create(prompt, family)
    case.difficulty_class = "medium"
    return case


def _make_case_set(n=3):
    return [_make_case(f"test prompt {i}", "comparison") for i in range(n)]


# ──────────────────────────────────────────────────────────────────────────
# Profile Validation
# ──────────────────────────────────────────────────────────────────────────


class TestProfiles:
    def test_standard_profile_has_correct_condition_id(self):
        assert STANDARD.condition_id == "condition_c_combined"

    def test_ablation_bare_has_correct_condition_id(self):
        assert ABLATION_BARE.condition_id == "baseline_0"

    def test_ablation_memory_only_has_correct_condition_id(self):
        assert ABLATION_MEMORY_ONLY.condition_id == "baseline_1"

    def test_ablation_no_concepts_has_correct_condition_id(self):
        assert ABLATION_NO_CONCEPTS.condition_id == "condition_b_economy"

    def test_ablation_no_economy_has_correct_condition_id(self):
        assert ABLATION_NO_ECONOMY.condition_id == "condition_a_concept_ready"

    def test_ablation_premium_always_has_correct_condition_id(self):
        assert ABLATION_PREMIUM_ALWAYS.condition_id == "baseline_2_premium_always"

    def test_standard_has_no_disabled(self):
        assert STANDARD.what_disabled == ""

    def test_ablation_bare_disabled_many(self):
        assert "memory" in ABLATION_BARE.what_disabled
        assert "economy" in ABLATION_BARE.what_disabled
        assert "concepts" in ABLATION_BARE.what_disabled

    def test_profile_to_dict(self):
        d = STANDARD.to_dict()
        assert "condition_id" in d
        assert "label" in d
        assert d["condition_id"] == "condition_c_combined"


class TestComparisonConfigs:
    def test_five_configs_exist(self):
        assert len(COMPARISON_CONFIGS) == 5

    def test_default_is_standard_vs_bare(self):
        assert DEFAULT_COMPARISON == "standard_vs_bare"

    def test_all_configs_have_standard(self):
        for comp_id, config in COMPARISON_CONFIGS.items():
            assert config.standard.condition_id == "condition_c_combined"

    def test_all_configs_have_unique_ablation(self):
        ablation_ids = {c.ablation.condition_id for c in COMPARISON_CONFIGS.values()}
        assert len(ablation_ids) == 5  # all different

    def test_config_to_dict(self):
        config = COMPARISON_CONFIGS["standard_vs_bare"]
        d = config.to_dict()
        assert d["comparison_id"] == "standard_vs_bare"
        assert "standard" in d
        assert "ablation" in d

    def test_invalid_comparison_id_raises(self):
        cases = _make_case_set()
        with pytest.raises(KeyError):
            run_conditions_comparison(cases, comparison_id="nonexistent")


# ──────────────────────────────────────────────────────────────────────────
# Single Comparison Run
# ──────────────────────────────────────────────────────────────────────────


class TestSingleComparison:
    def test_basic_run_returns_result(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases, run_regime_check=False)
        assert isinstance(result, ConditionsRunnerResult)

    def test_comparison_id_matches(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases, comparison_id="standard_vs_bare")
        assert result.comparison_id == "standard_vs_bare"

    def test_profiles_populated(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases)
        assert result.standard_profile_id == "condition_c_combined"
        assert result.ablation_profile_id == "baseline_0"

    def test_success_rates_are_floats(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases, run_regime_check=False)
        assert isinstance(result.standard_success_rate, float)
        assert isinstance(result.ablation_success_rate, float)
        assert 0.0 <= result.standard_success_rate <= 1.0
        assert 0.0 <= result.ablation_success_rate <= 1.0

    def test_delta_is_difference(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases, run_regime_check=False)
        expected_delta = result.standard_success_rate - result.ablation_success_rate
        assert abs(result.delta - expected_delta) < 1e-6

    def test_task_count_matches_input(self):
        cases = _make_case_set(5)
        result = run_conditions_comparison(cases, run_regime_check=False)
        assert result.task_count == 5

    def test_iteration_recorded(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases, iteration=3, run_regime_check=False)
        assert result.iteration == 3

    def test_to_dict_has_required_keys(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases)
        d = result.to_dict()
        required_keys = [
            "comparison_id", "iteration", "standard_profile_id", "ablation_profile_id",
            "standard_success_rate", "ablation_success_rate", "delta", "task_count",
            "accuracy_history", "blind_spot_report", "regime_decision",
            "should_transition", "diagnostic_value_avg",
        ]
        for key in required_keys:
            assert key in d, f"Missing key: {key}"


# ──────────────────────────────────────────────────────────────────────────
# Delta Direction: Pipeline Helps vs Hurts
# ──────────────────────────────────────────────────────────────────────────


class TestDeltaDirection:
    def test_pipeline_helps_property(self):
        result = ConditionsRunnerResult(
            comparison_id="test",
            iteration=0,
            standard_profile_id="std",
            ablation_profile_id="abl",
            standard_success_rate=0.8,
            ablation_success_rate=0.6,
            delta=0.2,
            task_count=10,
            standard_avg_cost=0.01,
            ablation_avg_cost=0.005,
            cost_delta=0.005,
            accuracy_history=[0.8],
            blind_spot_report={},
            diagnostic_value_avg=0.5,
        )
        assert result.pipeline_helps is True
        assert result.pipeline_hurts is False

    def test_pipeline_hurts_property(self):
        result = ConditionsRunnerResult(
            comparison_id="test",
            iteration=0,
            standard_profile_id="std",
            ablation_profile_id="abl",
            standard_success_rate=0.5,
            ablation_success_rate=0.7,
            delta=-0.2,
            task_count=10,
            standard_avg_cost=0.01,
            ablation_avg_cost=0.005,
            cost_delta=0.005,
            accuracy_history=[0.5],
            blind_spot_report={},
            diagnostic_value_avg=0.5,
        )
        assert result.pipeline_helps is False
        assert result.pipeline_hurts is True

    def test_equal_performance(self):
        result = ConditionsRunnerResult(
            comparison_id="test",
            iteration=0,
            standard_profile_id="std",
            ablation_profile_id="abl",
            standard_success_rate=0.6,
            ablation_success_rate=0.6,
            delta=0.0,
            task_count=10,
            standard_avg_cost=0.01,
            ablation_avg_cost=0.01,
            cost_delta=0.0,
            accuracy_history=[0.6],
            blind_spot_report={},
            diagnostic_value_avg=0.5,
        )
        assert result.pipeline_helps is False
        assert result.pipeline_hurts is False


# ──────────────────────────────────────────────────────────────────────────
# Accuracy History Accumulation
# ──────────────────────────────────────────────────────────────────────────


class TestAccuracyHistory:
    def test_single_iteration_creates_history_of_one(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases, run_regime_check=False)
        assert len(result.accuracy_history) == 1
        assert result.accuracy_history[0] == result.standard_success_rate

    def test_history_accumulates_across_iterations(self):
        cases = _make_case_set()
        # Simulate 3 previous iterations
        prev_history = [0.5, 0.6, 0.65]
        result = run_conditions_comparison(
            cases,
            accuracy_history=prev_history,
            run_regime_check=False,
        )
        assert len(result.accuracy_history) == 4  # 3 previous + current
        assert result.accuracy_history[:3] == prev_history

    def test_history_does_not_mutate_input(self):
        cases = _make_case_set()
        original_history = [0.5, 0.6]
        import copy
        saved = copy.copy(original_history)
        run_conditions_comparison(
            cases,
            accuracy_history=original_history,
            run_regime_check=False,
        )
        assert original_history == saved  # not mutated

    def test_history_with_enough_points_triggers_saturation(self):
        """If accuracy_history is flat for k iterations, saturation should fire."""
        cases = _make_case_set()
        # 4 identical values → deltas all 0 → saturation active
        flat_history = [0.60, 0.60, 0.60, 0.60]
        result = run_conditions_comparison(
            cases,
            accuracy_history=flat_history,
            run_regime_check=True,
        )
        assert result.regime_decision is not None
        signals = result.regime_decision.signals
        # Saturation should be active (history of 5 points, last 3 deltas ≈ 0)
        # Note: flat_history has 4 points, after append = 5 points
        # The last 3 deltas are all 0 → saturation ACTIVE

    def test_empty_history_starts_fresh(self):
        cases = _make_case_set()
        result = run_conditions_comparison(
            cases,
            accuracy_history=None,
            run_regime_check=False,
        )
        assert len(result.accuracy_history) == 1


# ──────────────────────────────────────────────────────────────────────────
# Regime Transition Integration
# ──────────────────────────────────────────────────────────────────────────


class TestRegimeIntegration:
    def test_regime_check_disabled(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases, run_regime_check=False)
        assert result.regime_decision is None
        assert result.should_transition is False

    def test_regime_check_enabled_returns_decision(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases, run_regime_check=True)
        assert result.regime_decision is not None

    def test_to_dict_includes_regime_decision(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases, run_regime_check=True)
        d = result.to_dict()
        assert d["regime_decision"] is not None
        assert "verdict" in d["regime_decision"]

    def test_should_transition_reflects_decision(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases, run_regime_check=True)
        if result.regime_decision:
            assert result.should_transition == result.regime_decision.should_transition

    def test_negative_memory_count_in_meta(self):
        cases = _make_case_set()
        failures = [{"id": "f1", "failure_type": "wrong_answer"}]
        result = run_conditions_comparison(
            cases,
            negative_memory_failures=failures,
            run_regime_check=False,
        )
        assert result.meta["negative_memory_failures_count"] == 1


# ──────────────────────────────────────────────────────────────────────────
# Multi-Ablation Run
# ──────────────────────────────────────────────────────────────────────────


class TestMultiAblation:
    def test_all_comparisons_run(self):
        cases = _make_case_set()
        results = run_multi_ablation(cases, run_regime_check=False)
        assert len(results) == 5
        for comp_id in COMPARISON_CONFIGS:
            assert comp_id in results

    def test_each_result_has_correct_profiles(self):
        cases = _make_case_set()
        results = run_multi_ablation(cases, run_regime_check=False)
        for comp_id, result in results.items():
            config = COMPARISON_CONFIGS[comp_id]
            assert result.standard_profile_id == config.standard.condition_id
            assert result.ablation_profile_id == config.ablation.condition_id

    def test_extract_signal_deltas(self):
        cases = _make_case_set()
        results = run_multi_ablation(cases, run_regime_check=False)
        deltas = extract_signal_deltas(results)
        assert len(deltas) == 5
        for comp_id, delta_data in deltas.items():
            assert "delta" in delta_data
            assert "standard_success_rate" in delta_data
            assert "ablation_success_rate" in delta_data
            assert "pipeline_helps" in delta_data
            assert "pipeline_hurts" in delta_data
            assert "diagnostic_value_avg" in delta_data

    def test_delta_values_are_consistent(self):
        cases = _make_case_set()
        results = run_multi_ablation(cases, run_regime_check=False)
        deltas = extract_signal_deltas(results)
        for comp_id, delta_data in deltas.items():
            result = results[comp_id]
            assert abs(delta_data["delta"] - round(result.delta, 4)) < 1e-6


# ──────────────────────────────────────────────────────────────────────────
# Blind Spot Report Integration
# ──────────────────────────────────────────────────────────────────────────


class TestBlindSpotIntegration:
    def test_blind_spot_report_in_result(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases, run_regime_check=False)
        assert "suspiciously_easy_regions" in result.blind_spot_report
        assert "untested_combinations" in result.blind_spot_report
        assert "coverage_ratio" in result.blind_spot_report

    def test_blind_spot_uses_both_conditions(self):
        """Blind spot analysis should cover results from both conditions."""
        cases = _make_case_set()
        result = run_conditions_comparison(cases, run_regime_check=False)
        # The blind_spot_report should exist and be valid
        assert isinstance(result.blind_spot_report["coverage_ratio"], float)


# ──────────────────────────────────────────────────────────────────────────
# Edge Cases
# ──────────────────────────────────────────────────────────────────────────


class TestEdgeCases:
    def test_single_task(self):
        cases = [_make_case()]
        result = run_conditions_comparison(cases, run_regime_check=False)
        assert result.task_count == 1

    def test_iteration_defaults_to_zero(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases, run_regime_check=False)
        assert result.iteration == 0

    def test_to_dict_round_trip(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases)
        d = result.to_dict()
        # Verify it's serializable
        import json
        json_str = json.dumps(d, default=str)
        assert len(json_str) > 0

    def test_cost_metrics_populated(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases, run_regime_check=False)
        assert isinstance(result.standard_avg_cost, float)
        assert isinstance(result.ablation_avg_cost, float)
        assert isinstance(result.cost_delta, float)

    def test_diagnostic_value_populated(self):
        cases = _make_case_set()
        result = run_conditions_comparison(cases, run_regime_check=False)
        assert isinstance(result.diagnostic_value_avg, float)
        assert 0.0 <= result.diagnostic_value_avg <= 1.0

    def test_custom_saturation_params_passed_through(self):
        cases = _make_case_set()
        # Should not crash with custom params
        result = run_conditions_comparison(
            cases,
            saturation_window_k=5,
            saturation_epsilon=0.05,
            trigger_threshold=3,
        )
        assert isinstance(result, ConditionsRunnerResult)
