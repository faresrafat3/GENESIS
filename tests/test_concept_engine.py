"""Tests for the concept engine: selectivity, family policy, and contrastive groups."""
from __future__ import annotations

from virtual_sia.core.objects.concept import ConceptCard
from virtual_sia.core.objects.scope import Scope
from virtual_sia.core.objects.memory import MemoryUnit
from virtual_sia.runtime.concept_engine.apply import select_applicable_concepts, _family_policy
from virtual_sia.runtime.concept_engine.config import DEFAULT_FAMILY_SELECTIVITY, FAMILY_SELECTIVITY_STRATEGY
from virtual_sia.runtime.concept_engine.selector import build_contrastive_groups


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
    """With max_active=1 for comparison, only 1 concept should be selected even with multiple matching."""
    c1 = _make_concept(
        "contrast_rule",
        "identifies decisive differences between two proposals",
        ["comparison"],
        operational_meaning="compare contrast difference decisive between proposals",
    )
    c2 = _make_concept(
        "evidence_weighting",
        "weights evidence sources for comparison between options",
        ["comparison"],
        operational_meaning="compare evidence weighting options between proposals",
    )

    selected, decisions = select_applicable_concepts(
        task_family="comparison",
        task_text="Compare these two proposals and identify the decisive difference between them",
        concepts=[c1, c2],
    )
    # comparison max_active is 1
    assert len(selected) <= DEFAULT_FAMILY_SELECTIVITY["comparison"]["max_active"]


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
