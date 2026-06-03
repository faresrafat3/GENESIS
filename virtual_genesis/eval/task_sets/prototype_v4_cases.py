from __future__ import annotations

from ...core.objects.task_case import TaskCase


PROTOTYPE_V4_CASES = []


def _case(prompt, primary, secondary, overlap, required, forbidden, diagnostic):
    case = TaskCase.create(prompt, expected_primary_family=primary)
    case.expected_secondary_families = secondary
    case.family_overlap_type = overlap
    case.required_properties = required
    case.forbidden_shortcuts = forbidden
    case.diagnostic_purpose = diagnostic
    case.target_thesis = ["thesis_1", "thesis_2"]
    return case


PROTOTYPE_V4_CASES.extend([
    _case(
        "Prepare a release recommendation that decides which option is safer, but present the decisive evidence in a handoff-ready summary.",
        "comparison",
        ["procedure"],
        "comparison_procedure_overlap",
        ["explicit comparison", "evidence-backed choice", "handoff-usable structure"],
        ["generic preference without evidence", "structure without a decision", "decision without structure"],
        ["stress comparison-procedure overlap"],
    ),
    _case(
        "Turn the scattered findings below into a handoff note that still makes the strongest contrast between the two explanations explicit.",
        "synthesis",
        ["comparison", "procedure"],
        "comparison_synthesis_procedure_overlap",
        ["explicit comparison", "evidence-grounded conclusion", "handoff-usable structure"],
        ["summary without distinction", "generic preference without evidence"],
        ["stress multi-frame overlap"],
    ),
    _case(
        "For the audit note below, decide which explanation is better supported and return the key supporting fields in a clean structure.",
        "comparison",
        ["procedure"],
        "comparison_procedure_overlap",
        ["explicit comparison", "evidence-backed choice", "handoff-usable structure"],
        ["generic preference without evidence", "decision without structure"],
        ["stress comparison+procedure"],
    ),
    _case(
        "Create an operator-ready incident summary from the fragments below, making clear what evidence justifies the next step.",
        "synthesis",
        ["procedure"],
        "synthesis_procedure_overlap",
        ["evidence-grounded conclusion", "handoff-usable structure"],
        ["summary without distinction"],
        ["stress synthesis+procedure"],
    ),
    _case(
        "Choose the more defensible migration path and present the decisive fields as a compact checklist for approval.",
        "comparison",
        ["procedure"],
        "comparison_procedure_overlap",
        ["explicit comparison", "evidence-backed choice", "handoff-usable structure"],
        ["generic preference without evidence", "decision without structure"],
        ["stress comparison+procedure"],
    ),
    _case(
        "Build a concise, grounded handoff summary that merges the observations while separating what is known from what is inferred.",
        "synthesis",
        ["procedure"],
        "synthesis_procedure_overlap",
        ["evidence-grounded conclusion", "fact vs inference separation", "handoff-usable structure"],
        ["summary without distinction"],
        ["stress synthesis grounding"],
    ),
    _case(
        "From the two proposed actions below, identify the stronger one and convert the critical evidence into a reusable operator note.",
        "comparison",
        ["synthesis", "procedure"],
        "comparison_synthesis_procedure_overlap",
        ["explicit comparison", "evidence-backed choice", "handoff-usable structure"],
        ["generic preference without evidence"],
        ["stress three-way overlap"],
    ),
    _case(
        "Prepare a structured final note from these fragments so a reviewer can both see the main conclusion and inspect the supporting signals.",
        "synthesis",
        ["procedure"],
        "synthesis_procedure_overlap",
        ["evidence-grounded conclusion", "handoff-usable structure"],
        ["summary without distinction"],
        ["stress synthesis structure"],
    ),
    _case(
        "Extract the operational fields from the two competing notes and make the more credible path obvious in the final layout.",
        "procedure",
        ["comparison"],
        "procedure_comparison_overlap",
        ["handoff-usable structure", "explicit comparison"],
        ["structure without a decision"],
        ["stress procedure+comparison"],
    ),
    _case(
        "Normalize the handoff details below into a checklist while preserving which findings actually support the recommended choice.",
        "procedure",
        ["synthesis"],
        "procedure_synthesis_overlap",
        ["handoff-usable structure", "evidence-grounded conclusion"],
        ["structure without a decision"],
        ["stress procedure+synthesis"],
    ),
    _case(
        "Produce a reusable operator checklist from the raw material below, but ensure the most important difference between the two options remains visible.",
        "procedure",
        ["comparison"],
        "procedure_comparison_overlap",
        ["handoff-usable structure", "explicit comparison"],
        ["structure without a decision"],
        ["stress procedure+comparison"],
    ),
    _case(
        "Rework the fragmented details into a stable field-oriented summary for the next shift, keeping the recommendation tightly grounded.",
        "procedure",
        ["synthesis"],
        "procedure_synthesis_overlap",
        ["handoff-usable structure", "evidence-grounded conclusion"],
        ["summary without distinction"],
        ["stress procedure+synthesis"],
    ),
])
