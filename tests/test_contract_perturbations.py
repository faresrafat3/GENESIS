"""Tests for contract-level perturbation operators and curriculum integration."""
from __future__ import annotations

from virtual_sia.core.objects.task_case import TaskCase
from virtual_sia.eval.perturbations.contract_perturbations import (
    contract_flip,
    contract_tightening_strict,
    counterfactual_contract,
    property_addition,
    property_removal,
    shortcut_injection,
)
from virtual_sia.eval.perturbations.taskcase_variants import (
    build_curriculum_from_cases,
    build_curriculum_levels,
)


def _make_comparison_case() -> TaskCase:
    """Create a minimal comparison TaskCase for testing."""
    case = TaskCase.create(
        prompt_text="Compare the two options and select the one with the clearest supporting evidence.",
        expected_primary_family="comparison",
    )
    case.required_properties = ["explicit comparison", "evidence-backed choice"]
    case.forbidden_shortcuts = ["generic preference without evidence"]
    return case


def _make_synthesis_case() -> TaskCase:
    """Create a minimal synthesis TaskCase for testing."""
    case = TaskCase.create(
        prompt_text="Produce a grounded synthesis based on the evidence.",
        expected_primary_family="synthesis",
    )
    case.required_properties = ["evidence-grounded conclusion", "fact vs inference separation"]
    case.forbidden_shortcuts = ["summary without distinction"]
    return case


def _make_procedure_case() -> TaskCase:
    """Create a minimal procedure TaskCase for testing."""
    case = TaskCase.create(
        prompt_text="Extract the required fields and return them in a stable structured layout.",
        expected_primary_family="procedure",
    )
    case.required_properties = ["stable structured layout", "reusable field ordering"]
    case.forbidden_shortcuts = ["unstructured dump"]
    return case


# --- Tests for property_addition ---


class TestPropertyAddition:
    def test_returns_task_case(self):
        result = property_addition(_make_comparison_case())
        assert isinstance(result, TaskCase)

    def test_tag_added(self):
        result = property_addition(_make_comparison_case())
        assert "perturb_property_addition" in result.tags

    def test_meta_perturbation_type(self):
        result = property_addition(_make_comparison_case())
        assert result.meta["perturbation_type"] == "property_addition"

    def test_adds_property_comparison(self):
        original = _make_comparison_case()
        result = property_addition(original)
        assert len(result.required_properties) == len(original.required_properties) + 1
        assert "quantitative cost-benefit ratio" in result.required_properties

    def test_adds_property_synthesis(self):
        result = property_addition(_make_synthesis_case())
        assert "temporal ordering of evidence" in result.required_properties

    def test_adds_property_procedure(self):
        result = property_addition(_make_procedure_case())
        assert "rollback instructions for each step" in result.required_properties

    def test_does_not_duplicate_property(self):
        case = _make_comparison_case()
        case.required_properties.append("quantitative cost-benefit ratio")
        original_len = len(case.required_properties)
        result = property_addition(case)
        assert len(result.required_properties) == original_len

    def test_unknown_family_gets_default(self):
        case = TaskCase.create(prompt_text="Test", expected_primary_family="custom_family")
        case.required_properties = ["some prop"]
        result = property_addition(case)
        assert "meta-cognitive reflection on reasoning process" in result.required_properties


# --- Tests for property_removal ---


class TestPropertyRemoval:
    def test_returns_task_case(self):
        result = property_removal(_make_comparison_case())
        assert isinstance(result, TaskCase)

    def test_tag_added(self):
        result = property_removal(_make_comparison_case())
        assert "perturb_property_removal" in result.tags

    def test_meta_perturbation_type(self):
        result = property_removal(_make_comparison_case())
        assert result.meta["perturbation_type"] == "property_removal"

    def test_removes_last_property(self):
        original = _make_comparison_case()
        result = property_removal(original)
        assert len(result.required_properties) == len(original.required_properties) - 1

    def test_empty_properties_stays_empty(self):
        case = TaskCase.create(prompt_text="Test", expected_primary_family="comparison")
        case.required_properties = []
        result = property_removal(case)
        assert result.required_properties == []


# --- Tests for shortcut_injection ---


class TestShortcutInjection:
    def test_returns_task_case(self):
        result = shortcut_injection(_make_comparison_case())
        assert isinstance(result, TaskCase)

    def test_tag_added(self):
        result = shortcut_injection(_make_comparison_case())
        assert "perturb_shortcut_injection" in result.tags

    def test_meta_perturbation_type(self):
        result = shortcut_injection(_make_comparison_case())
        assert result.meta["perturbation_type"] == "shortcut_injection"

    def test_adds_shortcut_comparison(self):
        result = shortcut_injection(_make_comparison_case())
        assert "formulaic comparison structure" in result.forbidden_shortcuts

    def test_adds_shortcut_synthesis(self):
        result = shortcut_injection(_make_synthesis_case())
        assert "bullet-point listing without narrative" in result.forbidden_shortcuts

    def test_adds_shortcut_procedure(self):
        result = shortcut_injection(_make_procedure_case())
        assert "generic step numbering without context" in result.forbidden_shortcuts

    def test_does_not_duplicate_shortcut(self):
        case = _make_comparison_case()
        case.forbidden_shortcuts.append("formulaic comparison structure")
        original_len = len(case.forbidden_shortcuts)
        result = shortcut_injection(case)
        assert len(result.forbidden_shortcuts) == original_len


# --- Tests for contract_flip ---


class TestContractFlip:
    def test_returns_task_case(self):
        result = contract_flip(_make_comparison_case())
        assert isinstance(result, TaskCase)

    def test_tag_added(self):
        result = contract_flip(_make_comparison_case())
        assert "perturb_contract_flip" in result.tags

    def test_meta_perturbation_type(self):
        result = contract_flip(_make_comparison_case())
        assert result.meta["perturbation_type"] == "contract_flip"

    def test_moves_property_to_shortcuts(self):
        original = _make_comparison_case()
        first_prop = original.required_properties[0]
        result = contract_flip(original)
        assert first_prop not in result.required_properties
        assert first_prop in result.forbidden_shortcuts

    def test_moves_shortcut_to_properties(self):
        case = _make_comparison_case()
        # Ensure there's more than 1 forbidden_shortcut after the flip adds one
        case.forbidden_shortcuts = ["shortcut_a", "shortcut_b"]
        result = contract_flip(case)
        # The first original shortcut should have moved to properties
        assert "shortcut_a" in result.required_properties

    def test_empty_properties_no_crash(self):
        case = TaskCase.create(prompt_text="Test", expected_primary_family="comparison")
        case.required_properties = []
        case.forbidden_shortcuts = ["some shortcut"]
        result = contract_flip(case)
        assert isinstance(result, TaskCase)


# --- Tests for contract_tightening_strict ---


class TestContractTighteningStrict:
    def test_returns_task_case(self):
        result = contract_tightening_strict(_make_comparison_case())
        assert isinstance(result, TaskCase)

    def test_tag_added(self):
        result = contract_tightening_strict(_make_comparison_case())
        assert "perturb_contract_tightening_strict" in result.tags

    def test_meta_perturbation_type(self):
        result = contract_tightening_strict(_make_comparison_case())
        assert result.meta["perturbation_type"] == "contract_tightening_strict"

    def test_strict_mode_meta(self):
        result = contract_tightening_strict(_make_comparison_case())
        assert result.meta["strict_mode"] is True

    def test_evaluation_notes_set(self):
        result = contract_tightening_strict(_make_comparison_case())
        assert "STRICT" in result.evaluation_notes
        assert "No partial credit" in result.evaluation_notes

    def test_adds_coverage_property(self):
        result = contract_tightening_strict(_make_comparison_case())
        assert "complete coverage of all requirements" in result.required_properties

    def test_adds_no_placeholder_shortcut(self):
        result = contract_tightening_strict(_make_comparison_case())
        assert "no placeholder or generic content" in result.forbidden_shortcuts


# --- Tests for counterfactual_contract ---


class TestCounterfactualContract:
    def test_returns_task_case(self):
        result = counterfactual_contract(_make_comparison_case())
        assert isinstance(result, TaskCase)

    def test_tag_added(self):
        result = counterfactual_contract(_make_comparison_case())
        assert "perturb_counterfactual_contract" in result.tags

    def test_meta_perturbation_type(self):
        result = counterfactual_contract(_make_comparison_case())
        assert result.meta["perturbation_type"] == "counterfactual_contract"

    def test_is_counterfactual_meta(self):
        result = counterfactual_contract(_make_comparison_case())
        assert result.meta["is_counterfactual"] is True

    def test_swaps_properties_and_shortcuts(self):
        original = _make_comparison_case()
        original_props = list(original.required_properties)
        original_shortcuts = list(original.forbidden_shortcuts)
        result = counterfactual_contract(original)
        assert result.required_properties == original_shortcuts
        assert result.forbidden_shortcuts == original_props

    def test_empty_properties_gets_default(self):
        case = TaskCase.create(prompt_text="Test", expected_primary_family="comparison")
        case.required_properties = []
        case.forbidden_shortcuts = ["some shortcut"]
        result = counterfactual_contract(case)
        assert result.required_properties == ["some shortcut"]
        assert result.forbidden_shortcuts == ["standard approach"]

    def test_empty_shortcuts_gets_default(self):
        case = TaskCase.create(prompt_text="Test", expected_primary_family="comparison")
        case.required_properties = ["some prop"]
        case.forbidden_shortcuts = []
        result = counterfactual_contract(case)
        assert result.required_properties == ["avoidance of standard approach"]
        assert result.forbidden_shortcuts == ["some prop"]


# --- Tests for curriculum integration ---


class TestCurriculumIntegration:
    def test_produces_8_levels(self):
        case = _make_comparison_case()
        levels = build_curriculum_levels(case)
        assert len(levels) == 8

    def test_each_level_is_task_case(self):
        case = _make_comparison_case()
        levels = build_curriculum_levels(case)
        for level in levels:
            assert isinstance(level, TaskCase)

    def test_levels_have_correct_meta(self):
        case = _make_comparison_case()
        levels = build_curriculum_levels(case)
        for i, level in enumerate(levels):
            assert level.meta["curriculum_level"] == i
            assert f"curriculum_level_{i}" in level.tags

    def test_level_6_has_contract_perturbation_tags(self):
        case = _make_comparison_case()
        levels = build_curriculum_levels(case)
        level_6 = levels[6]
        assert "perturb_contract_flip" in level_6.tags
        assert "perturb_property_addition" in level_6.tags

    def test_level_7_has_contract_perturbation_tags(self):
        case = _make_comparison_case()
        levels = build_curriculum_levels(case)
        level_7 = levels[7]
        assert "perturb_counterfactual_contract" in level_7.tags
        assert "perturb_contract_tightening_strict" in level_7.tags

    def test_build_curriculum_from_cases_default_limit_8(self):
        cases = [_make_comparison_case(), _make_synthesis_case()]
        result = build_curriculum_from_cases(cases)
        # Default limit_per_case=8, 2 cases -> 16 variants
        assert len(result) == 16

    def test_build_curriculum_from_cases_custom_limit(self):
        cases = [_make_comparison_case()]
        result = build_curriculum_from_cases(cases, limit_per_case=4)
        assert len(result) == 4
