"""Tests for task ingress: ingest_task and classify_task_family."""
from __future__ import annotations

from virtual_genesis.core.objects.task_case import TaskCase
from virtual_genesis.runtime.task_ingress.service import ingest_task, classify_task_family


def test_ingest_task_raw_string():
    """ingest_task with a comparison-style string should classify task_family as 'comparison'."""
    task = ingest_task("Compare these two options and identify the key difference")
    assert task.task_family == "comparison"
    assert task.normalized_text != ""


def test_ingest_task_with_taskcase():
    """ingest_task with a TaskCase should preserve expected_primary_family in meta."""
    case = TaskCase.create(
        prompt_text="Synthesize the findings from these three reports",
        expected_primary_family="synthesis",
    )
    task = ingest_task(case)
    envelope = (task.meta or {}).get("normalized_envelope", {})
    assert envelope.get("expected_primary_family") == "synthesis"
    assert task.meta.get("expected_primary_family") == "synthesis"


def test_classify_task_family_known_prompts():
    """classify_task_family should correctly classify known prompts for each family."""
    comparison_text = "compare these two proposals and choose the better one"
    synthesis_text = "synthesize the findings into a coherent summary"
    procedure_text = "extract the fields and format them as a checklist"

    family_c, scores_c, _, _ = classify_task_family(comparison_text)
    assert family_c == "comparison", f"Expected comparison, got {family_c} with scores {scores_c}"

    family_s, scores_s, _, _ = classify_task_family(synthesis_text)
    assert family_s == "synthesis", f"Expected synthesis, got {family_s} with scores {scores_s}"

    family_p, scores_p, _, _ = classify_task_family(procedure_text)
    assert family_p == "procedure", f"Expected procedure, got {family_p} with scores {scores_p}"
