"""Tests for broader domain cycle: new task families (analysis, extraction, planning),
classification keywords, concept engine config, task set, domain transfer report,
and eval runner."""
from __future__ import annotations

from virtual_genesis.core.objects.task_case import TaskCase
from virtual_genesis.core.ontology.enums import TaskFamily
from virtual_genesis.runtime.task_ingress.service import (
    classify_task_family,
    default_success_criteria,
    ingest_task,
    FAMILY_KEYWORDS,
)
from virtual_genesis.runtime.concept_engine.config import (
    DEFAULT_FAMILY_SELECTIVITY,
    FAMILY_SELECTIVITY_STRATEGY,
)
from virtual_genesis.eval.task_sets.prototype_v7_broader_domain import (
    PROTOTYPE_V7_BROADER_DOMAIN_CASES,
    build_v7_broader_domain_curriculum,
)
from virtual_genesis.eval.reports.domain_transfer import generate_domain_transfer_report
from virtual_genesis.eval.runners.run_broader_domain_eval import run_broader_domain_eval


# --- Tests for TaskFamily enum ---


class TestTaskFamilyEnum:
    def test_enum_has_all_families(self):
        expected = {"comparison", "synthesis", "procedure", "analysis", "extraction", "planning", "unknown"}
        actual = {f.value for f in TaskFamily}
        assert actual == expected

    def test_enum_values_are_strings(self):
        for f in TaskFamily:
            assert isinstance(f.value, str)


# --- Tests for FAMILY_KEYWORDS classification ---


class TestFamilyKeywordsClassification:
    def test_analysis_keywords_present(self):
        assert "analysis" in FAMILY_KEYWORDS
        assert len(FAMILY_KEYWORDS["analysis"]) > 5

    def test_extraction_keywords_present(self):
        assert "extraction" in FAMILY_KEYWORDS
        assert len(FAMILY_KEYWORDS["extraction"]) > 5

    def test_planning_keywords_present(self):
        assert "planning" in FAMILY_KEYWORDS
        assert len(FAMILY_KEYWORDS["planning"]) > 5

    def test_classifies_analysis_text(self):
        text = "diagnose the root cause of the system failure and explain why it happened"
        family, scores, ambiguity, ranked = classify_task_family(text)
        assert family == "analysis"

    def test_classifies_extraction_text(self):
        text = "extract structured data points from the noisy text and tabulate the key information"
        family, scores, ambiguity, ranked = classify_task_family(text)
        assert family == "extraction"

    def test_classifies_planning_text(self):
        text = "plan the steps to complete the migration respecting dependencies and constraints with milestones"
        family, scores, ambiguity, ranked = classify_task_family(text)
        assert family == "planning"

    def test_analysis_arabic_keyword(self):
        text = "تحليل المشكلة وتحديد السبب الرئيسي"
        family, scores, ambiguity, ranked = classify_task_family(text)
        assert "analysis" in ranked

    def test_extraction_arabic_keyword(self):
        text = "استخراج البيانات من النص المختلط"
        family, scores, ambiguity, ranked = classify_task_family(text)
        assert "extraction" in ranked

    def test_planning_arabic_keyword(self):
        text = "تخطيط الخطوات اللازمة لانجاز المهمة"
        family, scores, ambiguity, ranked = classify_task_family(text)
        assert "planning" in ranked


# --- Tests for default_success_criteria ---


class TestDefaultSuccessCriteria:
    def test_analysis_criteria(self):
        criteria = default_success_criteria("analysis")
        assert "causal chain identified" in criteria
        assert "root cause supported by evidence" in criteria

    def test_extraction_criteria(self):
        criteria = default_success_criteria("extraction")
        assert "all fields extracted" in criteria
        assert "structured output valid" in criteria

    def test_planning_criteria(self):
        criteria = default_success_criteria("planning")
        assert "steps sequenced correctly" in criteria
        assert "constraints satisfied" in criteria


# --- Tests for concept engine config ---


class TestConceptEngineConfig:
    def test_family_selectivity_has_analysis(self):
        assert "analysis" in DEFAULT_FAMILY_SELECTIVITY
        assert DEFAULT_FAMILY_SELECTIVITY["analysis"]["max_active"] == 2
        assert DEFAULT_FAMILY_SELECTIVITY["analysis"]["min_score"] == 6

    def test_family_selectivity_has_extraction(self):
        assert "extraction" in DEFAULT_FAMILY_SELECTIVITY
        assert DEFAULT_FAMILY_SELECTIVITY["extraction"]["max_active"] == 1
        assert DEFAULT_FAMILY_SELECTIVITY["extraction"]["min_score"] == 7

    def test_family_selectivity_has_planning(self):
        assert "planning" in DEFAULT_FAMILY_SELECTIVITY
        assert DEFAULT_FAMILY_SELECTIVITY["planning"]["max_active"] == 2
        assert DEFAULT_FAMILY_SELECTIVITY["planning"]["min_score"] == 6

    def test_strategy_has_analysis(self):
        assert FAMILY_SELECTIVITY_STRATEGY["analysis"] == "semantic_balanced"

    def test_strategy_has_extraction(self):
        assert FAMILY_SELECTIVITY_STRATEGY["extraction"] == "contract_heavy"

    def test_strategy_has_planning(self):
        assert FAMILY_SELECTIVITY_STRATEGY["planning"] == "semantic_balanced"


# --- Tests for PROTOTYPE_V7_BROADER_DOMAIN_CASES ---


class TestPrototypeV7Cases:
    def test_case_count_is_18(self):
        assert len(PROTOTYPE_V7_BROADER_DOMAIN_CASES) == 18

    def test_all_are_task_case_objects(self):
        for case in PROTOTYPE_V7_BROADER_DOMAIN_CASES:
            assert isinstance(case, TaskCase)

    def test_analysis_cases_count(self):
        analysis_cases = [c for c in PROTOTYPE_V7_BROADER_DOMAIN_CASES if c.expected_primary_family == "analysis"]
        assert len(analysis_cases) == 6

    def test_extraction_cases_count(self):
        extraction_cases = [c for c in PROTOTYPE_V7_BROADER_DOMAIN_CASES if c.expected_primary_family == "extraction"]
        assert len(extraction_cases) == 6

    def test_planning_cases_count(self):
        planning_cases = [c for c in PROTOTYPE_V7_BROADER_DOMAIN_CASES if c.expected_primary_family == "planning"]
        assert len(planning_cases) == 6

    def test_all_cases_have_required_properties(self):
        for case in PROTOTYPE_V7_BROADER_DOMAIN_CASES:
            assert len(case.required_properties) > 0

    def test_all_cases_have_forbidden_shortcuts(self):
        for case in PROTOTYPE_V7_BROADER_DOMAIN_CASES:
            assert len(case.forbidden_shortcuts) > 0

    def test_all_cases_have_diagnostic_purpose(self):
        for case in PROTOTYPE_V7_BROADER_DOMAIN_CASES:
            assert len(case.diagnostic_purpose) > 0
            assert "domain_transfer" in case.diagnostic_purpose

    def test_all_cases_have_target_thesis(self):
        for case in PROTOTYPE_V7_BROADER_DOMAIN_CASES:
            assert case.target_thesis == ["thesis_1", "thesis_2"]

    def test_curriculum_builds_successfully(self):
        curriculum = build_v7_broader_domain_curriculum()
        assert len(curriculum) > 0
        assert all(isinstance(c, TaskCase) for c in curriculum)


# --- Tests for domain transfer report ---


class TestDomainTransferReport:
    def test_report_structure_empty_results(self):
        report = generate_domain_transfer_report([])
        assert "concept_activation_rate_per_family" in report
        assert "transfer_coefficients" in report
        assert "overall_transfer_rate" in report
        assert "family_pair_transfer_matrix" in report
        assert "new_family_success_rates" in report
        assert "task_count" in report
        assert report["task_count"] == 0

    def test_report_with_mock_results(self):
        mock_results = [
            {
                "task": {"task_family": "analysis"},
                "used_concepts_count": 2,
                "blackboard": {
                    "concept_activations": [
                        {"concept_id": "c1"},
                        {"concept_id": "c2"},
                    ],
                    "verification_state": {"verification_summary": {"good_enough": True}},
                },
            },
            {
                "task": {"task_family": "comparison"},
                "used_concepts_count": 1,
                "blackboard": {
                    "concept_activations": [
                        {"concept_id": "c1"},
                    ],
                    "verification_state": {"verification_summary": {"good_enough": True}},
                },
            },
            {
                "task": {"task_family": "extraction"},
                "used_concepts_count": 1,
                "blackboard": {
                    "concept_activations": [
                        {"concept_id": "c1"},
                    ],
                    "verification_state": {"verification_summary": {"good_enough": False}},
                },
            },
        ]
        report = generate_domain_transfer_report(mock_results)
        assert report["task_count"] == 3
        assert report["concept_activation_rate_per_family"]["analysis"] == 2.0
        assert report["concept_activation_rate_per_family"]["comparison"] == 1.0
        # c1 activated on both comparison (old) and analysis+extraction (new)
        assert len(report["transfer_coefficients"]) == 2  # c1 and c2
        # c1: old=1 (comparison), new=2 (analysis+extraction) -> coeff=2.0
        c1_entry = next(e for e in report["transfer_coefficients"] if e["concept_id"] == "c1")
        assert c1_entry["old_activations"] == 1
        assert c1_entry["new_activations"] == 2
        assert c1_entry["transfer_coefficient"] == 2.0

    def test_report_transfer_matrix(self):
        mock_results = [
            {
                "task": {"task_family": "comparison"},
                "used_concepts_count": 1,
                "blackboard": {
                    "concept_activations": [{"concept_id": "c1"}],
                    "verification_state": {"verification_summary": {"good_enough": True}},
                },
            },
            {
                "task": {"task_family": "analysis"},
                "used_concepts_count": 1,
                "blackboard": {
                    "concept_activations": [{"concept_id": "c1"}],
                    "verification_state": {"verification_summary": {"good_enough": True}},
                },
            },
        ]
        report = generate_domain_transfer_report(mock_results)
        matrix = report["family_pair_transfer_matrix"]
        # c1 activated on comparison AND analysis -> matrix[comparison][analysis] = 1
        assert matrix["comparison"]["analysis"] == 1
        assert matrix["comparison"]["extraction"] == 0
        assert matrix["comparison"]["planning"] == 0

    def test_report_new_family_success_rates(self):
        mock_results = [
            {
                "task": {"task_family": "analysis"},
                "used_concepts_count": 0,
                "blackboard": {
                    "concept_activations": [],
                    "verification_state": {"verification_summary": {"good_enough": True}},
                },
            },
            {
                "task": {"task_family": "analysis"},
                "used_concepts_count": 0,
                "blackboard": {
                    "concept_activations": [],
                    "verification_state": {"verification_summary": {"good_enough": False}},
                },
            },
        ]
        report = generate_domain_transfer_report(mock_results)
        assert report["new_family_success_rates"]["analysis"] == 0.5

    def test_report_custom_families(self):
        report = generate_domain_transfer_report(
            [],
            original_families=["comparison"],
            new_families=["analysis"],
        )
        matrix = report["family_pair_transfer_matrix"]
        assert "comparison" in matrix
        assert "analysis" in matrix["comparison"]


# --- Tests for eval runner ---


class TestBroaderDomainEvalRunner:
    def test_runner_is_callable(self):
        assert callable(run_broader_domain_eval)

    def test_runner_executes_and_returns_expected_keys(self):
        result = run_broader_domain_eval(output_path="/tmp/test_broader_domain_summary.json")
        expected_keys = [
            "task_count",
            "curriculum_count",
            "conditions",
            "classification_report",
            "summary_base",
            "summary_curriculum",
            "perturbation_resistance",
            "domain_transfer",
            "raw_results_base",
            "raw_results_curriculum",
        ]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"
        assert result["task_count"] == 18
        assert result["curriculum_count"] > 0
        assert "overall_transfer_rate" in result["domain_transfer"]
