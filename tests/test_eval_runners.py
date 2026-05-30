"""Tests for eval runners: CONDITIONS dict, compare_conditions, and summarize_comparison."""
from __future__ import annotations

from virtual_sia.eval.runners.run_condition import CONDITIONS
from virtual_sia.eval.runners.compare_conditions import compare_conditions
from virtual_sia.eval.reports.summary import summarize_comparison


def test_conditions_dict_has_expected_keys():
    """CONDITIONS should contain all 6 expected condition keys."""
    expected_keys = {
        "baseline_0",
        "baseline_1",
        "baseline_2_premium_always",
        "condition_a_concept_ready",
        "condition_b_economy",
        "condition_c_combined",
    }
    assert set(CONDITIONS.keys()) == expected_keys


def test_compare_conditions_returns_dict():
    """compare_conditions with a minimal task list should return a dict keyed by condition_id."""
    tasks = ["Compare these two options", "Summarize the findings"]
    results = compare_conditions(["baseline_0", "baseline_1"], tasks, task_set_ref="test")
    assert isinstance(results, dict)
    assert "baseline_0" in results
    assert "baseline_1" in results


def test_summarize_comparison_thesis_signals():
    """summarize_comparison should produce thesis_signals keys from a results dict."""
    mock_results = {
        "baseline_1": {
            "aggregate_metrics": {"success_rate": 0.5, "avg_estimated_cost": 0.01, "concept_count": 0, "concept_activation_rate": 0.0, "premium_run_count": 0},
            "meta": {"warmup_summary": None},
        },
        "condition_a_concept_ready": {
            "aggregate_metrics": {"success_rate": 0.6, "avg_estimated_cost": 0.01, "concept_count": 2, "concept_activation_rate": 0.3, "premium_run_count": 0},
            "meta": {"warmup_summary": {"warmup_task_count": 2}},
        },
        "baseline_2_premium_always": {
            "aggregate_metrics": {"success_rate": 0.7, "avg_estimated_cost": 0.05, "concept_count": 0, "concept_activation_rate": 0.0, "premium_run_count": 5},
            "meta": {"warmup_summary": None},
        },
        "condition_b_economy": {
            "aggregate_metrics": {"success_rate": 0.6, "avg_estimated_cost": 0.02, "concept_count": 0, "concept_activation_rate": 0.0, "premium_run_count": 2},
            "meta": {"warmup_summary": None},
        },
        "condition_c_combined": {
            "aggregate_metrics": {"success_rate": 0.65, "avg_estimated_cost": 0.03, "concept_count": 3, "concept_activation_rate": 0.4, "premium_run_count": 3},
            "meta": {"warmup_summary": {"warmup_task_count": 2}},
        },
    }
    summary = summarize_comparison(mock_results)
    assert "thesis_signals" in summary
    assert "thesis_1_concept_vs_retrieval" in summary["thesis_signals"]
    assert "thesis_2_economy_vs_premium_always" in summary["thesis_signals"]
    assert "combined_condition" in summary["thesis_signals"]
