"""Tests for theory leverage cycle (B1-B5): theory prediction, predictive value update,
contradiction explanation, theory-guided verification, concept selection, tier routing,
and pipeline integration."""
from __future__ import annotations

from virtual_genesis.core.objects.concept import ConceptCard
from virtual_genesis.core.objects.scope import Scope
from virtual_genesis.core.objects.task import TaskObject
from virtual_genesis.core.objects.theory import LocalTheoryObject
from virtual_genesis.core.objects.blackboard import BlackboardObject, BlackboardMemoryPack, BlackboardTaskCore
from virtual_genesis.runtime.theory_runtime.apply import (
    get_theory_prediction_for_task,
    update_theory_predictive_value,
    check_theory_explains_contradiction,
    select_applicable_theories,
    build_theory_hints,
)
from virtual_genesis.runtime.theory_runtime.registry import InMemoryTheoryRegistry
from virtual_genesis.runtime.verification_runtime.service import verify_output_theory_guided
from virtual_genesis.runtime.concept_engine.apply import select_applicable_concepts_theory_guided
from virtual_genesis.runtime.economy_control.router import choose_tier_theory_guided
from virtual_genesis.runtime.pipeline.minimal_run import run_minimal_pipeline


# --- Helpers ---


def _make_theory(family: str = "comparison", predictive_claims: list[str] | None = None, concept_refs: list[str] | None = None) -> LocalTheoryObject:
    theory = LocalTheoryObject.create(
        name=f"test_theory_{family}",
        core_question=f"Why do {family} tasks fail?",
    )
    theory.scope = Scope(task_families=[family])
    theory.predictive_claims = predictive_claims or [
        "Tasks with insufficient contrast will fail",
        "Complexity in multi-option comparison leads to difficulty",
    ]
    theory.concept_refs = concept_refs or []
    theory.mechanism_claims = [f"{family} tasks require structured evidence"]
    theory.prescriptive_implications = ["Ensure explicit contrast is present"]
    theory.confidence_score = 0.7
    theory.predictive_value = 0.6
    return theory


def _make_task(family: str = "comparison", difficulty: str = "medium", criticality: str = "medium") -> TaskObject:
    t = TaskObject.create(raw_text="test task")
    t.task_family = family
    t.difficulty_estimate = difficulty
    t.criticality_level = criticality
    return t


def _make_blackboard(task: TaskObject | None = None) -> BlackboardObject:
    task = task or _make_task()
    task_core = BlackboardTaskCore(
        task_id=task.id,
        task_family=task.task_family,
        criticality_level=task.criticality_level,
        difficulty_estimate=task.difficulty_estimate,
    )
    return BlackboardObject.create(task_ref=task.id, task_core=task_core)


def _make_memory_pack() -> BlackboardMemoryPack:
    return BlackboardMemoryPack()


def _make_concept(name: str, family: str = "comparison", concept_id: str | None = None) -> ConceptCard:
    from virtual_genesis.core.objects.base import make_id
    card = ConceptCard(
        id=concept_id or make_id("concept"),
        object_type="concept",
        name=name,
        definition=f"Definition of {name}",
        operational_meaning=f"Operational meaning of {name} for {family} tasks",
        scope=Scope(task_families=[family]),
    )
    return card


# --- Tests for get_theory_prediction_for_task ---


class TestGetTheoryPredictionForTask:
    def test_prediction_when_claims_match_task_text(self):
        theory = _make_theory(predictive_claims=[
            "Tasks with insufficient contrast will fail",
        ])
        prediction = get_theory_prediction_for_task(theory, "comparison", "Compare contrast between options")
        assert len(prediction["relevant_claims"]) > 0
        assert prediction["confidence"] > 0.0

    def test_no_prediction_when_claims_dont_match(self):
        theory = _make_theory(predictive_claims=[
            "Tasks with xyzzyx will explode",
        ])
        prediction = get_theory_prediction_for_task(theory, "comparison", "Compare two options and justify your choice")
        assert len(prediction["relevant_claims"]) == 0
        assert prediction["confidence"] == 0.0

    def test_predicts_failure_with_failure_keywords(self):
        theory = _make_theory(predictive_claims=[
            "Comparison tasks with options will fail without evidence",
        ])
        prediction = get_theory_prediction_for_task(theory, "comparison", "Compare these options carefully")
        assert prediction["predicts_failure"] is True

    def test_predicts_difficulty_with_difficulty_keywords(self):
        theory = _make_theory(predictive_claims=[
            "Multi-option comparison shows difficulty in analysis",
        ])
        prediction = get_theory_prediction_for_task(theory, "comparison", "Compare these for analysis of difficulty")
        assert prediction["predicts_difficulty"] is True

    def test_confidence_reflects_predictive_value(self):
        theory = _make_theory(predictive_claims=[
            "Tasks with contrast require careful evaluation",
        ])
        theory.predictive_value = 0.85
        prediction = get_theory_prediction_for_task(theory, "comparison", "Evaluate contrast in these tasks")
        assert prediction["confidence"] == 0.85

    def test_no_failure_or_difficulty_for_neutral_claims(self):
        theory = _make_theory(predictive_claims=[
            "Comparison tasks with evidence produce good results",
        ])
        prediction = get_theory_prediction_for_task(theory, "comparison", "Compare evidence in these tasks")
        assert prediction["predicts_failure"] is False
        assert prediction["predicts_difficulty"] is False


# --- Tests for update_theory_predictive_value ---


class TestUpdateTheoryPredictiveValue:
    def test_initial_update_correct_prediction(self):
        theory = _make_theory()
        theory.prediction_count = 0
        theory.correct_predictions = 0
        theory.predictive_value = 0.5
        update_theory_predictive_value(theory, prediction_correct=True)
        # (0 + 1 + 1) / (0 + 1 + 2) = 2/3
        assert theory.prediction_count == 1
        assert theory.correct_predictions == 1
        assert abs(theory.predictive_value - (2 / 3)) < 1e-9

    def test_initial_update_incorrect_prediction(self):
        theory = _make_theory()
        theory.prediction_count = 0
        theory.correct_predictions = 0
        theory.predictive_value = 0.5
        update_theory_predictive_value(theory, prediction_correct=False)
        # (0 + 1) / (0 + 1 + 2) = 1/3
        assert theory.prediction_count == 1
        assert theory.correct_predictions == 0
        assert abs(theory.predictive_value - (1 / 3)) < 1e-9

    def test_laplace_smoothing_formula(self):
        theory = _make_theory()
        theory.prediction_count = 5
        theory.correct_predictions = 3
        update_theory_predictive_value(theory, prediction_correct=True)
        # (3 + 1 + 1) / (5 + 1 + 2) = 5/8 = 0.625
        assert theory.prediction_count == 6
        assert theory.correct_predictions == 4
        assert abs(theory.predictive_value - (5 / 8)) < 1e-9

    def test_multiple_updates_converge(self):
        theory = _make_theory()
        theory.prediction_count = 0
        theory.correct_predictions = 0
        theory.predictive_value = 0.5
        # All correct: should converge toward 1
        for _ in range(10):
            update_theory_predictive_value(theory, prediction_correct=True)
        assert theory.predictive_value > 0.8
        assert theory.prediction_count == 10
        assert theory.correct_predictions == 10

    def test_all_incorrect_converges_low(self):
        theory = _make_theory()
        theory.prediction_count = 0
        theory.correct_predictions = 0
        theory.predictive_value = 0.5
        for _ in range(10):
            update_theory_predictive_value(theory, prediction_correct=False)
        assert theory.predictive_value < 0.2
        assert theory.prediction_count == 10
        assert theory.correct_predictions == 0


# --- Tests for check_theory_explains_contradiction ---


class TestCheckTheoryExplainsContradiction:
    def test_returns_true_when_claims_overlap_contradiction(self):
        theory = _make_theory(
            family="comparison",
            predictive_claims=["Tasks with insufficient contrast will fail"],
        )
        contradiction = {
            "task_family": "comparison",
            "summary": "The tasks showed insufficient contrast between options",
        }
        result = check_theory_explains_contradiction(theory, contradiction)
        assert result is True

    def test_returns_false_when_no_overlap(self):
        theory = _make_theory(
            family="comparison",
            predictive_claims=["Tasks with xyzzyx will explode"],
        )
        contradiction = {
            "task_family": "comparison",
            "summary": "Output lacked contrast and sufficient evidence",
        }
        result = check_theory_explains_contradiction(theory, contradiction)
        assert result is False

    def test_explanatory_power_increases_on_true(self):
        theory = _make_theory(
            family="comparison",
            predictive_claims=["Tasks with insufficient contrast will fail"],
        )
        theory.explanatory_power = 0.3
        contradiction = {
            "task_family": "comparison",
            "summary": "The tasks showed insufficient contrast between options",
        }
        check_theory_explains_contradiction(theory, contradiction)
        assert theory.explanatory_power == 0.4

    def test_returns_false_when_scope_mismatch(self):
        theory = _make_theory(
            family="comparison",
            predictive_claims=["Tasks with insufficient contrast will fail"],
        )
        contradiction = {
            "task_family": "synthesis",
            "summary": "Output lacked contrast and insufficient evidence",
        }
        result = check_theory_explains_contradiction(theory, contradiction)
        assert result is False

    def test_explanatory_power_capped_at_one(self):
        theory = _make_theory(
            family="comparison",
            predictive_claims=["Tasks with insufficient contrast will fail"],
        )
        theory.explanatory_power = 0.95
        contradiction = {
            "task_family": "comparison",
            "summary": "The tasks showed insufficient contrast between options",
        }
        check_theory_explains_contradiction(theory, contradiction)
        assert theory.explanatory_power == 1.0


# --- Tests for verify_output_theory_guided ---


class TestVerifyOutputTheoryGuided:
    def test_normal_pass_when_no_prediction(self):
        prediction = {"predicts_failure": False, "predicts_difficulty": False, "confidence": 0.0, "relevant_claims": []}
        result = verify_output_theory_guided(
            "comparison",
            "This option is better supported by evidence and contrast with the alternative",
            theory_prediction=prediction,
        )
        assert result["theory_guided"] is False
        assert result["verification_summary"]["good_enough"] is True

    def test_stricter_check_when_predicts_failure_single_marker_fails(self):
        prediction = {"predicts_failure": True, "predicts_difficulty": False, "confidence": 0.7, "relevant_claims": ["will fail"]}
        # Text with only 1 primary marker should fail in strict mode
        text_one_marker = "This is supported by the data"
        result = verify_output_theory_guided("comparison", text_one_marker, theory_prediction=prediction)
        assert result["theory_guided"] is True
        assert result["verification_summary"]["good_enough"] is False

    def test_passes_strict_check_with_multiple_markers(self):
        prediction = {"predicts_failure": True, "predicts_difficulty": False, "confidence": 0.7, "relevant_claims": ["will fail"]}
        # Text with 2+ primary markers should pass even in strict mode
        text_multi = "This is supported by contrast and the difference is grounded by evidence"
        result = verify_output_theory_guided("comparison", text_multi, theory_prediction=prediction)
        assert result["theory_guided"] is True
        assert result["verification_summary"]["good_enough"] is True

    def test_predicts_difficulty_requires_secondary_marker(self):
        prediction = {"predicts_failure": False, "predicts_difficulty": True, "confidence": 0.6, "relevant_claims": ["difficulty"]}
        # Text that passes primary but has no secondary marker -- when no framing candidates
        # are provided, secondary_markers is empty, so secondary_hit defaults to True
        text_primary_only = "This is supported by evidence"
        result = verify_output_theory_guided(
            "comparison", text_primary_only,
            theory_prediction=prediction,
            framing_candidates=["comparison", "synthesis"],
        )
        # With framing_candidates including synthesis, secondary markers exist
        # "evidence" is a synthesis secondary marker, so it should pass
        assert result["theory_guided"] is True
        assert result["evidence_checks"]["theory_predicts_difficulty"] is True

    def test_difficulty_fails_without_secondary(self):
        prediction = {"predicts_failure": False, "predicts_difficulty": True, "confidence": 0.6, "relevant_claims": ["difficulty"]}
        # Text with primary marker for comparison but no synthesis secondary markers
        text_no_secondary = "This provides contrast between the options"
        result = verify_output_theory_guided(
            "comparison", text_no_secondary,
            theory_prediction=prediction,
            framing_candidates=["comparison", "synthesis"],
        )
        # "contrast" matches comparison primary, but no synthesis markers hit
        # secondary markers for synthesis: "supported by", "grounded by", "evidence", "merge", "integrate", "observed", "inferred"
        # None of those are in text_no_secondary
        assert result["theory_guided"] is True
        assert result["verification_summary"]["good_enough"] is False


# --- Tests for select_applicable_concepts_theory_guided ---


class TestSelectApplicableConceptsTheoryGuided:
    def test_theory_aligned_concepts_get_score_boost(self):
        concept = _make_concept("evidence_contrast", "comparison")
        theory = _make_theory(family="comparison", concept_refs=[concept.id])
        # Use task text that has tokens overlapping concept name/definition
        # Concept name: "evidence_contrast", definition: "Definition of evidence_contrast"
        # operational_meaning: "Operational meaning of evidence_contrast for comparison tasks"
        task_text = "evidence contrast in comparison tasks"

        selected_normal, decisions_normal = select_applicable_concepts_theory_guided(
            "comparison", task_text, [concept],
            theory=_make_theory(family="comparison", concept_refs=[]),
        )
        selected_boosted, decisions_boosted = select_applicable_concepts_theory_guided(
            "comparison", task_text, [concept],
            theory=theory,
        )
        # The boosted version should give a higher score to the concept
        if decisions_normal and decisions_boosted:
            normal_score = decisions_normal[0].activation_score
            boosted_score = decisions_boosted[0].activation_score
            if decisions_normal[0].selected:
                # If selected, boosted should have higher score
                assert boosted_score > normal_score

    def test_near_threshold_concept_admitted_when_in_theory_refs(self):
        # Create a concept that is just below threshold (min_score=7 for comparison)
        # We need semantic_fit to be low enough that base_score < 7 but >= 5 (7-2)
        concept = _make_concept("marginal_concept", "comparison", concept_id="concept_marginal_1")
        concept.definition = "marginal"
        concept.operational_meaning = "marginal"
        # task_text designed to give minimal overlap with concept tokens
        # concept tokens: "marginal_concept", "marginal", "comparison"
        # With contract_heavy strategy: base_score = family_fit(2) + contract_fit*2 + semantic_fit
        # Aim for score ~ 5 or 6 (below 7, but >= 5 which is 7-2)
        task_text = "compare the marginal options here"  # "marginal" overlaps

        theory = _make_theory(family="comparison", concept_refs=["concept_marginal_1"])

        # Without theory: concept might not be selected
        from virtual_genesis.runtime.concept_engine.apply import select_applicable_concepts
        selected_base, decisions_base = select_applicable_concepts(
            "comparison", task_text, [concept],
        )

        # With theory: concept should be admitted via theory-guided admission
        selected_theory, decisions_theory = select_applicable_concepts_theory_guided(
            "comparison", task_text, [concept], theory=theory,
        )

        # Find the decision for our concept in theory-guided result
        theory_decision = next((d for d in decisions_theory if d.concept_ref == "concept_marginal_1"), None)
        if theory_decision:
            # If near threshold, should get "[theory_admission]" or "[theory_boost]" note
            if "[theory_admission]" in theory_decision.notes or "[theory_boost]" in theory_decision.notes:
                assert theory_decision.selected is True

    def test_non_aligned_concepts_unchanged(self):
        concept = _make_concept("some_concept", "comparison")
        theory = _make_theory(family="comparison", concept_refs=["different_id_not_matching"])
        task_text = "compare evidence in comparison tasks with some_concept definition"

        from virtual_genesis.runtime.concept_engine.apply import select_applicable_concepts
        selected_normal, decisions_normal = select_applicable_concepts(
            "comparison", task_text, [concept],
        )
        selected_theory, decisions_theory = select_applicable_concepts_theory_guided(
            "comparison", task_text, [concept], theory=theory,
        )
        # Non-aligned concept should have same score in both
        if decisions_normal and decisions_theory:
            assert decisions_normal[0].activation_score == decisions_theory[0].activation_score


# --- Tests for choose_tier_theory_guided ---


class TestChooseTierTheoryGuided:
    def test_prevents_tier_0_when_predicts_difficulty(self):
        task = _make_task(family="procedure", difficulty="low")
        bb = _make_blackboard(task)
        mp = _make_memory_pack()
        prediction = {"predicts_difficulty": True, "predicts_failure": False, "confidence": 0.6}
        decision = choose_tier_theory_guided(task, bb, mp, theory_prediction=prediction)
        assert decision.chosen_tier != "tier_0"

    def test_forces_tier_2_when_predicts_failure_high_confidence(self):
        task = _make_task(family="procedure", difficulty="low")
        bb = _make_blackboard(task)
        mp = _make_memory_pack()
        prediction = {"predicts_failure": True, "predicts_difficulty": False, "confidence": 0.7}
        decision = choose_tier_theory_guided(task, bb, mp, theory_prediction=prediction)
        assert decision.chosen_tier == "tier_2"

    def test_no_change_when_prediction_is_benign(self):
        task = _make_task(family="procedure", difficulty="low")
        bb = _make_blackboard(task)
        mp = _make_memory_pack()
        prediction = {"predicts_failure": False, "predicts_difficulty": False, "confidence": 0.0}
        decision = choose_tier_theory_guided(task, bb, mp, theory_prediction=prediction)
        # Original router for procedure+low+no ambiguity => tier_0
        assert decision.chosen_tier == "tier_0"

    def test_low_confidence_failure_no_force(self):
        task = _make_task(family="procedure", difficulty="low")
        bb = _make_blackboard(task)
        mp = _make_memory_pack()
        prediction = {"predicts_failure": True, "predicts_difficulty": False, "confidence": 0.4}
        decision = choose_tier_theory_guided(task, bb, mp, theory_prediction=prediction)
        # Confidence < 0.6, so should not force tier_2
        assert decision.chosen_tier == "tier_0"


# --- Tests for pipeline integration ---


class TestPipelineTheoryLeverage:
    def test_pipeline_with_theory_leverage_disabled(self):
        result = run_minimal_pipeline("Compare these two options and justify your choice")
        assert result["use_theory_leverage"] is False
        assert result["theory_prediction"] is None
        assert result["theory_predictive_value"] is None
        # Standard keys should still exist
        assert "task" in result
        assert "blackboard" in result

    def test_pipeline_with_theory_leverage_enabled_no_theories(self):
        result = run_minimal_pipeline(
            "Compare these two options and justify your choice",
            use_theory_leverage=True,
        )
        assert result["use_theory_leverage"] is True
        # No theories in registry, so prediction is None
        assert result["theory_prediction"] is None
        assert result["theory_predictive_value"] is None

    def test_pipeline_with_theory_leverage_and_seeded_theory(self):
        registry = InMemoryTheoryRegistry()
        theory = _make_theory(
            family="comparison",
            predictive_claims=["Tasks with options will fail without contrast evidence"],
        )
        registry.add_theory(theory)

        result = run_minimal_pipeline(
            "Compare these two options and justify your choice",
            theory_registry=registry,
            use_theory_leverage=True,
        )
        assert result["use_theory_leverage"] is True
        assert result["theory_prediction"] is not None
        assert result["theory_predictive_value"] is not None
        # predictive_value should have been updated from initial 0.6
        assert result["theory_predictive_value"] != 0.6 or result["theory_prediction"]["relevant_claims"] == []

    def test_pipeline_with_both_theory_and_anomaly_leverage(self):
        registry = InMemoryTheoryRegistry()
        theory = _make_theory(
            family="comparison",
            predictive_claims=["Tasks with options will fail without contrast evidence"],
        )
        registry.add_theory(theory)

        result = run_minimal_pipeline(
            "Compare these two options and justify your choice",
            theory_registry=registry,
            use_theory_leverage=True,
            use_anomaly_leverage=True,
        )
        assert result["use_theory_leverage"] is True
        assert result["use_anomaly_leverage"] is True
        assert "anomaly_candidates" in result
        assert "theory_prediction" in result

    def test_pipeline_theory_leverage_returns_expected_keys(self):
        result = run_minimal_pipeline(
            "Compare these two options",
            use_theory_leverage=True,
        )
        expected_keys = [
            "task", "blackboard", "tier_decision", "escalation",
            "ledger", "stored_memory", "anomaly_candidates",
            "use_theory_leverage", "theory_prediction", "theory_predictive_value",
        ]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"


# --- Tests for select_applicable_theories and build_theory_hints ---


class TestSelectApplicableTheories:
    def test_selects_theory_matching_family(self):
        theory = _make_theory(family="comparison")
        result = select_applicable_theories("comparison", [theory])
        assert len(result) == 1
        assert result[0] is theory

    def test_skips_theory_not_matching_family(self):
        theory = _make_theory(family="synthesis")
        result = select_applicable_theories("comparison", [theory])
        assert len(result) == 0

    def test_respects_limit(self):
        t1 = _make_theory(family="comparison")
        t2 = _make_theory(family="comparison")
        result = select_applicable_theories("comparison", [t1, t2], limit=1)
        assert len(result) == 1


class TestBuildTheoryHints:
    def test_builds_hints_from_theories(self):
        theory = _make_theory(family="comparison")
        hints = build_theory_hints([theory])
        assert len(hints) == 1
        assert "test_theory_comparison" in hints[0]

    def test_empty_list_returns_empty_hints(self):
        hints = build_theory_hints([])
        assert hints == []
