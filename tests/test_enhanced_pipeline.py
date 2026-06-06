"""
Tests for Enhanced Pipeline — GENESIS
=======================================
"""

import pytest
from virtual_genesis.runtime.enhanced_pipeline.enhanced_run import run_enhanced_pipeline
from virtual_genesis.eval.task_sets.prototype_v3b_curriculum import PROTOTYPE_V3B_CURRICULUM


def _get_real_task():
    """Get a real task from the curriculum."""
    return PROTOTYPE_V3B_CURRICULUM[0]


class TestEnhancedPipeline:
    """Tests for the enhanced pipeline wrapper."""

    def test_basic_enhanced_run(self):
        """Enhanced pipeline should return base result plus enhancements."""
        task = _get_real_task()
        result = run_enhanced_pipeline(task)
        
        # Base result fields
        assert "task" in result
        assert "blackboard" in result
        assert "tier_decision" in result
        
        # Enhancement flag
        assert result.get("enhanced") is True

    def test_semantic_verification_included(self):
        """Should include semantic verification results."""
        task = _get_real_task()
        result = run_enhanced_pipeline(task, use_semantic_verification=True)
        
        assert "semantic_verification" in result
        sv = result["semantic_verification"]
        assert "verdict" in sv

    def test_value_computation_included(self):
        """Should include value computation results."""
        task = _get_real_task()
        result = run_enhanced_pipeline(task, use_value_computation=True)
        
        assert "value_computation" in result
        vc = result["value_computation"]
        assert "value_functions" in vc
        assert "cognitive_return" in vc
        assert "VoC" in vc["value_functions"]
        assert "VoI" in vc["value_functions"]

    def test_ladder_tracking_included(self):
        """Should track ladder ascent state."""
        task = _get_real_task()
        result = run_enhanced_pipeline(task, use_ladder_tracking=True)
        
        assert "ladder_tracking" in result
        lt = result["ladder_tracking"]
        assert "current_level" in lt
        assert "entropy" in lt
        assert lt["current_level_int"] >= 0

    def test_theory_testing_included(self):
        """Should test executable theories."""
        task = _get_real_task()
        result = run_enhanced_pipeline(task, use_theory_testing=True)
        
        assert "theory_testing" in result
        tt = result["theory_testing"]
        assert "T07" in tt
        assert "T08" in tt
        assert "T10" in tt

    def test_can_disable_all_enhancements(self):
        """Should work with all enhancements disabled (falls back to minimal pipeline)."""
        task = _get_real_task()
        result = run_enhanced_pipeline(
            task,
            use_semantic_verification=False,
            use_value_computation=False,
            use_ladder_tracking=False,
            use_theory_testing=False,
        )
        
        # Should still have base result
        assert "task" in result
        assert result.get("enhanced") is True
        
        # No enhancement data
        assert result.get("semantic_verification") == {}
        assert result.get("value_computation") == {}

    def test_multiple_runs_ladder_advances(self):
        """Running multiple tasks should advance ladder entropy."""
        for i in range(5):
            task = PROTOTYPE_V3B_CURRICULUM[i % len(PROTOTYPE_V3B_CURRICULUM)]
            result = run_enhanced_pipeline(task, use_ladder_tracking=True)
        
        # After 5 runs, should have evidence tracked
        from virtual_genesis.runtime.ladder_ascent.engine import get_ladder_engine
        engine = get_ladder_engine()
        overview = engine.get_system_overview()
        
        # At least one task family should have evidence
        total_evidence = sum(v["total_evidence"] for v in overview.values())
        assert total_evidence >= 5

    def test_cognitive_return_calculation(self):
        """Should calculate ROI for the pipeline run."""
        task = _get_real_task()
        result = run_enhanced_pipeline(task, use_value_computation=True)
        
        cr = result["value_computation"]["cognitive_return"]
        assert "total_return" in cr
        assert "roi" in cr
        assert "worthwhile" in cr

    def test_backward_compatible_with_minimal_pipeline_flags(self):
        """Should support all minimal_pipeline flags."""
        task = _get_real_task()
        result = run_enhanced_pipeline(
            task,
            use_memory=True,
            use_economy=True,
            use_concepts=False,
            use_productive_forgetting=True,
        )
        
        assert "task" in result
        assert "blackboard" in result
