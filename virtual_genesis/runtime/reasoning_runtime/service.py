from __future__ import annotations

from typing import Any, Dict, Sequence

from ...core.objects.cost import CostProfile


def _grounding_phrase(memory_pack: Any) -> str:
    if getattr(memory_pack, "concept_refs", None):
        return " Supported by concept-guided evidence framing."
    if getattr(memory_pack, "procedural_refs", None):
        return " Supported by retrieved procedural guidance."
    if getattr(memory_pack, "semantic_refs", None) or getattr(memory_pack, "episodic_refs", None):
        return " Supported by retrieved evidence context."
    return ""


def _concept_phrase(memory_pack: Any) -> str:
    hints = getattr(memory_pack, "concept_hints", None) or []
    if not hints:
        return ""
    top = hints[:2]
    return " Active concepts: " + " | ".join(top)


def _theory_phrase(memory_pack: Any) -> str:
    hints = getattr(memory_pack, "theory_hints", None) or []
    if not hints:
        return ""
    top = hints[:1]
    return " Active theory: " + " | ".join(top)


def _concept_directives(memory_pack: Any) -> dict[str, bool]:
    hints = " ".join(getattr(memory_pack, "concept_hints", None) or []).lower()
    return {
        "force_explicit_contrast": "explicit evidence-backed contrast" in hints or "generic preference" in hints,
        "force_observed_inferred_split": "separate observations from inference" in hints or "ungrounded synthesis" in hints,
        "force_checklist_reuse": "stable checklist" in hints or "field-oriented workflow" in hints,
        "avoid_generic_summary": "do not collapse the answer into a generic summary" in hints,
    }


def _theory_directives(memory_pack: Any) -> dict[str, bool]:
    hints = " ".join(getattr(memory_pack, "theory_hints", None) or []).lower()
    return {
        "theory_emphasize_contrast": "explicit evidence-backed contrast" in hints,
        "theory_emphasize_grounding": "grounded" in hints or "evidence" in hints,
        "theory_emphasize_structure": "checklist" in hints or "field-oriented" in hints,
    }


def _has(families: Sequence[str], target: str) -> bool:
    return target in families


def _brevity_pressure(task_text: str) -> bool:
    lowered = task_text.lower()
    return any(token in lowered for token in ["extremely brief", "very brief", "compact"]) 


def _render_comparison(task_text: str, families: Sequence[str], grounding: str, concept_phrase: str, theory_phrase: str, directives: dict[str, bool], theory_directives: dict[str, bool]) -> str:
    brief = _brevity_pressure(task_text)
    if brief and not directives.get("force_explicit_contrast", False):
        parts = [
            "Conclusion: Option A seems preferable.",
            "Supported by: the record favors it.",
        ]
    else:
        parts = [
            "Conclusion: Option A is safer or stronger than Option B based on the available support.",
            f"Supported by: the task asks for a defensible contrast grounded in the evidence from `{task_text[:90]}`.",
        ]
        if directives.get("force_explicit_contrast", False) or theory_directives.get("theory_emphasize_contrast", False):
            parts.append("Contrast: the decisive difference is explicit and tied to evidence quality, not generic preference.")
        else:
            parts.append("Contrast: the decisive difference is the quality and explicitness of the support behind the preferred option.")
    if _has(families, "procedure"):
        parts.append("Handoff checklist: decision=Option A | basis=evidence-backed contrast | status=ready for operator review.")
    if _has(families, "synthesis"):
        parts.append("Merged view: the comparison is presented as one grounded summary rather than disconnected notes.")
    return " ".join(parts) + grounding + concept_phrase + theory_phrase


def _render_synthesis(task_text: str, families: Sequence[str], grounding: str, concept_phrase: str, theory_phrase: str, directives: dict[str, bool], theory_directives: dict[str, bool]) -> str:
    brief = _brevity_pressure(task_text)
    parts = []
    if brief and not directives.get("avoid_generic_summary", False):
        parts.extend([
            "Summary: the evidence points toward one main grounded conclusion.",
            "Supported by: the available observations.",
        ])
    else:
        if directives.get("force_observed_inferred_split", False) or theory_directives.get("theory_emphasize_grounding", False):
            parts.extend([
                "Observed: the fragments provide multiple supporting signals that must be integrated rather than listed separately.",
                "Inferred: the conclusion below stays close to the observed evidence and avoids unsupported merging.",
            ])
        else:
            parts.extend([
                "Observed: the fragments provide multiple supporting signals that must be integrated rather than listed separately.",
                "Inferred: the strongest conclusion is the one that remains closest to the observed evidence without adding unsupported claims.",
            ])
        parts.append(f"Supported by: the prompt requests a grounded merged answer from `{task_text[:90]}`.")
    if _has(families, "comparison"):
        parts.append("Contrast: where two explanations compete, preference should follow the explanation with clearer evidence support.")
    if _has(families, "procedure"):
        parts.append("Checklist: observed facts captured | inference separated | handoff layout ready.")
    if directives.get("avoid_generic_summary", False):
        parts.append("Distinction preserved: the answer must not collapse into a generic summary that hides decisive support.")
    return " ".join(parts) + grounding + concept_phrase + theory_phrase


def _render_procedure(task_text: str, families: Sequence[str], grounding: str, concept_phrase: str, theory_phrase: str, directives: dict[str, bool], theory_directives: dict[str, bool]) -> str:
    parts = [
        "Checklist:",
        "- field_1: extracted and normalized",
        "- field_2: extracted and normalized",
        "- layout: stable and operator-friendly",
    ]
    if directives.get("force_checklist_reuse", False) or theory_directives.get("theory_emphasize_structure", False):
        parts.append("Workflow note: use a repeatable field-oriented checklist rather than an ad hoc summary.")
    if _has(families, "comparison"):
        parts.append("Decision note: Option A is the more credible or safer path when a contrast is required.")
    if _has(families, "synthesis"):
        parts.append("Summary note: the fields preserve the grounded conclusion without losing evidence support.")
    return " ".join(parts) + grounding + concept_phrase + theory_phrase


def _render_family_answer(task_family: str, task_text: str, families: Sequence[str], grounding: str, concept_phrase: str, theory_phrase: str, directives: dict[str, bool], theory_directives: dict[str, bool], chosen_tier: str) -> str:
    if task_family == "comparison":
        base = _render_comparison(task_text, families, grounding, concept_phrase, theory_phrase, directives, theory_directives)
    elif task_family == "synthesis":
        base = _render_synthesis(task_text, families, grounding, concept_phrase, theory_phrase, directives, theory_directives)
    elif task_family == "procedure":
        base = _render_procedure(task_text, families, grounding, concept_phrase, theory_phrase, directives, theory_directives)
    else:
        base = f"Task family: {task_family}. Provisional answer for: {task_text[:180]}.{grounding}{concept_phrase}{theory_phrase}"

    if chosen_tier == "tier_2":
        base += " Premium reasoning applied for stronger grounding and safer finalization."
    return base.strip()


def run_reasoning(
    task_text: str,
    task_family: str,
    memory_pack: Dict[str, Any] | None = None,
    chosen_tier: str = "tier_1",
    framing_candidates: Sequence[str] | None = None,
) -> Dict[str, Any]:
    memory_pack = memory_pack or {}
    families = list(framing_candidates or [task_family])
    if task_family not in families:
        families.insert(0, task_family)

    grounding = _grounding_phrase(memory_pack)
    concept_phrase = _concept_phrase(memory_pack)
    theory_phrase = _theory_phrase(memory_pack)
    directives = _concept_directives(memory_pack)
    theory_directives = _theory_directives(memory_pack)
    answer = _render_family_answer(task_family, task_text, families, grounding, concept_phrase, theory_phrase, directives, theory_directives, chosen_tier)

    if chosen_tier == "tier_0":
        est_cost = 0.0
        latency = 120
        confidence = 0.35
    elif chosen_tier == "tier_1":
        est_cost = 0.001
        latency = 350
        confidence = 0.65
    else:
        est_cost = 0.01
        latency = 900
        confidence = 0.82

    return {
        "candidate_claims": [
            {
                "claim_id": f"claim_{task_family}_{chosen_tier}",
                "claim_text": answer,
                "confidence": confidence,
                "status": "draft",
            }
        ],
        "cost_profile": CostProfile(
            prompt_tokens=max(1, len(task_text.split())),
            completion_tokens=max(1, len(answer.split())),
            total_tokens=max(1, len(task_text.split()) + len(answer.split())),
            latency_ms=latency,
            estimated_cost_usd=est_cost,
            premium_share=1.0 if chosen_tier == "tier_2" else 0.0,
        ),
        "notes": f"reasoning executed on {chosen_tier}",
    }
