from __future__ import annotations

from ...core.objects.task_case import TaskCase


def _comparison_case(prompt: str, critical: bool = False) -> TaskCase:
    case = TaskCase.create(prompt, expected_primary_family="comparison")
    case.required_properties = ["explicit comparison", "evidence-backed choice"]
    case.forbidden_shortcuts = ["generic preference without evidence"]
    case.diagnostic_purpose = ["thesis_1_discriminative", "comparison_quality"]
    case.target_thesis = ["thesis_1", "thesis_2"]
    case.criticality_class = "high" if critical else "medium"
    return case


def _synthesis_case(prompt: str, critical: bool = False) -> TaskCase:
    case = TaskCase.create(prompt, expected_primary_family="synthesis")
    case.expected_secondary_families = ["procedure"]
    case.family_overlap_type = "light_synthesis_procedure_overlap"
    case.required_properties = ["evidence-grounded conclusion", "fact vs inference separation"]
    case.forbidden_shortcuts = ["summary without distinction"]
    case.diagnostic_purpose = ["thesis_1_discriminative", "synthesis_grounding"]
    case.target_thesis = ["thesis_1", "thesis_2"]
    case.criticality_class = "high" if critical else "medium"
    return case


def _procedure_case(prompt: str, critical: bool = False) -> TaskCase:
    case = TaskCase.create(prompt, expected_primary_family="procedure")
    case.required_properties = ["stable structured layout"]
    case.forbidden_shortcuts = []
    case.diagnostic_purpose = ["procedure_reuse", "thesis_2_support"]
    case.target_thesis = ["thesis_1", "thesis_2"]
    case.criticality_class = "high" if critical else "medium"
    return case


PROTOTYPE_V5_CASES = [
    # Comparison: clear family, stronger hidden requirement but no heavy overlap
    _comparison_case("For the release memo, choose the safer rollback plan and justify the decision with the clearest supporting evidence.", critical=True),
    _comparison_case("Determine which mitigation option is better supported and make the decisive contrast explicit."),
    _comparison_case("Choose the more defensible explanation and tie your conclusion to the evidence rather than preference."),
    _comparison_case("State which path is more credible and explain the main evidence-backed difference."),
    _comparison_case("Pick the stronger recommendation and justify it using the most relevant support."),
    _comparison_case("Identify which account deserves more confidence and make the contrast clear for a reviewer."),

    # Synthesis: designed to fail if output becomes generic summary
    _synthesis_case("Prepare a grounded incident update from the fragments below, clearly separating what is observed from what is inferred.", critical=True),
    _synthesis_case("Write one concise evidence-based conclusion from the notes below and keep observation distinct from inference."),
    _synthesis_case("Merge the findings into a short grounded answer without blurring facts and interpretation."),
    _synthesis_case("Produce a compact synthesis that stays close to the evidence and makes any inference explicit."),
    _synthesis_case("Create a coherent answer from the fragments below, preserving the support trail and separating what was seen from what is concluded."),
    _synthesis_case("Turn the scattered findings into one grounded explanation that does not collapse into a generic summary."),

    # Procedure: should remain easy enough but structurally demanding
    _procedure_case("Extract the required fields below and return them in a stable, labeled layout for handoff."),
    _procedure_case("Convert the raw details into a clean checklist with explicit fields and normalized ordering."),
    _procedure_case("Reformat the record into a structured handoff note with reusable field ordering."),
    _procedure_case("Build a compact field-oriented checklist from the raw material below."),
    _procedure_case("Produce a stable structured layout from the details below so the next operator can scan it quickly."),
    _procedure_case("Turn the input into a consistent checklist with labeled values and minimal noise."),
]
