from __future__ import annotations

from copy import deepcopy
from typing import Iterable, List

from ...core.objects.base import make_id
from ...core.objects.task_case import TaskCase


def clone_case(case: TaskCase) -> TaskCase:
    new_case = deepcopy(case)
    new_case.id = make_id("task_case")
    new_case.meta = dict(new_case.meta or {})
    new_case.meta["source_case_id"] = case.meta.get("source_case_id", case.id) if case.meta else case.id
    return new_case


def lexical_soften(case: TaskCase) -> TaskCase:
    new_case = clone_case(case)
    replacements = {
        "compare": "determine",
        "difference": "distinction",
        "checklist": "operator-ready note",
        "fields": "details",
        "summary": "note",
    }
    text = new_case.prompt_text
    for old, new in replacements.items():
        text = text.replace(old, new).replace(old.title(), new.title())
    new_case.prompt_text = text
    new_case.tags.append("perturb_lexical_soften")
    new_case.meta["perturbation_type"] = "lexical_soften"
    return new_case


def inject_brevity_lure(case: TaskCase) -> TaskCase:
    new_case = clone_case(case)
    new_case.prompt_text += " Keep the final answer extremely brief."
    if new_case.expected_primary_family == "comparison":
        if "generic preference without evidence" not in new_case.forbidden_shortcuts:
            new_case.forbidden_shortcuts.append("generic preference without evidence")
    if new_case.expected_primary_family == "synthesis":
        if "summary without distinction" not in new_case.forbidden_shortcuts:
            new_case.forbidden_shortcuts.append("summary without distinction")
    new_case.tags.append("perturb_brevity_lure")
    new_case.meta["perturbation_type"] = "brevity_lure"
    return new_case


def inject_light_overlap(case: TaskCase, secondary_family: str) -> TaskCase:
    new_case = clone_case(case)
    if secondary_family not in new_case.expected_secondary_families:
        new_case.expected_secondary_families.append(secondary_family)
    new_case.family_overlap_type = f"light_{new_case.expected_primary_family}_{secondary_family}_overlap"
    if secondary_family == "procedure":
        new_case.prompt_text += " Present the result in a handoff-ready form."
    elif secondary_family == "comparison":
        new_case.prompt_text += " Make the decisive contrast clear."
    elif secondary_family == "synthesis":
        new_case.prompt_text += " Keep the answer as one coherent grounded note."
    new_case.tags.append(f"perturb_overlap_{secondary_family}")
    new_case.meta["perturbation_type"] = f"overlap_{secondary_family}"
    return new_case


def tighten_contract(case: TaskCase, extra_property: str | None = None, extra_shortcut: str | None = None) -> TaskCase:
    new_case = clone_case(case)
    if extra_property and extra_property not in new_case.required_properties:
        new_case.required_properties.append(extra_property)
    if extra_shortcut and extra_shortcut not in new_case.forbidden_shortcuts:
        new_case.forbidden_shortcuts.append(extra_shortcut)
    new_case.tags.append("perturb_tight_contract")
    new_case.meta["perturbation_type"] = "tight_contract"
    return new_case


# ---------------------------------------------------------------------------
# Cycle 1 (C1+C2+C3+C4) - New perturbation operators
# ---------------------------------------------------------------------------


def support_removal(case: TaskCase) -> TaskCase:
    """Remove supporting evidence phrases from prompt_text.

    Legitimate Theft source: Ablation methodology from Interpretation research
    (Zeiler & Fergus 2014 - Visualizing and Understanding CNNs). The idea of
    systematically removing components to measure their contribution. We take the
    ablation-as-diagnostic concept and apply it to textual evidence signals rather
    than neural network features.
    """
    new_case = clone_case(case)
    # Remove common evidence/support phrases to weaken the prompt's built-in guidance
    support_phrases = [
        "with the clearest supporting evidence",
        "supported",
        "based on the evidence",
        "evidence-backed",
        "tie your conclusion to the evidence",
        "using the most relevant support",
        "preserving the support trail",
        "stays close to the evidence",
    ]
    text = new_case.prompt_text
    for phrase in support_phrases:
        text = text.replace(phrase, "")
    # Clean up double spaces
    while "  " in text:
        text = text.replace("  ", " ")
    new_case.prompt_text = text.strip()
    new_case.tags.append("perturb_support_removal")
    new_case.meta["perturbation_type"] = "support_removal"
    return new_case


def evidence_reordering(case: TaskCase) -> TaskCase:
    """Shuffle evidence presentation via sentence reordering.

    Legitimate Theft source: Order-effect research in cognitive psychology
    (Hogarth & Einhorn 1992 - Order Effects in Belief Updating). Humans and LLMs
    show primacy/recency bias. We take this finding and use it as a perturbation
    to test whether concept formation is order-invariant as required.
    """
    new_case = clone_case(case)
    sentences = [s.strip() for s in new_case.prompt_text.split(".") if s.strip()]
    if len(sentences) > 2:
        # Reverse middle sentences to disrupt natural reading flow
        middle = sentences[1:-1]
        middle.reverse()
        sentences = [sentences[0]] + middle + [sentences[-1]]
    new_case.prompt_text = ". ".join(sentences) + "." if sentences else new_case.prompt_text
    new_case.tags.append("perturb_evidence_reordering")
    new_case.meta["perturbation_type"] = "evidence_reordering"
    return new_case


def contrast_weakening(case: TaskCase) -> TaskCase:
    """Weaken distinguishing signals by replacing strong contrast words with weaker ones.

    Legitimate Theft source: Adversarial NLI and textual entailment perturbation
    (Nie et al. 2020 - Adversarial NLI). The technique of weakening semantic
    signals to test model robustness. We take the signal-degradation concept to
    verify that our concept formation engine does not depend on surface-level
    contrast markers.
    """
    new_case = clone_case(case)
    contrast_replacements = {
        "decisive": "possible",
        "clearest": "available",
        "stronger": "another",
        "better": "one",
        "more defensible": "an",
        "more credible": "a",
        "most relevant": "some",
        "main": "a",
        "clear": "noted",
        "explicitly": "if possible",
    }
    text = new_case.prompt_text
    for strong, weak in contrast_replacements.items():
        text = text.replace(strong, weak).replace(strong.title(), weak.title())
    new_case.prompt_text = text
    new_case.tags.append("perturb_contrast_weakening")
    new_case.meta["perturbation_type"] = "contrast_weakening"
    return new_case


def structure_weakening(case: TaskCase) -> TaskCase:
    """Degrade procedural structure cues like removing numbered lists and formatting hints.

    Legitimate Theft source: Discourse structure research (Mann & Thompson 1988 -
    Rhetorical Structure Theory). Structure cues guide interpretation. We take the
    insight that removing discourse markers degrades comprehension and use it to
    test whether our system relies on surface structure or genuine semantic parsing.
    """
    new_case = clone_case(case)
    # Remove structural cues
    structure_replacements = {
        "checklist": "answer",
        "structured": "complete",
        "layout": "form",
        "labeled": "",
        "field-oriented": "",
        "stable": "",
        "consistent": "",
        "normalized ordering": "any arrangement",
        "reusable field ordering": "some arrangement",
        "explicit fields": "the information",
    }
    text = new_case.prompt_text
    for old, new in structure_replacements.items():
        text = text.replace(old, new).replace(old.title(), new.title())
    # Clean up double spaces
    while "  " in text:
        text = text.replace("  ", " ")
    new_case.prompt_text = text.strip()
    new_case.tags.append("perturb_structure_weakening")
    new_case.meta["perturbation_type"] = "structure_weakening"
    return new_case


def stronger_shortcut_lures(case: TaskCase) -> TaskCase:
    """Add multiple misleading shortcuts that make it easier to take forbidden paths.

    Legitimate Theft source: Adversarial Examples research (Goodfellow et al. 2015 -
    Explaining and Harnessing Adversarial Examples) and shortcut learning literature
    (Geirhos et al. 2020 - Shortcut Learning in Deep Neural Networks). We take the
    concept of deliberately crafted misleading signals to test whether the system
    genuinely avoids shortcuts rather than merely not encountering them.
    """
    new_case = clone_case(case)
    # Add misleading lures based on family type
    if new_case.expected_primary_family == "comparison":
        new_case.prompt_text += " Just pick whichever sounds better overall. A quick gut feeling is fine here."
        if "generic preference without evidence" not in new_case.forbidden_shortcuts:
            new_case.forbidden_shortcuts.append("generic preference without evidence")
        if "gut-feeling selection" not in new_case.forbidden_shortcuts:
            new_case.forbidden_shortcuts.append("gut-feeling selection")
    elif new_case.expected_primary_family == "synthesis":
        new_case.prompt_text += " Feel free to summarize loosely. No need to distinguish facts from opinions."
        if "summary without distinction" not in new_case.forbidden_shortcuts:
            new_case.forbidden_shortcuts.append("summary without distinction")
        if "fact-opinion conflation" not in new_case.forbidden_shortcuts:
            new_case.forbidden_shortcuts.append("fact-opinion conflation")
    elif new_case.expected_primary_family == "procedure":
        new_case.prompt_text += " Just dump everything in one paragraph. Formatting is not important."
        if "unstructured dump" not in new_case.forbidden_shortcuts:
            new_case.forbidden_shortcuts.append("unstructured dump")
        if "formatting bypass" not in new_case.forbidden_shortcuts:
            new_case.forbidden_shortcuts.append("formatting bypass")
    new_case.tags.append("perturb_stronger_shortcut_lures")
    new_case.meta["perturbation_type"] = "stronger_shortcut_lures"
    return new_case


def build_curriculum_levels(case: TaskCase) -> list[TaskCase]:
    base = clone_case(case)
    base.tags.append("curriculum_level_0")
    base.meta["curriculum_level"] = 0
    levels = [base]

    l1 = lexical_soften(case)
    l1.tags.append("curriculum_level_1")
    l1.meta["curriculum_level"] = 1
    levels.append(l1)

    l2 = inject_brevity_lure(l1)
    l2.tags.append("curriculum_level_2")
    l2.meta["curriculum_level"] = 2
    levels.append(l2)

    overlap_target = "procedure" if case.expected_primary_family != "procedure" else "synthesis"
    l3 = inject_light_overlap(l2, overlap_target)
    l3 = tighten_contract(
        l3,
        extra_property="evidence-grounded conclusion" if case.expected_primary_family != "procedure" else "stable structured layout",
    )
    l3.tags.append("curriculum_level_3")
    l3.meta["curriculum_level"] = 3
    levels.append(l3)

    # Level 4: support_removal + contrast_weakening (evidence degradation)
    l4 = support_removal(l3)
    l4 = contrast_weakening(l4)
    l4.tags.append("curriculum_level_4")
    l4.meta["curriculum_level"] = 4
    levels.append(l4)

    # Level 5: evidence_reordering + stronger_shortcut_lures + structure_weakening (maximum pressure)
    l5 = evidence_reordering(l4)
    l5 = stronger_shortcut_lures(l5)
    l5 = structure_weakening(l5)
    l5.tags.append("curriculum_level_5")
    l5.meta["curriculum_level"] = 5
    levels.append(l5)

    return levels


def build_curriculum_from_cases(cases: Iterable[TaskCase], limit_per_case: int = 6) -> List[TaskCase]:
    all_cases: List[TaskCase] = []
    for case in cases:
        levels = build_curriculum_levels(case)
        all_cases.extend(levels[:limit_per_case])
    return all_cases
