from __future__ import annotations

from typing import Dict, List

from ...core.objects.task_case import TaskCase
from ..perturbations.taskcase_variants import (
    contrast_weakening,
    stronger_shortcut_lures,
    support_removal,
)


"""Anti-shortcut benchmark slice.

Legitimate Theft source: Shortcut Learning in Deep Neural Networks
(Geirhos et al. 2020) and Challenge Sets for evaluating NLU
(McCoy et al. 2019 - Right for the Wrong Reasons). We take the
methodology of constructing evaluation sets specifically designed
to expose reliance on spurious correlations and surface heuristics,
applying it to verify that Virtual-GENESIS's concept formation engine
produces genuine understanding rather than pattern matching.
"""

# Known forbidden shortcuts that the system must genuinely avoid
KNOWN_SHORTCUTS: Dict[str, Dict[str, str]] = {
    "generic preference without evidence": {
        "family": "comparison",
        "description": "Choosing an option without citing specific evidence",
        "attack_vector": "Make the prompt sound like a preference question",
    },
    "gut-feeling selection": {
        "family": "comparison",
        "description": "Selection based on vague intuition markers",
        "attack_vector": "Add emotional/intuitive language encouraging quick picks",
    },
    "summary without distinction": {
        "family": "synthesis",
        "description": "Generic summary that collapses fact and inference",
        "attack_vector": "Frame the task as a simple summarization",
    },
    "fact-opinion conflation": {
        "family": "synthesis",
        "description": "Mixing observed facts with derived opinions seamlessly",
        "attack_vector": "Present mixed signals without clear separation markers",
    },
    "unstructured dump": {
        "family": "procedure",
        "description": "Dumping content without structure or labels",
        "attack_vector": "Suggest that formatting does not matter",
    },
    "formatting bypass": {
        "family": "procedure",
        "description": "Skipping structural requirements to save effort",
        "attack_vector": "Encourage prose-form output over structured fields",
    },
}


def _create_anti_shortcut_cases_for_comparison() -> List[TaskCase]:
    """Generate cases that would pass verification ONLY if comparison shortcuts are avoided."""
    cases = []

    # Case 1: Looks like a preference question but requires evidence
    c1 = TaskCase.create(
        prompt_text="Which of these two approaches do you like better? Pick your favorite and explain. "
        "Note: your selection must be backed by specific documented evidence from the incident log.",
        expected_primary_family="comparison",
    )
    c1.required_properties = ["explicit comparison", "evidence-backed choice"]
    c1.forbidden_shortcuts = ["generic preference without evidence", "gut-feeling selection"]
    c1.diagnostic_purpose = ["anti_shortcut", "comparison_evidence_requirement"]
    c1.tags = ["anti_shortcut", "targets_generic_preference"]
    c1.meta = {"benchmark_type": "anti_shortcut", "targeted_shortcut": "generic preference without evidence"}
    cases.append(c1)

    # Case 2: Emotional framing but must be evidence-based
    c2 = TaskCase.create(
        prompt_text="Trust your instinct here - which mitigation feels right? "
        "However, the final answer must articulate the decisive evidence-based contrast between options.",
        expected_primary_family="comparison",
    )
    c2.required_properties = ["explicit comparison", "evidence-backed choice", "contrast articulation"]
    c2.forbidden_shortcuts = ["generic preference without evidence", "gut-feeling selection"]
    c2.diagnostic_purpose = ["anti_shortcut", "resist_emotional_framing"]
    c2.tags = ["anti_shortcut", "targets_gut_feeling"]
    c2.meta = {"benchmark_type": "anti_shortcut", "targeted_shortcut": "gut-feeling selection"}
    cases.append(c2)

    # Case 3: Apply perturbation operators for extra pressure
    c3 = TaskCase.create(
        prompt_text="Compare the two solutions and select the more defensible one based on the clearest supporting evidence. "
        "Make the decisive contrast explicit for a reviewer.",
        expected_primary_family="comparison",
    )
    c3.required_properties = ["explicit comparison", "evidence-backed choice"]
    c3.forbidden_shortcuts = ["generic preference without evidence"]
    c3.diagnostic_purpose = ["anti_shortcut", "perturbation_overlap"]
    c3.tags = ["anti_shortcut", "perturbation_combined"]
    c3.meta = {"benchmark_type": "anti_shortcut", "targeted_shortcut": "generic preference without evidence"}
    c3 = support_removal(c3)
    c3 = stronger_shortcut_lures(c3)
    cases.append(c3)

    return cases


def _create_anti_shortcut_cases_for_synthesis() -> List[TaskCase]:
    """Generate cases that would pass verification ONLY if synthesis shortcuts are avoided."""
    cases = []

    # Case 1: Sounds like a summary request but requires distinction
    c1 = TaskCase.create(
        prompt_text="Summarize what happened in the incident. "
        "Critical requirement: every statement must be labeled as observed-fact or derived-inference.",
        expected_primary_family="synthesis",
    )
    c1.required_properties = ["evidence-grounded conclusion", "fact vs inference separation"]
    c1.forbidden_shortcuts = ["summary without distinction", "fact-opinion conflation"]
    c1.diagnostic_purpose = ["anti_shortcut", "synthesis_distinction_requirement"]
    c1.tags = ["anti_shortcut", "targets_summary_without_distinction"]
    c1.meta = {"benchmark_type": "anti_shortcut", "targeted_shortcut": "summary without distinction"}
    cases.append(c1)

    # Case 2: Mixed signals with no obvious separation
    c2 = TaskCase.create(
        prompt_text="The team reported conflicting findings. Merge them into one account. "
        "You must explicitly flag where you bridge gaps with inference versus where you report direct observation.",
        expected_primary_family="synthesis",
    )
    c2.required_properties = ["evidence-grounded conclusion", "fact vs inference separation", "source attribution"]
    c2.forbidden_shortcuts = ["summary without distinction", "fact-opinion conflation"]
    c2.diagnostic_purpose = ["anti_shortcut", "resist_conflation_pressure"]
    c2.tags = ["anti_shortcut", "targets_fact_opinion_conflation"]
    c2.meta = {"benchmark_type": "anti_shortcut", "targeted_shortcut": "fact-opinion conflation"}
    cases.append(c2)

    # Case 3: Perturbation-combined pressure
    c3 = TaskCase.create(
        prompt_text="Produce a grounded synthesis from the fragments below. "
        "Separate confirmed observations from inferred conclusions and preserve the evidence trail.",
        expected_primary_family="synthesis",
    )
    c3.required_properties = ["evidence-grounded conclusion", "fact vs inference separation"]
    c3.forbidden_shortcuts = ["summary without distinction"]
    c3.diagnostic_purpose = ["anti_shortcut", "perturbation_overlap"]
    c3.tags = ["anti_shortcut", "perturbation_combined"]
    c3.meta = {"benchmark_type": "anti_shortcut", "targeted_shortcut": "summary without distinction"}
    c3 = contrast_weakening(c3)
    c3 = stronger_shortcut_lures(c3)
    cases.append(c3)

    return cases


def _create_anti_shortcut_cases_for_procedure() -> List[TaskCase]:
    """Generate cases that would pass verification ONLY if procedure shortcuts are avoided."""
    cases = []

    # Case 1: Explicitly suggests skipping structure
    c1 = TaskCase.create(
        prompt_text="Just get the key info out of this record, however you want. "
        "Requirement: output must be a stable labeled layout with explicit field names and normalized ordering.",
        expected_primary_family="procedure",
    )
    c1.required_properties = ["stable structured layout", "field completeness"]
    c1.forbidden_shortcuts = ["unstructured dump", "formatting bypass"]
    c1.diagnostic_purpose = ["anti_shortcut", "procedure_structure_requirement"]
    c1.tags = ["anti_shortcut", "targets_unstructured_dump"]
    c1.meta = {"benchmark_type": "anti_shortcut", "targeted_shortcut": "unstructured dump"}
    cases.append(c1)

    # Case 2: Suggests prose is fine
    c2 = TaskCase.create(
        prompt_text="Write up the details in a flowing paragraph if you prefer. "
        "Note: the output will be consumed by an automated parser and must use consistent labeled fields.",
        expected_primary_family="procedure",
    )
    c2.required_properties = ["stable structured layout", "field completeness"]
    c2.forbidden_shortcuts = ["unstructured dump", "formatting bypass"]
    c2.diagnostic_purpose = ["anti_shortcut", "resist_prose_pressure"]
    c2.tags = ["anti_shortcut", "targets_formatting_bypass"]
    c2.meta = {"benchmark_type": "anti_shortcut", "targeted_shortcut": "formatting bypass"}
    cases.append(c2)

    # Case 3: Perturbation-combined pressure
    c3 = TaskCase.create(
        prompt_text="Extract the required fields from the raw input and return them in a stable, labeled layout for handoff.",
        expected_primary_family="procedure",
    )
    c3.required_properties = ["stable structured layout"]
    c3.forbidden_shortcuts = ["unstructured dump"]
    c3.diagnostic_purpose = ["anti_shortcut", "perturbation_overlap"]
    c3.tags = ["anti_shortcut", "perturbation_combined"]
    c3.meta = {"benchmark_type": "anti_shortcut", "targeted_shortcut": "unstructured dump"}
    c3 = support_removal(c3)
    c3 = stronger_shortcut_lures(c3)
    cases.append(c3)

    return cases


def generate_anti_shortcut_benchmark() -> List[TaskCase]:
    """Generate the full anti-shortcut benchmark slice.

    For each forbidden_shortcut type, generates 3+ task cases that would
    pass verification ONLY if the shortcut is genuinely avoided. Includes
    overlap with new perturbation operators (support_removal, contrast_weakening,
    stronger_shortcut_lures) for maximum diagnostic pressure.

    Returns a list of TaskCase objects specifically designed to defeat known shortcuts.
    """
    cases: List[TaskCase] = []
    cases.extend(_create_anti_shortcut_cases_for_comparison())
    cases.extend(_create_anti_shortcut_cases_for_synthesis())
    cases.extend(_create_anti_shortcut_cases_for_procedure())
    return cases


# Pre-built benchmark for direct import
ANTI_SHORTCUT_BENCHMARK: List[TaskCase] = generate_anti_shortcut_benchmark()
