from __future__ import annotations

from typing import List

from ...core.objects.task_case import TaskCase
from ..perturbations.taskcase_variants import build_curriculum_from_cases


def _comparison_case(prompt: str, critical: bool = False) -> TaskCase:
    case = TaskCase.create(prompt, expected_primary_family="comparison")
    case.required_properties = ["explicit comparison", "evidence-backed choice", "contrast articulation"]
    case.forbidden_shortcuts = ["generic preference without evidence", "gut-feeling selection"]
    case.diagnostic_purpose = ["thesis_1_discriminative", "comparison_quality", "perturbation_resistance"]
    case.target_thesis = ["thesis_1", "thesis_2"]
    case.criticality_class = "high" if critical else "medium"
    case.difficulty_class = "hard"
    return case


def _synthesis_case(prompt: str, critical: bool = False) -> TaskCase:
    case = TaskCase.create(prompt, expected_primary_family="synthesis")
    case.expected_secondary_families = ["procedure"]
    case.family_overlap_type = "light_synthesis_procedure_overlap"
    case.required_properties = ["evidence-grounded conclusion", "fact vs inference separation", "source attribution"]
    case.forbidden_shortcuts = ["summary without distinction", "fact-opinion conflation"]
    case.diagnostic_purpose = ["thesis_1_discriminative", "synthesis_grounding", "perturbation_resistance"]
    case.target_thesis = ["thesis_1", "thesis_2"]
    case.criticality_class = "high" if critical else "medium"
    case.difficulty_class = "hard"
    return case


def _procedure_case(prompt: str, critical: bool = False) -> TaskCase:
    case = TaskCase.create(prompt, expected_primary_family="procedure")
    case.required_properties = ["stable structured layout", "field completeness"]
    case.forbidden_shortcuts = ["unstructured dump"]
    case.diagnostic_purpose = ["procedure_reuse", "thesis_2_support", "perturbation_resistance"]
    case.target_thesis = ["thesis_1", "thesis_2"]
    case.criticality_class = "high" if critical else "medium"
    case.difficulty_class = "hard"
    return case


PROTOTYPE_V6_CASES: List[TaskCase] = [
    # Comparison (6 cases): harder prompts with deeper evidence requirements
    _comparison_case(
        "Evaluate both deployment strategies against the failure evidence collected last quarter and select the one with stronger empirical support. Make the decisive contrast unmistakable.",
        critical=True,
    ),
    _comparison_case(
        "Given the conflicting reports from the two monitoring sources, determine which interpretation is more defensible and explain the critical evidence difference.",
    ),
    _comparison_case(
        "Compare the two proposed escalation paths using only the documented incident data. Choose the better-supported option and articulate why the alternative fails.",
    ),
    _comparison_case(
        "Between the legacy and proposed approaches, identify which has stronger backing from the operational history and make the evidence gap explicit.",
    ),
    _comparison_case(
        "Analyze the competing root-cause hypotheses and pick the one with more corroborating signals. The contrast must be traceable to specific evidence items.",
    ),
    _comparison_case(
        "Review both vendor assessments and select the more credible conclusion. Ground the selection in the observable differences between their supporting data.",
    ),

    # Synthesis (6 cases): require genuine evidence separation
    _synthesis_case(
        "From the scattered incident fragments below, produce a single grounded explanation that rigorously separates what was directly observed from what is inferred. Flag any inference explicitly.",
        critical=True,
    ),
    _synthesis_case(
        "Merge the three conflicting status updates into one coherent account. Distinguish confirmed facts from speculation and note where sources disagree.",
    ),
    _synthesis_case(
        "Synthesize the raw operational notes into a compact evidence-based conclusion. Every claim must trace to a specific note and inferences must be marked.",
    ),
    _synthesis_case(
        "Create a unified interpretation from the fragmented signals below. Preserve the evidential chain and clearly label any gap-filling reasoning.",
    ),
    _synthesis_case(
        "Turn the contradictory findings into one grounded narrative. Separate observation from interpretation and identify which conclusions lack direct support.",
    ),
    _synthesis_case(
        "Combine the partial reports into a coherent picture. Mark each statement as observed-fact or derived-inference and highlight unresolved contradictions.",
    ),

    # Procedure (6 cases): structurally demanding with completeness requirements
    _procedure_case(
        "Extract all actionable fields from the raw input and organize them into a stable, labeled layout suitable for automated downstream consumption.",
        critical=True,
    ),
    _procedure_case(
        "Transform the unstructured incident record into a normalized handoff document with explicit field labels, consistent ordering, and no omitted values.",
    ),
    _procedure_case(
        "Produce a field-complete structured checklist from the noisy input. Every required field must appear with its value or an explicit 'missing' marker.",
    ),
    _procedure_case(
        "Convert the ad-hoc notes into a reusable structured format with labeled sections, normalized field names, and deterministic ordering.",
    ),
    _procedure_case(
        "Build a clean operator-ready layout from the raw details below. Ensure stable structure, explicit labels, and a format that another tool can parse reliably.",
    ),
    _procedure_case(
        "Reformat the scattered data points into a consistent checklist with typed fields, normalized values, and a predictable layout for handoff.",
    ),
]


def build_v6_curriculum() -> List[TaskCase]:
    """Apply the extended 6-level curriculum to all v6 cases.

    Uses build_curriculum_from_cases with limit_per_case=6 to produce
    the full perturbation curriculum across all difficulty levels.
    """
    return build_curriculum_from_cases(PROTOTYPE_V6_CASES, limit_per_case=6)
