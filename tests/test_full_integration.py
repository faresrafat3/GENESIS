"""Tests for full integration: pipeline with all governance flags and integration runner."""
from __future__ import annotations

from virtual_sia.core.objects.identity import AgentIdentityObject
from virtual_sia.runtime.pipeline.minimal_run import run_minimal_pipeline
from virtual_sia.eval.runners.run_full_integration import (
    run_condition_all_flags,
    run_condition_concept_only,
    run_condition_combined_baseline,
)
from virtual_sia.eval.reports.integration_summary import generate_integration_summary_report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_identity() -> AgentIdentityObject:
    return AgentIdentityObject.create(
        commitments=["transparency in reasoning", "accuracy", "cognitive economy"],
        self_model={"capability": "reasoning agent", "limitation": "simulated"},
    )


SIMPLE_TASKS = [
    "Compare these two approaches",
    "Summarize the key findings from the data",
    "Explain the mechanism behind this phenomenon",
]


# ---------------------------------------------------------------------------
# TestFullIntegration
# ---------------------------------------------------------------------------

class TestFullIntegration:
    def test_pipeline_all_flags_no_error(self):
        """Run pipeline with all 5 governance flags True + identity, confirm no exception."""
        identity = _make_identity()
        result = run_minimal_pipeline(
            "Compare these two approaches",
            use_memory=True,
            use_economy=True,
            use_concepts=True,
            use_anomaly_leverage=True,
            use_theory_leverage=True,
            use_productive_forgetting=True,
            use_identity_governance=True,
            use_paradigm_fork=True,
            identity=identity,
        )
        assert isinstance(result, dict)
        assert "task" in result
        assert "blackboard" in result
        assert "ledger" in result

    def test_flags_dont_interfere(self):
        """Run pipeline with all flags, confirm all result keys present."""
        identity = _make_identity()
        result = run_minimal_pipeline(
            "Compare these two approaches",
            use_memory=True,
            use_economy=True,
            use_concepts=True,
            use_anomaly_leverage=True,
            use_theory_leverage=True,
            use_productive_forgetting=True,
            use_identity_governance=True,
            use_paradigm_fork=True,
            identity=identity,
        )
        # All governance-related keys must be present
        assert "alignment_report" in result
        assert "crisis_report" in result
        assert "fork_result" in result
        assert "forgetting_report" in result
        assert "theory_prediction" in result
        assert "anomaly_severity" in result

        # Boolean flags reflected
        assert result["use_anomaly_leverage"] is True
        assert result["use_theory_leverage"] is True
        assert result["use_identity_governance"] is True
        assert result["use_paradigm_fork"] is True

    def test_all_flags_ge_concept_only(self):
        """Run small task set both ways, confirm all-flags success_rate >= concept-only."""
        all_flags = run_condition_all_flags(SIMPLE_TASKS)
        concept_only = run_condition_concept_only(SIMPLE_TASKS)

        all_flags_rate = all_flags["aggregate_metrics"]["success_rate"]
        concept_only_rate = concept_only["aggregate_metrics"]["success_rate"]

        # Why this holds: The deterministic pipeline with simulated reasoning
        # produces identical results for both conditions (both achieve 1.0 on
        # simple tasks), so >= is trivially satisfied. The real value of this
        # test is confirming no regression from adding governance flags -- i.e.,
        # enabling all five governance mechanisms does not degrade the success
        # rate below the concept-only baseline.
        assert all_flags_rate >= concept_only_rate

    def test_integration_runner_returns_valid_payload(self):
        """Test the runner functions return correct payload structure."""
        tasks = SIMPLE_TASKS[:2]

        all_flags = run_condition_all_flags(tasks)
        concept_only = run_condition_concept_only(tasks)
        combined = run_condition_combined_baseline(tasks)

        # Each result has task_results, aggregate_metrics, warmup_summary
        for result in [all_flags, concept_only, combined]:
            assert "task_results" in result
            assert "aggregate_metrics" in result
            assert "warmup_summary" in result
            assert isinstance(result["task_results"], list)
            assert result["aggregate_metrics"]["task_count"] == len(tasks)
            assert 0.0 <= result["aggregate_metrics"]["success_rate"] <= 1.0

        # Integration summary report generates correct keys
        summary = generate_integration_summary_report(
            all_flags_results=all_flags["task_results"],
            concept_only_results=concept_only["task_results"],
            combined_results=combined["task_results"],
        )
        assert "governance_overhead" in summary
        assert "cumulative_benefit" in summary
        assert "interaction_effects" in summary
        assert "per_condition_metrics" in summary
        assert "all_flags_enabled" in summary["per_condition_metrics"]
        assert "concept_only" in summary["per_condition_metrics"]
        assert "combined_baseline" in summary["per_condition_metrics"]
