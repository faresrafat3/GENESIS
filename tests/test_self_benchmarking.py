"""Tests for self-benchmarking system: benchmark generation from anomaly candidates,
blind spot discovery, diagnostic value metrics, and the self-benchmark cycle runner."""
from __future__ import annotations

from virtual_genesis.core.objects.task_case import TaskCase
from virtual_genesis.eval.benchmark_generator import generate_from_anomaly_candidates
from virtual_genesis.eval.reports.blind_spot_discovery import discover_blind_spots
from virtual_genesis.eval.reports.diagnostic_value import (
    compute_diagnostic_value,
    compute_diagnostic_value_report,
)
from virtual_genesis.eval.runners.run_self_benchmark_cycle import run_self_benchmark_cycle


# --- Helper factories ---


def _make_anomaly(source_type="property_gap", summary="test anomaly", severity=0.5, task_family="comparison"):
    return {
        "source_type": source_type,
        "summary": summary,
        "severity": severity,
        "task_family": task_family,
    }


def _make_result(task_family="comparison", good_enough=True, stress_type=None, diagnostic_purpose=None, difficulty_class="medium", task_id="task_1", anomaly_candidates=None):
    task = {
        "id": task_id,
        "task_family": task_family,
        "difficulty_class": difficulty_class,
        "stress_type": stress_type,
        "diagnostic_purpose": diagnostic_purpose or [],
    }
    return {
        "task": task,
        "blackboard": {
            "verification_state": {
                "verification_summary": {"good_enough": good_enough},
            },
        },
        "anomaly_candidates": anomaly_candidates or [],
    }


def _make_task_case(family="comparison", stress_type=None, diagnostic_purpose=None, difficulty_class="medium"):
    case = TaskCase.create(prompt_text="test prompt", expected_primary_family=family)
    case.difficulty_class = difficulty_class
    case.stress_type = stress_type
    case.diagnostic_purpose = diagnostic_purpose or []
    return case


# --- Tests for benchmark_generator ---


class TestBenchmarkGenerator:
    def test_empty_input_returns_empty_list(self):
        result = generate_from_anomaly_candidates([])
        assert result == []

    def test_single_anomaly_returns_one_task_case(self):
        anomalies = [_make_anomaly()]
        result = generate_from_anomaly_candidates(anomalies)
        assert len(result) == 1
        assert isinstance(result[0], TaskCase)

    def test_multiple_anomalies_returns_multiple_cases(self):
        anomalies = [_make_anomaly(), _make_anomaly(source_type="shortcut_pattern"), _make_anomaly(source_type="contradiction_pattern")]
        result = generate_from_anomaly_candidates(anomalies)
        assert len(result) == 3

    def test_diagnostic_purpose_set_correctly(self):
        anomalies = [_make_anomaly()]
        result = generate_from_anomaly_candidates(anomalies)
        assert result[0].diagnostic_purpose == ["anomaly_derived", "self_benchmark"]

    def test_tags_include_source_type(self):
        anomalies = [_make_anomaly(source_type="shortcut_pattern")]
        result = generate_from_anomaly_candidates(anomalies)
        assert "shortcut_pattern" in result[0].tags

    def test_tags_include_auto_generated(self):
        anomalies = [_make_anomaly()]
        result = generate_from_anomaly_candidates(anomalies)
        assert "auto_generated" in result[0].tags

    def test_high_severity_sets_hard_difficulty(self):
        anomalies = [_make_anomaly(severity=0.8)]
        result = generate_from_anomaly_candidates(anomalies)
        assert result[0].difficulty_class == "hard"

    def test_low_severity_sets_medium_difficulty(self):
        anomalies = [_make_anomaly(severity=0.3)]
        result = generate_from_anomaly_candidates(anomalies)
        assert result[0].difficulty_class == "medium"

    def test_boundary_severity_0_7_sets_hard(self):
        anomalies = [_make_anomaly(severity=0.7)]
        result = generate_from_anomaly_candidates(anomalies)
        assert result[0].difficulty_class == "hard"

    def test_expected_primary_family_from_anomaly(self):
        anomalies = [_make_anomaly(task_family="synthesis")]
        result = generate_from_anomaly_candidates(anomalies)
        assert result[0].expected_primary_family == "synthesis"

    def test_prompt_text_contains_family(self):
        anomalies = [_make_anomaly(task_family="analysis")]
        result = generate_from_anomaly_candidates(anomalies)
        assert "analysis" in result[0].prompt_text

    def test_prompt_text_contains_summary(self):
        anomalies = [_make_anomaly(summary="memory retrieval failed")]
        result = generate_from_anomaly_candidates(anomalies)
        assert "memory retrieval failed" in result[0].prompt_text

    def test_property_gap_source_type_prompt(self):
        anomalies = [_make_anomaly(source_type="property_gap")]
        result = generate_from_anomaly_candidates(anomalies)
        assert "required properties" in result[0].prompt_text

    def test_shortcut_pattern_source_type_prompt(self):
        anomalies = [_make_anomaly(source_type="shortcut_pattern")]
        result = generate_from_anomaly_candidates(anomalies)
        assert "forbidden shortcuts" in result[0].prompt_text

    def test_contradiction_pattern_source_type_prompt(self):
        anomalies = [_make_anomaly(source_type="contradiction_pattern")]
        result = generate_from_anomaly_candidates(anomalies)
        assert "contradictions" in result[0].prompt_text

    def test_unknown_source_type_uses_default_prompt(self):
        anomalies = [_make_anomaly(source_type="totally_new_type")]
        result = generate_from_anomaly_candidates(anomalies)
        assert "anomaly scenario" in result[0].prompt_text


# --- Tests for blind_spot_discovery ---


class TestBlindSpotDiscovery:
    def test_empty_inputs(self):
        report = discover_blind_spots([], [])
        assert report["untested_combinations"] == []
        assert report["suspiciously_easy_regions"] == []
        assert report["coverage_ratio"] == 1.0  # 0/0 edge case handled

    def test_untested_combinations_detected(self):
        cases = [
            _make_task_case(family="comparison", diagnostic_purpose=["test_a"]),
            _make_task_case(family="synthesis", diagnostic_purpose=["test_b"]),
        ]
        results = [
            _make_result(task_family="comparison", diagnostic_purpose=["test_a"]),
        ]
        report = discover_blind_spots(results, cases)
        assert len(report["untested_combinations"]) > 0
        # synthesis|test_b|medium should be untested
        untested_families = [combo[0] for combo in report["untested_combinations"]]
        assert "synthesis" in untested_families

    def test_suspiciously_easy_regions_detected(self):
        results = [
            _make_result(task_family="comparison", good_enough=True, task_id="t1"),
            _make_result(task_family="comparison", good_enough=True, task_id="t2"),
            _make_result(task_family="comparison", good_enough=True, task_id="t3"),
        ]
        report = discover_blind_spots(results, [])
        assert len(report["suspiciously_easy_regions"]) >= 1

    def test_mixed_results_not_suspiciously_easy(self):
        results = [
            _make_result(task_family="comparison", good_enough=True, task_id="t1"),
            _make_result(task_family="comparison", good_enough=False, task_id="t2"),
        ]
        report = discover_blind_spots(results, [])
        # comparison with mixed results should NOT be in suspiciously_easy
        easy_families = [combo[0] for combo in report["suspiciously_easy_regions"]]
        assert "comparison" not in easy_families

    def test_coverage_ratio_full_coverage(self):
        cases = [_make_task_case(family="comparison", diagnostic_purpose=["diag"])]
        results = [_make_result(task_family="comparison", diagnostic_purpose=["diag"])]
        report = discover_blind_spots(results, cases)
        assert report["coverage_ratio"] == 1.0

    def test_coverage_ratio_partial_coverage(self):
        cases = [
            _make_task_case(family="comparison", diagnostic_purpose=["a"]),
            _make_task_case(family="synthesis", diagnostic_purpose=["b"]),
        ]
        results = [_make_result(task_family="comparison", diagnostic_purpose=["a"])]
        report = discover_blind_spots(results, cases)
        assert report["coverage_ratio"] == 0.5

    def test_coverage_matrix_has_stats(self):
        results = [
            _make_result(task_family="comparison", good_enough=True, task_id="t1"),
            _make_result(task_family="comparison", good_enough=False, task_id="t2"),
        ]
        report = discover_blind_spots(results, [])
        assert len(report["coverage_matrix"]) > 0
        # Check the matrix entry has total and success fields
        for key, stats in report["coverage_matrix"].items():
            assert "total" in stats
            assert "success" in stats


# --- Tests for diagnostic_value ---


class TestDiagnosticValue:
    def test_all_same_true_returns_zero(self):
        results = {"cond_a": True, "cond_b": True, "cond_c": True}
        assert compute_diagnostic_value(results) == 0.0

    def test_all_same_false_returns_zero(self):
        results = {"cond_a": False, "cond_b": False, "cond_c": False}
        assert compute_diagnostic_value(results) == 0.0

    def test_mixed_results_returns_positive(self):
        results = {"cond_a": True, "cond_b": False}
        value = compute_diagnostic_value(results)
        assert value > 0.0

    def test_perfect_split_returns_one(self):
        results = {"cond_a": True, "cond_b": False}
        value = compute_diagnostic_value(results)
        assert value == 1.0

    def test_mostly_same_returns_low_value(self):
        results = {"a": True, "b": True, "c": True, "d": False}
        value = compute_diagnostic_value(results)
        assert 0.0 < value < 1.0

    def test_empty_input_returns_zero(self):
        assert compute_diagnostic_value({}) == 0.0

    def test_single_condition_returns_zero(self):
        assert compute_diagnostic_value({"only": True}) == 0.0


class TestDiagnosticValueReport:
    def test_report_structure(self):
        results_by_condition = {
            "cond_a": [_make_result(task_id="case_1", good_enough=True)],
            "cond_b": [_make_result(task_id="case_1", good_enough=False)],
        }
        report = compute_diagnostic_value_report(results_by_condition)
        assert "case_diagnostic_values" in report
        assert "avg_diagnostic_value" in report
        assert "low_value_cases" in report
        assert "high_value_cases" in report

    def test_high_value_case_detected(self):
        results_by_condition = {
            "cond_a": [_make_result(task_id="case_1", good_enough=True)],
            "cond_b": [_make_result(task_id="case_1", good_enough=False)],
        }
        report = compute_diagnostic_value_report(results_by_condition)
        assert "case_1" in report["high_value_cases"]

    def test_low_value_case_detected(self):
        results_by_condition = {
            "cond_a": [_make_result(task_id="case_1", good_enough=True)],
            "cond_b": [_make_result(task_id="case_1", good_enough=True)],
            "cond_c": [_make_result(task_id="case_1", good_enough=True)],
        }
        report = compute_diagnostic_value_report(results_by_condition)
        assert "case_1" in report["low_value_cases"]

    def test_empty_results(self):
        report = compute_diagnostic_value_report({})
        assert report["case_diagnostic_values"] == {}
        assert report["avg_diagnostic_value"] == 0.0
        assert report["low_value_cases"] == []
        assert report["high_value_cases"] == []

    def test_multiple_cases(self):
        results_by_condition = {
            "cond_a": [
                _make_result(task_id="case_1", good_enough=True),
                _make_result(task_id="case_2", good_enough=True),
            ],
            "cond_b": [
                _make_result(task_id="case_1", good_enough=False),
                _make_result(task_id="case_2", good_enough=True),
            ],
        }
        report = compute_diagnostic_value_report(results_by_condition)
        assert len(report["case_diagnostic_values"]) == 2
        # case_1 has high diagnostic value (different results)
        assert report["case_diagnostic_values"]["case_1"] > 0.8
        # case_2 has low diagnostic value (same results)
        assert report["case_diagnostic_values"]["case_2"] < 0.2


# --- Tests for run_self_benchmark_cycle ---


class TestRunSelfBenchmarkCycle:
    def test_disabled_self_benchmarking(self):
        cases = [TaskCase.create("test prompt", "comparison")]
        result = run_self_benchmark_cycle(cases, conditions=["baseline_0"], use_self_benchmarking=False)
        assert result["self_benchmarking_enabled"] is False
        assert "base_results" in result

    def test_enabled_self_benchmarking(self):
        cases = [TaskCase.create("test prompt for comparison task", "comparison")]
        result = run_self_benchmark_cycle(cases, conditions=["baseline_0", "baseline_1"], use_self_benchmarking=True)
        assert result["self_benchmarking_enabled"] is True
        assert "base_results" in result
        assert "anomaly_report" in result
        assert "blind_spot_report" in result
        assert "diagnostic_report" in result
        assert "new_cases_generated" in result

    def test_cycle_returns_anomaly_candidates_count(self):
        cases = [TaskCase.create("compare these items carefully", "comparison")]
        result = run_self_benchmark_cycle(cases, conditions=["baseline_0"], use_self_benchmarking=True)
        assert "anomaly_candidates_count" in result
        assert isinstance(result["anomaly_candidates_count"], int)

    def test_cycle_returns_diagnostic_report(self):
        cases = [TaskCase.create("synthesize the information", "synthesis")]
        result = run_self_benchmark_cycle(cases, conditions=["baseline_0"], use_self_benchmarking=True)
        diag = result["diagnostic_report"]
        assert "case_diagnostic_values" in diag
        assert "avg_diagnostic_value" in diag
