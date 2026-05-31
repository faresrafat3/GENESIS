"""Contract-level perturbation operators.

These operators modify the CONTRACT (required_properties, forbidden_shortcuts)
rather than just prompt_text. They test whether verification correctly responds
to changes in success criteria.

Legitimate Theft Sources:
- 5.65: CheckList (Ribeiro et al. 2020, ACL Best Paper) - Minimum Functionality Tests
- 5.66: Contrast Sets (Gardner et al. 2020, EMNLP) - Minimal edits to flip results
- 5.67: Counterfactually-Augmented Data (Kaushik et al. 2020, ICLR) - Same text, reversed label
- 5.68: Dynabench (Kiela et al. 2021, NAACL) - Dynamic adversarial benchmarking
"""
from __future__ import annotations

from .taskcase_variants import clone_case
from ...core.objects.task_case import TaskCase


def property_addition(case: TaskCase) -> TaskCase:
    """Add an extra required_property that template-based responses won't satisfy.

    Theft 5.66: Gardner et al. 2020 Contrast Sets - minimal edit should change result.
    """
    new_case = clone_case(case)
    extra_props = {
        "comparison": "quantitative cost-benefit ratio",
        "synthesis": "temporal ordering of evidence",
        "procedure": "rollback instructions for each step",
    }
    extra = extra_props.get(
        new_case.expected_primary_family,
        "meta-cognitive reflection on reasoning process",
    )
    if extra not in new_case.required_properties:
        new_case.required_properties.append(extra)
    new_case.tags.append("perturb_property_addition")
    new_case.meta["perturbation_type"] = "property_addition"
    return new_case


def property_removal(case: TaskCase) -> TaskCase:
    """Remove a required_property to test if verification correctly passes easier.

    Theft 5.65: Ribeiro CheckList - Minimum Functionality Test.
    """
    new_case = clone_case(case)
    if new_case.required_properties:
        new_case.required_properties = new_case.required_properties[:-1]
    new_case.tags.append("perturb_property_removal")
    new_case.meta["perturbation_type"] = "property_removal"
    return new_case


def shortcut_injection(case: TaskCase) -> TaskCase:
    """Add a forbidden_shortcut that targets template-style responses.

    Theft 5.66: Contrast Sets - adding constraint should change verification.
    """
    new_case = clone_case(case)
    injected_shortcuts = {
        "comparison": "formulaic comparison structure",
        "synthesis": "bullet-point listing without narrative",
        "procedure": "generic step numbering without context",
    }
    shortcut = injected_shortcuts.get(
        new_case.expected_primary_family,
        "mechanical pattern-matching response",
    )
    if shortcut not in new_case.forbidden_shortcuts:
        new_case.forbidden_shortcuts.append(shortcut)
    new_case.tags.append("perturb_shortcut_injection")
    new_case.meta["perturbation_type"] = "shortcut_injection"
    return new_case


def contract_flip(case: TaskCase) -> TaskCase:
    """Swap a required_property to forbidden_shortcuts and vice versa.

    Theft 5.67: Kaushik Counterfactual Data - same text, reversed label.
    """
    new_case = clone_case(case)
    if new_case.required_properties:
        moved_prop = new_case.required_properties.pop(0)
        if moved_prop not in new_case.forbidden_shortcuts:
            new_case.forbidden_shortcuts.append(moved_prop)
    if new_case.forbidden_shortcuts and len(new_case.forbidden_shortcuts) > 1:
        moved_shortcut = new_case.forbidden_shortcuts.pop(0)
        if moved_shortcut not in new_case.required_properties:
            new_case.required_properties.insert(0, moved_shortcut)
    new_case.tags.append("perturb_contract_flip")
    new_case.meta["perturbation_type"] = "contract_flip"
    return new_case


def contract_tightening_strict(case: TaskCase) -> TaskCase:
    """Make ALL properties mandatory with no partial credit.

    Theft 5.68: Dynabench - dynamic adversarial benchmarking.
    """
    new_case = clone_case(case)
    new_case.evaluation_notes = (
        "STRICT: All required_properties must be fully satisfied. No partial credit."
    )
    if "complete coverage of all requirements" not in new_case.required_properties:
        new_case.required_properties.append("complete coverage of all requirements")
    if "no placeholder or generic content" not in new_case.forbidden_shortcuts:
        new_case.forbidden_shortcuts.append("no placeholder or generic content")
    new_case.tags.append("perturb_contract_tightening_strict")
    new_case.meta["perturbation_type"] = "contract_tightening_strict"
    new_case.meta["strict_mode"] = True
    return new_case


def counterfactual_contract(case: TaskCase) -> TaskCase:
    """Create a mirror case where success criteria are inverted.

    Theft 5.67: Kaushik Counterfactual Data - same task, inverted requirements.
    """
    new_case = clone_case(case)
    original_props = list(new_case.required_properties)
    original_shortcuts = list(new_case.forbidden_shortcuts)
    new_case.required_properties = (
        original_shortcuts if original_shortcuts else ["avoidance of standard approach"]
    )
    new_case.forbidden_shortcuts = (
        original_props if original_props else ["standard approach"]
    )
    new_case.tags.append("perturb_counterfactual_contract")
    new_case.meta["perturbation_type"] = "counterfactual_contract"
    new_case.meta["is_counterfactual"] = True
    return new_case
