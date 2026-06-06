"""
Tests for Executable Theories — GENESIS
=========================================
"""

import pytest
from virtual_genesis.runtime.theory_executables.theories import (
    Theory07_PipelineMemoryVsInjection,
    Theory08_FeedbackValueMatrix,
    Theory09_AnticipatoryConcepts,
    Theory10_ReasoningSaturation,
    get_all_executable_theories,
    evaluate_all_theories,
    register_theories_with_falsification_engine,
    Axiom,
    Prediction,
    FalsificationCondition,
    PredictionOutcome,
)


class TestExecutableTheoryBase:
    """Tests for the base ExecutableTheory structure."""

    def evaluate_all_theories_have_required_fields(self):
        for tid, theory in get_all_executable_theories().items():
            assert theory.theory_id == tid
            assert len(theory.name) > 0
            assert len(theory.core_question) > 0
            assert len(theory.description) > 0
            assert len(theory.axioms) > 0
            assert len(theory.predictions) > 0
            assert len(theory.falsification_conditions) > 0

    def evaluate_all_theories_serializable(self):
        for tid, theory in get_all_executable_theories().items():
            d = theory.to_dict()
            assert "theory_id" in d
            assert "axioms" in d
            assert "predictions" in d
            assert d["theory_id"] == tid

    def test_all_predictions_have_ids(self):
        for tid, theory in get_all_executable_theories().items():
            ids = [p.id for p in theory.predictions]
            assert len(ids) == len(set(ids)), f"Duplicate prediction IDs in {tid}"


class TestTheory07:
    """Tests for Theory-07: Pipeline as Memory vs Decision Injection."""

    def setup_method(self):
        self.theory = Theory07_PipelineMemoryVsInjection()

    def test_theory_metadata(self):
        assert self.theory.theory_id == "T07"
        assert len(self.theory.axioms) == 3
        assert len(self.theory.predictions) == 4

    def test_p1_confirmed_when_pipeline_removed(self):
        """run_58 data: standard=65, no_pipeline=70 → +5 improvement."""
        result = self.theory.test({
            "standard_gen1_accuracy": 65.0,
            "no_pipeline_gen1_accuracy": 70.0,
        })
        
        p1_result = next(r for r in result["prediction_results"] if r["prediction_id"] == "T07-P1")
        assert p1_result["outcome"] == PredictionOutcome.CONFIRMED

    def test_p1_refuted_when_pipeline_helps(self):
        """If pipeline helps, P1 should be refuted."""
        result = self.theory.test({
            "standard_gen1_accuracy": 70.0,
            "no_pipeline_gen1_accuracy": 60.0,
        })
        
        p1_result = next(r for r in result["prediction_results"] if r["prediction_id"] == "T07-P1")
        assert p1_result["outcome"] == PredictionOutcome.REFUTED

    def test_p2_chemistry_hurt_more(self):
        result = self.theory.test({
            "physics_delta_without_pipeline": 0,
            "chemistry_delta_without_pipeline": 33.3,  # 16.7% → 50%
        })
        
        p2_result = next(r for r in result["prediction_results"] if r["prediction_id"] == "T07-P2")
        assert p2_result["outcome"] == PredictionOutcome.CONFIRMED

    def test_p3_untested_without_multi_model(self):
        result = self.theory.test({})
        
        p3_result = next(r for r in result["prediction_results"] if r["prediction_id"] == "T07-P3")
        assert p3_result["outcome"] == PredictionOutcome.UNTESTED


class TestTheory08:
    """Tests for Theory-08: Feedback Value Matrix."""

    def setup_method(self):
        self.theory = Theory08_FeedbackValueMatrix()

    def test_theory_metadata(self):
        assert self.theory.theory_id == "T08"
        assert len(self.theory.axioms) == 3
        assert len(self.theory.predictions) == 3

    def test_p1_confirmed_gen2_worse(self):
        """run_57/58 data: Gen2 consistently drops or stays same."""
        result = self.theory.test({
            "gen1_accuracy": 70.0,
            "gen2_accuracy": 60.0,  # 10-point drop
        })
        
        p1_result = next(r for r in result["prediction_results"] if r["prediction_id"] == "T08-P1")
        assert p1_result["outcome"] == PredictionOutcome.CONFIRMED

    def test_p1_refuted_gen2_better(self):
        result = self.theory.test({
            "gen1_accuracy": 60.0,
            "gen2_accuracy": 70.0,
        })
        
        p1_result = next(r for r in result["prediction_results"] if r["prediction_id"] == "T08-P1")
        assert p1_result["outcome"] == PredictionOutcome.REFUTED

    def test_p3_confirmed_with_run58_data(self):
        """run_58 A3: Gen1=70, Gen2=60 → 10-point drop."""
        result = self.theory.test({
            "a3_gen1_accuracy": 70.0,
            "a3_gen2_accuracy": 60.0,
        })
        
        p3_result = next(r for r in result["prediction_results"] if r["prediction_id"] == "T08-P3")
        assert p3_result["outcome"] == PredictionOutcome.CONFIRMED


class TestTheory09:
    """Tests for Theory-09: Anticipatory Concepts."""

    def setup_method(self):
        self.theory = Theory09_AnticipatoryConcepts()

    def test_theory_metadata(self):
        assert self.theory.theory_id == "T09"
        assert len(self.theory.axioms) >= 1
        assert len(self.theory.predictions) >= 1

    def test_p1_chemistry_improves_more(self):
        result = self.theory.test({
            "chemistry_gain_anticipatory": 15.0,
            "physics_gain_anticipatory": 3.0,
        })
        
        p1_result = next(r for r in result["prediction_results"] if r["prediction_id"] == "T09-P1")
        assert p1_result["outcome"] == PredictionOutcome.CONFIRMED


class TestTheory10:
    """Tests for Theory-10: Reasoning Saturation."""

    def setup_method(self):
        self.theory = Theory10_ReasoningSaturation()

    def test_theory_metadata(self):
        assert self.theory.theory_id == "T10"
        assert len(self.theory.axioms) == 4
        assert len(self.theory.predictions) == 5

    def test_p4_confirmed_with_run57_data(self):
        """run_57 data: correct median=989, incorrect median=6836."""
        result = self.theory.test({
            "median_correct_tokens": 989,
            "median_incorrect_tokens": 6836,
        })
        
        p4_result = next(r for r in result["prediction_results"] if r["prediction_id"] == "T10-P4")
        assert p4_result["outcome"] == PredictionOutcome.CONFIRMED

    def test_p4_refuted_if_reversed(self):
        result = self.theory.test({
            "median_correct_tokens": 6836,
            "median_incorrect_tokens": 989,
        })
        
        p4_result = next(r for r in result["prediction_results"] if r["prediction_id"] == "T10-P4")
        assert p4_result["outcome"] == PredictionOutcome.REFUTED

    def test_p1_untested_without_sweep(self):
        result = self.theory.test({})
        p1_result = next(r for r in result["prediction_results"] if r["prediction_id"] == "T10-P1")
        assert p1_result["outcome"] == PredictionOutcome.UNTESTED

    def test_p1_confirmed_at_4k(self):
        result = self.theory.test({
            "accuracy_by_max_tokens": {
                1024: 0.60,
                2048: 0.70,
                4096: 0.80,  # Peak
                8192: 0.75,
                16384: 0.65,
            },
        })
        p1_result = next(r for r in result["prediction_results"] if r["prediction_id"] == "T10-P1")
        assert p1_result["outcome"] == PredictionOutcome.CONFIRMED

    def test_p2_genesis_higher_empty_rate(self):
        result = self.theory.test({
            "genesis_empty_content_rate": 0.40,
            "baseline_empty_content_rate": 0.30,
        })
        p2_result = next(r for r in result["prediction_results"] if r["prediction_id"] == "T10-P2")
        assert p2_result["outcome"] == PredictionOutcome.CONFIRMED


class TestAllTheories:
    """Tests for the unified theory testing interface."""

    def test_get_all_theories(self):
        theories = get_all_executable_theories()
        assert len(theories) == 4
        assert "T07" in theories
        assert "T08" in theories
        assert "T09" in theories
        assert "T10" in theories

    def test_evaluate_all_theories(self):
        evidence = {
            "standard_gen1_accuracy": 65.0,
            "no_pipeline_gen1_accuracy": 70.0,
            "gen1_accuracy": 70.0,
            "gen2_accuracy": 60.0,
            "a3_gen1_accuracy": 70.0,
            "a3_gen2_accuracy": 60.0,
            "median_correct_tokens": 989,
            "median_incorrect_tokens": 6836,
        }
        
        results = evaluate_all_theories(evidence)
        assert len(results) == 4
        
        # T07 should have at least one confirmed prediction
        assert results["T07"]["confirmed"] > 0
        
        # T08 should have P1 and P3 confirmed
        assert results["T08"]["confirmed"] >= 2
        
        # T10 should have P4 confirmed
        assert results["T10"]["confirmed"] >= 1

    def test_register_with_falsification_engine(self):
        from virtual_genesis.runtime.semantic_verifier.verifier import TheoryFalsificationEngine
        
        engine = TheoryFalsificationEngine()
        register_theories_with_falsification_engine(engine)
        
        overview = engine.get_overview()
        assert overview["total_theories"] == 4
        assert overview["total_predictions"] >= 12  # 4+3+2+5 = 14

    def test_paper_locked_evidence(self):
        """Test with the paper's locked empirical values."""
        evidence = {
            # From PROJECT_README.md locked values
            "standard_gen1_accuracy": 65.0,     # run_57 Gen1
            "no_pipeline_gen1_accuracy": 70.0,   # run_58 Gen1
            "gen1_accuracy": 70.0,                # run_58 Gen1 (broad feedback baseline)
            "gen2_accuracy": 60.0,                # run_58 Gen2 (drift!)
            "a3_gen1_accuracy": 70.0,             # run_58 Gen1
            "a3_gen2_accuracy": 60.0,             # run_58 Gen2
            "median_correct_tokens": 989,         # run_57 reasoning analysis
            "median_incorrect_tokens": 6836,      # run_57 reasoning analysis
            "genesis_empty_content_rate": 0.35,   # run_57
            "baseline_empty_content_rate": 0.35,  # run_57 (same baseline)
        }
        
        results = evaluate_all_theories(evidence)
        
        # With paper data, at least these should be confirmed:
        # T07-P1: removing pipeline helped (+5)
        # T08-P1: Gen2 worse than Gen1
        # T08-P3: 10-point drop in A3
        # T10-P4: correct median < incorrect median
        
        total_confirmed = sum(r["confirmed"] for r in results.values())
        assert total_confirmed >= 4, f"Expected >=4 confirmed, got {total_confirmed}"
