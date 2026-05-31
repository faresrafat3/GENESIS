"""Tests for Cycle 1 perturbation operators, extended curriculum, and anti-shortcut benchmark."""
from __future__ import annotations

from virtual_sia.core.objects.task_case import TaskCase
from virtual_sia.eval.perturbations.taskcase_variants import (
    build_curriculum_from_cases,
    build_curriculum_levels,
    contrast_weakening,
    evidence_reordering,
    stronger_shortcut_lures,
    structure_weakening,
    support_removal,
)
from virtual_sia.eval.task_sets.anti_shortcut_benchmark import (
    ANTI_SHORTCUT_BENCHMARK,
    KNOWN_SHORTCUTS,
    generate_anti_shortcut_benchmark,
)
from virtual_sia.eval.task_sets.prototype_v6_cases import (
    PROTOTYPE_V6_CASES,
    build_v6_curriculum,
)
from virtual_sia.eval.reports.perturbation_resistance import (
    generate_perturbation_resistance_report,
)


def _make_sample_case(family: str = "comparison") -> TaskCase:
    """Create a minimal TaskCase for testing perturbation operators."""
    case = TaskCase.create(
        prompt_text="Compare the two options and select the one with the clearest supporting evidence. Make the decisive contrast explicit.",
        expected_primary_family=family,
    )
    case.required_properties = ["explicit comparison", "evidence-backed choice"]
    case.forbidden_shortcuts = ["generic preference without evidence"]
    return case


def _make_synthesis_case() -> TaskCase:
    case = TaskCase.create(
        prompt_text="Produce a grounded synthesis based on the evidence. Separate facts from inferences explicitly.",
        expected_primary_family="synthesis",
    )
    case.required_properties = ["evidence-grounded conclusion", "fact vs inference separation"]
    case.forbidden_shortcuts = ["summary without distinction"]
    return case


def _make_procedure_case() -> TaskCase:
    case = TaskCase.create(
        prompt_text="Extract the required fields and return them in a stable structured layout with normalized ordering and explicit fields.",
        expected_primary_family="procedure",
    )
    case.required_properties = ["stable structured layout"]
    case.forbidden_shortcuts = []
    return case


# --- Tests for support_removal ---

class TestSupportRemoval:
    def test_returns_task_case(self):
        result = support_removal(_make_sample_case())
        assert isinstance(result, TaskCase)

    def test_tag_added(self):
        result = support_removal(_make_sample_case())
        assert "perturb_support_removal" in result.tags

    def test_meta_perturbation_type(self):
        result = support_removal(_make_sample_case())
        assert result.meta["perturbation_type"] == "support_removal"

    def test_prompt_modified(self):
        original = _make_sample_case()
        result = support_removal(original)
        assert result.prompt_text != original.prompt_text

    def test_removes_evidence_phrases(self):
        result = support_removal(_make_sample_case())
        assert "clearest supporting evidence" not in result.prompt_text


# --- Tests for evidence_reordering ---

class TestEvidenceReordering:
    def test_returns_task_case(self):
        result = evidence_reordering(_make_sample_case())
        assert isinstance(result, TaskCase)

    def test_tag_added(self):
        result = evidence_reordering(_make_sample_case())
        assert "perturb_evidence_reordering" in result.tags

    def test_meta_perturbation_type(self):
        result = evidence_reordering(_make_sample_case())
        assert result.meta["perturbation_type"] == "evidence_reordering"

    def test_prompt_modified(self):
        # Need 3+ sentences for reordering to take effect
        case = TaskCase.create(
            prompt_text="First gather the evidence. Then compare both options carefully. Finally select the stronger one. Make the contrast explicit.",
            expected_primary_family="comparison",
        )
        result = evidence_reordering(case)
        assert result.prompt_text != case.prompt_text


# --- Tests for contrast_weakening ---

class TestContrastWeakening:
    def test_returns_task_case(self):
        result = contrast_weakening(_make_sample_case())
        assert isinstance(result, TaskCase)

    def test_tag_added(self):
        result = contrast_weakening(_make_sample_case())
        assert "perturb_contrast_weakening" in result.tags

    def test_meta_perturbation_type(self):
        result = contrast_weakening(_make_sample_case())
        assert result.meta["perturbation_type"] == "contrast_weakening"

    def test_prompt_modified(self):
        original = _make_sample_case()
        result = contrast_weakening(original)
        assert result.prompt_text != original.prompt_text

    def test_weakens_contrast_words(self):
        result = contrast_weakening(_make_sample_case())
        # "clearest" should be replaced with "available"
        assert "clearest" not in result.prompt_text
        # "decisive" should be replaced with "possible"
        assert "decisive" not in result.prompt_text


# --- Tests for structure_weakening ---

class TestStructureWeakening:
    def test_returns_task_case(self):
        result = structure_weakening(_make_procedure_case())
        assert isinstance(result, TaskCase)

    def test_tag_added(self):
        result = structure_weakening(_make_procedure_case())
        assert "perturb_structure_weakening" in result.tags

    def test_meta_perturbation_type(self):
        result = structure_weakening(_make_procedure_case())
        assert result.meta["perturbation_type"] == "structure_weakening"

    def test_prompt_modified(self):
        original = _make_procedure_case()
        result = structure_weakening(original)
        assert result.prompt_text != original.prompt_text

    def test_removes_structure_cues(self):
        result = structure_weakening(_make_procedure_case())
        assert "structured" not in result.prompt_text.lower() or "layout" not in result.prompt_text


# --- Tests for stronger_shortcut_lures ---

class TestStrongerShortcutLures:
    def test_returns_task_case_comparison(self):
        result = stronger_shortcut_lures(_make_sample_case())
        assert isinstance(result, TaskCase)

    def test_tag_added(self):
        result = stronger_shortcut_lures(_make_sample_case())
        assert "perturb_stronger_shortcut_lures" in result.tags

    def test_meta_perturbation_type(self):
        result = stronger_shortcut_lures(_make_sample_case())
        assert result.meta["perturbation_type"] == "stronger_shortcut_lures"

    def test_prompt_modified_comparison(self):
        original = _make_sample_case()
        result = stronger_shortcut_lures(original)
        assert result.prompt_text != original.prompt_text
        assert "gut feeling" in result.prompt_text

    def test_adds_forbidden_shortcuts_comparison(self):
        result = stronger_shortcut_lures(_make_sample_case())
        assert "gut-feeling selection" in result.forbidden_shortcuts

    def test_prompt_modified_synthesis(self):
        original = _make_synthesis_case()
        result = stronger_shortcut_lures(original)
        assert result.prompt_text != original.prompt_text
        assert "summarize loosely" in result.prompt_text

    def test_prompt_modified_procedure(self):
        original = _make_procedure_case()
        result = stronger_shortcut_lures(original)
        assert result.prompt_text != original.prompt_text
        assert "one paragraph" in result.prompt_text


# --- Tests for extended curriculum ---

class TestExtendedCurriculum:
    def test_produces_6_levels(self):
        case = _make_sample_case()
        levels = build_curriculum_levels(case)
        assert len(levels) == 6

    def test_each_level_is_task_case(self):
        case = _make_sample_case()
        levels = build_curriculum_levels(case)
        for level in levels:
            assert isinstance(level, TaskCase)

    def test_levels_have_correct_meta(self):
        case = _make_sample_case()
        levels = build_curriculum_levels(case)
        for i, level in enumerate(levels):
            assert level.meta["curriculum_level"] == i
            assert f"curriculum_level_{i}" in level.tags

    def test_build_curriculum_from_cases_default_limit(self):
        cases = [_make_sample_case(), _make_synthesis_case(), _make_procedure_case()]
        result = build_curriculum_from_cases(cases)
        # Default limit_per_case=6, 3 cases -> 18 variants
        assert len(result) == 18

    def test_build_curriculum_from_cases_custom_limit(self):
        cases = [_make_sample_case()]
        result = build_curriculum_from_cases(cases, limit_per_case=3)
        assert len(result) == 3


# --- Tests for v6 task set ---

class TestPrototypeV6Cases:
    def test_has_at_least_18_cases(self):
        assert len(PROTOTYPE_V6_CASES) >= 18

    def test_has_3_families(self):
        families = {c.expected_primary_family for c in PROTOTYPE_V6_CASES}
        assert "comparison" in families
        assert "synthesis" in families
        assert "procedure" in families

    def test_each_family_has_6_cases(self):
        from collections import Counter
        counts = Counter(c.expected_primary_family for c in PROTOTYPE_V6_CASES)
        assert counts["comparison"] == 6
        assert counts["synthesis"] == 6
        assert counts["procedure"] == 6

    def test_build_v6_curriculum_produces_cases(self):
        curriculum = build_v6_curriculum()
        # 18 cases * 6 levels = 108 curriculum cases
        assert len(curriculum) == 108

    def test_v6_cases_are_harder(self):
        for case in PROTOTYPE_V6_CASES:
            assert case.difficulty_class == "hard"


# --- Tests for anti-shortcut benchmark ---

class TestAntiShortcutBenchmark:
    def test_generates_valid_cases(self):
        cases = generate_anti_shortcut_benchmark()
        assert len(cases) >= 9  # 3 per family minimum

    def test_all_are_task_cases(self):
        for case in ANTI_SHORTCUT_BENCHMARK:
            assert isinstance(case, TaskCase)

    def test_all_have_anti_shortcut_tag(self):
        for case in ANTI_SHORTCUT_BENCHMARK:
            assert "anti_shortcut" in case.tags

    def test_all_have_forbidden_shortcuts(self):
        for case in ANTI_SHORTCUT_BENCHMARK:
            assert len(case.forbidden_shortcuts) > 0

    def test_covers_all_families(self):
        families = {c.expected_primary_family for c in ANTI_SHORTCUT_BENCHMARK}
        assert "comparison" in families
        assert "synthesis" in families
        assert "procedure" in families

    def test_benchmark_meta_has_targeted_shortcut(self):
        for case in ANTI_SHORTCUT_BENCHMARK:
            assert "benchmark_type" in (case.meta or {})
            assert case.meta["benchmark_type"] == "anti_shortcut"

    def test_known_shortcuts_dict_has_entries(self):
        assert len(KNOWN_SHORTCUTS) >= 6


# --- Tests for perturbation_resistance report ---

class TestPerturbationResistanceReport:
    def test_empty_results(self):
        report = generate_perturbation_resistance_report([], None)
        assert report["total_tasks_analyzed"] == 0
        assert report["breaking_point"] is None

    def test_with_mock_results(self):
        # Create minimal mock task results
        mock_results = []
        for level in range(6):
            mock_results.append({
                "task": {"task_family": "comparison", "meta": {"perturbation_type": "lexical_soften", "curriculum_level": level}},
                "blackboard": {"verification_state": {"verification_summary": {"good_enough": level < 4}}},
            })
        report = generate_perturbation_resistance_report(mock_results, None)
        assert report["total_tasks_analyzed"] == 6
        assert "success_rate_by_perturbation_type" in report
        assert "success_rate_by_curriculum_level" in report
        assert "breaking_point" in report
        assert "family_resistance" in report

    def test_breaking_point_detection(self):
        mock_results = []
        # Level 0-2: all pass, Level 3-5: all fail -> breaking_point = 3
        for level in range(6):
            mock_results.append({
                "task": {"task_family": "synthesis", "meta": {"perturbation_type": "none", "curriculum_level": level}},
                "blackboard": {"verification_state": {"verification_summary": {"good_enough": level < 3}}},
            })
        report = generate_perturbation_resistance_report(mock_results, None)
        # Level 3: 0 successes out of 1 -> rate 0.0 < 0.8
        assert report["breaking_point"] == 3
