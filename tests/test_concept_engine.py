"""Tests for the concept engine: selectivity, family policy, and contrastive groups."""
from __future__ import annotations

from virtual_genesis.core.objects.concept import ConceptCard
from virtual_genesis.core.objects.scope import Scope
from virtual_genesis.core.objects.memory import MemoryUnit
from virtual_genesis.runtime.concept_engine.apply import select_applicable_concepts, _family_policy
from virtual_genesis.runtime.concept_engine.config import DEFAULT_FAMILY_SELECTIVITY, FAMILY_SELECTIVITY_STRATEGY
from virtual_genesis.runtime.concept_engine.selector import build_contrastive_groups


def _make_concept(name: str, definition: str, families: list[str], operational_meaning: str = "") -> ConceptCard:
    """Helper to create a ConceptCard with specific scope families."""
    return ConceptCard(
        id=f"concept_{name}",
        object_type="concept",
        name=name,
        definition=definition,
        operational_meaning=operational_meaning or definition,
        scope=Scope(task_families=families),
    )


def test_select_applicable_concepts_empty_when_no_family_match():
    """Concepts scoped to 'comparison' should not be selected for 'procedure' tasks."""
    c1 = _make_concept("contrast_rule", "identifies decisive differences", ["comparison"])
    c2 = _make_concept("evidence_weighting", "weights evidence sources", ["comparison"])

    selected, decisions = select_applicable_concepts(
        task_family="procedure",
        task_text="Extract the fields from this document",
        concepts=[c1, c2],
    )
    assert selected == []
    assert decisions == []


def test_select_applicable_concepts_respects_max_active():
    """With max_active=1 for comparison, exactly 1 concept should be selected when multiple match."""
    c1 = _make_concept(
        "contrast_rule",
        "identifies decisive differences between two proposals",
        ["comparison"],
        operational_meaning="compare contrast difference decisive between proposals identify",
    )
    c2 = _make_concept(
        "evidence_weighting",
        "weights evidence sources for comparison between options",
        ["comparison"],
        operational_meaning="compare evidence weighting options between proposals identify",
    )

    selected, decisions = select_applicable_concepts(
        task_family="comparison",
        task_text="Compare these two proposals and identify the decisive difference between them",
        concepts=[c1, c2],
    )
    # Both concepts have enough token overlap to score above min_score (7),
    # but comparison max_active=1 so only 1 is selected.
    assert len(selected) == 1


def test_select_applicable_concepts_redundancy_penalty():
    """Two nearly identical concepts should have redundancy penalty applied to the second."""
    c1 = _make_concept(
        "pattern_alpha",
        "identifies recurring patterns in comparison tasks with strong evidence signals",
        ["comparison"],
        operational_meaning="recurring patterns comparison tasks strong evidence signals decisive",
    )
    c2 = _make_concept(
        "pattern_beta",
        "identifies recurring patterns in comparison tasks with strong evidence signals",
        ["comparison"],
        operational_meaning="recurring patterns comparison tasks strong evidence signals decisive",
    )

    _, decisions = select_applicable_concepts(
        task_family="comparison",
        task_text="Compare the recurring patterns and evidence signals in these two options to find the decisive difference",
        concepts=[c1, c2],
    )
    # At least one decision should have redundancy_penalty > 0 (the second similar concept)
    penalties = [d.redundancy_penalty for d in decisions]
    assert any(p > 0 for p in penalties), f"Expected redundancy penalty but got {penalties}"


def test_family_policy_returns_correct_defaults():
    """_family_policy should return values from DEFAULT_FAMILY_SELECTIVITY for each known family."""
    for family, cfg in DEFAULT_FAMILY_SELECTIVITY.items():
        max_active, min_score, strategy = _family_policy(family, None, None)
        assert max_active == cfg["max_active"], f"{family}: expected max_active={cfg['max_active']}, got {max_active}"
        assert min_score == cfg["min_score"], f"{family}: expected min_score={cfg['min_score']}, got {min_score}"
        assert strategy == FAMILY_SELECTIVITY_STRATEGY[family], f"{family}: strategy mismatch"


def test_build_contrastive_groups():
    """build_contrastive_groups should produce family_contrast groups from memories with different outcomes."""
    m1 = MemoryUnit.create("Successful comparison task")
    m1.meta = {"task_family": "comparison", "good_enough": True}

    m2 = MemoryUnit.create("Failed comparison task")
    m2.meta = {"task_family": "comparison", "good_enough": False}

    m3 = MemoryUnit.create("Successful synthesis task")
    m3.meta = {"task_family": "synthesis", "good_enough": True}

    m4 = MemoryUnit.create("Failed synthesis task")
    m4.meta = {"task_family": "synthesis", "good_enough": False}

    groups = build_contrastive_groups([m1, m2, m3, m4])
    # Should have at least 2 family_contrast groups (comparison and synthesis)
    family_contrast_groups = [g for g in groups if g["group_type"] == "family_contrast"]
    families_found = {g["family"] for g in family_contrast_groups}
    assert "comparison" in families_found
    assert "synthesis" in families_found
    for g in family_contrast_groups:
        assert len(g["successes"]) > 0
        assert len(g["failures"]) > 0


def test_contract_heavy_doubles_contract_fit():
    """contract_heavy strategy should produce higher scores when task_contract matches concept tokens."""
    c1 = _make_concept(
        "precision_rule",
        "ensures precision in property extraction for comparison",
        ["comparison"],
        operational_meaning="precision property extraction comparison required coverage",
    )

    task_text = "Compare these two proposals for precision and coverage"
    task_contract = {
        "required_properties": ["precision", "coverage", "extraction"],
        "forbidden_shortcuts": [],
        "diagnostic_purpose": [],
    }

    # With contract (contract_heavy doubles contract_fit)
    selected_with, decisions_with = select_applicable_concepts(
        task_family="comparison",
        task_text=task_text,
        concepts=[c1],
        task_contract=task_contract,
    )

    # Without contract (no contract_fit contribution)
    selected_without, decisions_without = select_applicable_concepts(
        task_family="comparison",
        task_text=task_text,
        concepts=[c1],
        task_contract=None,
    )

    # The contract_fit should be > 0 when a contract is provided
    assert decisions_with[0].contract_fit > 0
    # With contract_heavy, the activation_score should be higher due to 2x contract_fit
    assert decisions_with[0].activation_score > decisions_without[0].activation_score


def test_semantic_balanced_secondary_admission():
    """semantic_balanced strategy admits a 2nd concept when both score >= min_score and max_active >= 2."""
    # Both concepts scoped to synthesis with high semantic overlap to task text
    c1 = _make_concept(
        "integration_pattern",
        "combines multiple evidence sources into unified synthesis framework analysis",
        ["synthesis"],
        operational_meaning="combines multiple evidence sources unified synthesis framework analysis integration",
    )
    c2 = _make_concept(
        "convergence_rule",
        "identifies convergence points across multiple evidence sources in synthesis",
        ["synthesis"],
        operational_meaning="convergence points across multiple evidence sources synthesis framework analysis",
    )

    # Task text with heavy token overlap to both concepts
    task_text = (
        "Synthesize these multiple evidence sources into a unified framework "
        "analysis identifying convergence points and integration across all sources"
    )

    selected, decisions = select_applicable_concepts(
        task_family="synthesis",
        task_text=task_text,
        concepts=[c1, c2],
    )
    # synthesis max_active=2 and semantic_balanced strategy admits secondary concept
    # Both concepts should score >= 7 due to high token overlap
    assert len(selected) == 2, (
        f"Expected 2 selected but got {len(selected)}; "
        f"scores: {[(d.notes, d.activation_score, d.selected) for d in decisions]}"
    )


def test_structural_only_high_threshold_fallback():
    """structural_only strategy admits 1 concept via high-threshold fallback when score >= 10."""
    # Create a concept with VERY high token overlap to produce score >= 10
    c1 = _make_concept(
        "extraction_protocol",
        "extracts structured fields from document following strict procedure steps",
        ["procedure"],
        operational_meaning=(
            "extracts structured fields document following strict procedure "
            "steps protocol output format required properties schema"
        ),
    )

    # Task text with massive token overlap to the concept
    task_text = (
        "Following the strict procedure protocol, extracts structured fields "
        "from this document and output the required properties in the schema format steps"
    )

    selected, decisions = select_applicable_concepts(
        task_family="procedure",
        task_text=task_text,
        concepts=[c1],
    )
    # procedure has max_active=0 and min_score=99, but structural_only
    # high-threshold fallback admits 1 concept when score >= 10
    assert len(selected) == 1, (
        f"Expected 1 selected via high-threshold fallback but got {len(selected)}; "
        f"scores: {[(d.notes, d.activation_score, d.selected) for d in decisions]}"
    )
