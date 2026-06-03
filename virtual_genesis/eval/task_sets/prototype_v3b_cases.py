from __future__ import annotations

from ...core.objects.task_case import TaskCase


def _comparison_case(prompt: str) -> TaskCase:
    case = TaskCase.create(prompt, expected_primary_family="comparison")
    case.expected_secondary_families = []
    case.required_properties = ["explicit comparison", "evidence-backed choice"]
    case.forbidden_shortcuts = ["generic preference without evidence"]
    case.diagnostic_purpose = ["thesis_1_discriminative", "comparison_quality"]
    case.target_thesis = ["thesis_1", "thesis_2"]
    return case


def _synthesis_case(prompt: str) -> TaskCase:
    case = TaskCase.create(prompt, expected_primary_family="synthesis")
    case.expected_secondary_families = ["procedure"]
    case.family_overlap_type = "light_synthesis_procedure_overlap"
    case.required_properties = ["evidence-grounded conclusion", "fact vs inference separation"]
    case.forbidden_shortcuts = ["summary without distinction"]
    case.diagnostic_purpose = ["thesis_1_discriminative", "synthesis_grounding"]
    case.target_thesis = ["thesis_1", "thesis_2"]
    return case


def _procedure_case(prompt: str) -> TaskCase:
    case = TaskCase.create(prompt, expected_primary_family="procedure")
    case.expected_secondary_families = []
    case.required_properties = ["stable structured layout"]
    case.forbidden_shortcuts = []
    case.diagnostic_purpose = ["procedure_reuse", "thesis_2_support"]
    case.target_thesis = ["thesis_1", "thesis_2"]
    return case


PROTOTYPE_V3B_CASES = [
    # comparison — clear but not trivial
    _comparison_case("Choose the safer proposal and justify the choice with the strongest supporting evidence."),
    _comparison_case("Decide which explanation is more credible and make the decisive contrast explicit."),
    _comparison_case("Identify the stronger option and tie your conclusion to the evidence rather than preference."),
    _comparison_case("State which path is better supported and explain the critical difference briefly."),
    _comparison_case("Pick the more defensible recommendation and support it with the clearest evidence available."),
    _comparison_case("Determine which of the two accounts deserves more confidence and justify the choice."),

    # synthesis — grounded, with one extra subtle requirement
    _synthesis_case("Prepare a grounded summary from the fragments below, clearly separating observations from inference."),
    _synthesis_case("Write one concise evidence-based conclusion from the notes below, keeping observation and inference distinct."),
    _synthesis_case("Merge the findings into a short grounded answer while preserving what is observed versus inferred."),
    _synthesis_case("Produce a compact synthesis that stays close to the evidence and does not blur fact and inference."),
    _synthesis_case("Create a coherent evidence-grounded answer from the fragments, separating raw findings from conclusions."),
    _synthesis_case("Turn the scattered findings into one grounded explanation and keep the support structure visible."),

    # procedure — stable structure should matter
    _procedure_case("Extract the key fields below and return them in a stable, labeled layout."),
    _procedure_case("Convert the raw details into a clean checklist with explicit fields."),
    _procedure_case("Normalize the record into a structured handoff note with reusable field ordering."),
    _procedure_case("Reformat the details into a compact checklist for the next operator."),
    _procedure_case("Produce a field-oriented summary from the raw material below."),
    _procedure_case("Turn these details into a stable structured layout with labeled values."),
]
