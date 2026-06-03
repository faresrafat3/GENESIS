from __future__ import annotations

from ...core.objects.task_case import TaskCase


def _comparison_case(prompt: str) -> TaskCase:
    case = TaskCase.create(prompt, expected_primary_family="comparison")
    case.required_properties = ["explicit comparison", "evidence-backed choice"]
    case.forbidden_shortcuts = ["generic preference without evidence", "summary without distinction"]
    case.diagnostic_purpose = ["thesis_1_core", "comparison_quality"]
    case.target_thesis = ["thesis_1", "thesis_2"]
    return case


def _synthesis_case(prompt: str) -> TaskCase:
    case = TaskCase.create(prompt, expected_primary_family="synthesis")
    case.required_properties = ["evidence-grounded conclusion"]
    case.forbidden_shortcuts = ["summary without distinction"]
    case.diagnostic_purpose = ["thesis_1_core", "synthesis_grounding"]
    case.target_thesis = ["thesis_1", "thesis_2"]
    return case


def _procedure_case(prompt: str) -> TaskCase:
    case = TaskCase.create(prompt, expected_primary_family="procedure")
    case.required_properties = ["stable structured layout"]
    case.forbidden_shortcuts = []
    case.diagnostic_purpose = ["procedure_reuse"]
    case.target_thesis = ["thesis_1", "thesis_2"]
    return case


PROTOTYPE_V3_CASES = [
    _comparison_case("Given the two remediation notes below, determine which path is more defensible for a production review and justify your conclusion with the strongest available support."),
    _comparison_case("You are preparing a release recommendation: decide which proposal is safer and explain the decisive difference using the evidence provided."),
    _comparison_case("Review the two incident narratives and state which one better explains the outage, along with the most important supporting clue."),
    _comparison_case("For the final approval note, judge which migration option carries lower operational risk and support the judgment from the record."),
    _comparison_case("Between the two hypotheses below, indicate which one deserves more confidence and show the basis for that confidence."),
    _comparison_case("Choose the stronger of the two root-cause accounts and make the distinction explicit for an auditor."),
    _synthesis_case("Prepare a final incident update from the fragments below. The update must stay close to the evidence and avoid unsupported claims."),
    _synthesis_case("Draft a concise executive answer from the notes below while making clear what is observed versus what is inferred."),
    _synthesis_case("Turn the following fragments into one short status explanation that preserves the evidence trail."),
    _synthesis_case("A reviewer needs one grounded answer from these scattered findings; write it without collapsing distinct pieces of support."),
    _synthesis_case("Produce a compact recommendation from the material below, making sure every major point remains traceable to supporting detail."),
    _synthesis_case("Write a single coherent conclusion from the observations below, but keep the support structure visible."),
    _procedure_case("Prepare an operator handoff checklist from the raw details below, keeping the fields stable and easy to scan."),
    _procedure_case("Turn the record into a reusable handoff format with labeled values and a clean ordering."),
    _procedure_case("An operator needs this mess converted into a dependable checklist. Extract the important fields and normalize the layout."),
    _procedure_case("Rework the details below into a compact, repeatable handoff structure for the next shift."),
    _procedure_case("Build a clean field-oriented summary from the raw input below so that another operator can follow it quickly."),
    _procedure_case("Convert the unstructured details into a consistent checklist and preserve the key attributes without noise."),
]
