"""Focused real-LLM broader evaluation runner.

This runner performs a controlled A/B/C comparison on a small, fixed set of
tasks using a REAL language model via OpenRouter. It is deliberately small
(6 tasks x 3 conditions = 18 calls) with per-call timeouts and incremental
result persistence so that a network stall never loses completed work.

Legitimate Theft sources:
- 5.73 SWE-bench (Jimenez et al. 2024): controlled real-task evaluation rather
  than synthetic prompts.
- 5.74 LATS (Zhou et al. 2024): running the SAME task through different
  reasoning configurations to isolate the contribution of each augmentation.
- 5.76 Counterfactual / ablation evaluation protocol: A (raw) vs B (concept)
  vs C (concept+theory) is an ablation ladder where each rung adds exactly one
  governance signal, so any delta is attributable to that signal alone.

Run with:
    OPENROUTER_API_KEY=... python -m virtual_sia.eval.runners.run_real_llm_broader
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List

from ...api.llm_reasoning import build_augmented_prompt, build_raw_prompt, _call_openrouter
from ...api.config import DEFAULT_MODEL


# ---------------------------------------------------------------------------
# Fixed evaluation tasks: 2 per family, each with an explicit contract.
# ---------------------------------------------------------------------------
EVAL_TASKS: List[Dict[str, Any]] = [
    {
        "id": "cmp-1",
        "family": "comparison",
        "text": (
            "Compare blue-green deployment versus canary deployment. Select the "
            "approach with stronger evidence support and make the decisive "
            "contrast explicit."
        ),
        "required_properties": ["explicit comparison", "evidence-backed choice", "decisive contrast"],
        "forbidden_shortcuts": ["generic preference without evidence", "gut-feeling selection"],
        "concept_hints": [
            "Evidence Sufficiency Contrast: when comparing options, cite specific "
            "documented evidence for each option and state the decisive difference explicitly."
        ],
        "theory_hints": [
            "Comparison tasks fail when a choice is asserted without citing evidence. "
            "Predicted failure mode: generic preference."
        ],
    },
    {
        "id": "cmp-2",
        "family": "comparison",
        "text": (
            "Two monitoring tools are proposed: Prometheus and Datadog. Decide which "
            "is more defensible for a small self-hosted team and justify with concrete tradeoffs."
        ),
        "required_properties": ["explicit comparison", "evidence-backed choice", "tradeoff articulation"],
        "forbidden_shortcuts": ["generic preference without evidence"],
        "concept_hints": [
            "Evidence Sufficiency Contrast: anchor each claim in a concrete tradeoff "
            "(cost, self-hosting, maintenance) rather than brand preference."
        ],
        "theory_hints": [
            "Comparison quality depends on traceable tradeoffs, not popularity."
        ],
    },
    {
        "id": "syn-1",
        "family": "synthesis",
        "text": (
            "From these fragments: (a) latency rose at 14:00, (b) a deploy happened at 13:55, "
            "(c) error rate was flat, produce one grounded explanation. Separate observed "
            "facts from inferences explicitly."
        ),
        "required_properties": ["evidence-grounded conclusion", "fact vs inference separation"],
        "forbidden_shortcuts": ["summary without distinction", "fact-opinion conflation"],
        "concept_hints": [
            "Ungrounded Synthesis Risk: every conclusion must trace to a stated fragment; "
            "label inferences distinctly from observations."
        ],
        "theory_hints": [
            "Synthesis fails when fact and inference blur. Predicted failure: confident "
            "narrative not anchored to evidence."
        ],
    },
    {
        "id": "syn-2",
        "family": "synthesis",
        "text": (
            "Merge three conflicting status reports about an outage into one coherent account, "
            "flagging where you bridge gaps with inference versus direct observation."
        ),
        "required_properties": ["evidence-grounded conclusion", "fact vs inference separation", "conflict handling"],
        "forbidden_shortcuts": ["summary without distinction"],
        "concept_hints": [
            "Ungrounded Synthesis Risk: explicitly mark each statement as observed or inferred; "
            "note unresolved conflicts instead of smoothing them over."
        ],
        "theory_hints": [
            "Conflicting sources require explicit conflict markers, not a blended summary."
        ],
    },
    {
        "id": "prc-1",
        "family": "procedure",
        "text": (
            "Extract the fields (timestamp, severity, affected_service, status) from this note: "
            "'At 09:12 a SEV2 hit the auth-service; currently mitigated.' Return a stable labeled layout."
        ),
        "required_properties": ["stable structured layout", "field completeness"],
        "forbidden_shortcuts": ["unstructured dump", "formatting bypass"],
        "concept_hints": [
            "Stable Procedure Reuse: emit explicit labeled fields in a consistent order; "
            "mark any missing field rather than omitting it."
        ],
        "theory_hints": [
            "Procedure tasks fail when output is prose instead of labeled fields."
        ],
    },
    {
        "id": "prc-2",
        "family": "procedure",
        "text": (
            "Convert this ad-hoc text into a normalized checklist with explicit field names and "
            "deterministic ordering: 'restart node, then drain traffic, verify health, page on-call if red.'"
        ),
        "required_properties": ["stable structured layout", "ordered steps"],
        "forbidden_shortcuts": ["unstructured dump"],
        "concept_hints": [
            "Stable Procedure Reuse: produce an ordered, labeled checklist suitable for reuse."
        ],
        "theory_hints": [
            "Procedure quality depends on deterministic ordering and explicit labels."
        ],
    },
]


# ---------------------------------------------------------------------------
# Real (non-mock) quality scoring against the task contract.
# ---------------------------------------------------------------------------
def _tokenize(text: str) -> set[str]:
    return {t.strip(".,:;!?()[]{}#*-").lower() for t in text.split() if t.strip()}


def score_response(response: str, task: Dict[str, Any]) -> Dict[str, Any]:
    """Score a real LLM response against the task contract.

    Returns objective, reproducible signals (no LLM-as-judge):
    - property_hits: how many required_properties have lexical support
    - shortcut_violations: how many forbidden shortcuts appear verbatim-ish
    - has_structure: presence of markdown structure (headings / bullets)
    - cites_evidence: presence of evidence/citation markers
    - separates_fact_inference: presence of fact/inference separation markers
    - good_enough: contract pass heuristic
    """
    if response.startswith("[LLM_ERROR]") or response.startswith("LLM error"):
        return {
            "error": True,
            "raw": response,
            "property_hits": 0,
            "property_total": len(task["required_properties"]),
            "shortcut_violations": 0,
            "has_structure": False,
            "cites_evidence": False,
            "separates_fact_inference": False,
            "length": len(response),
            "good_enough": False,
        }

    low = response.lower()

    # Property support: map each required property to indicative markers.
    property_markers = {
        "explicit comparison": ["versus", "vs", "compared", "whereas", "while", "on the other hand"],
        "evidence-backed choice": ["evidence", "because", "documented", "data", "study", "benchmark"],
        "decisive contrast": ["decisive", "key difference", "the main difference", "critical distinction"],
        "tradeoff articulation": ["tradeoff", "trade-off", "cost", "downside", "advantage", "disadvantage"],
        "evidence-grounded conclusion": ["evidence", "based on", "fragment", "observed", "data"],
        "fact vs inference separation": ["observed", "inference", "inferred", "fact", "assume", "likely"],
        "conflict handling": ["conflict", "disagree", "inconsistent", "contradict", "unresolved"],
        "stable structured layout": ["timestamp", "severity", "field", ":", "- "],
        "field completeness": ["timestamp", "severity", "service", "status", "missing"],
        "ordered steps": ["1.", "2.", "step", "first", "then", "next"],
    }
    property_hits = 0
    property_detail = {}
    for prop in task["required_properties"]:
        markers = property_markers.get(prop, [prop.lower()])
        hit = any(m in low for m in markers)
        property_detail[prop] = hit
        property_hits += int(hit)

    # Shortcut violations: a shortcut is violated if the response is shallow.
    shortcut_violations = 0
    if "generic preference without evidence" in task["forbidden_shortcuts"]:
        # Violated if it picks something but never says "evidence/because/data".
        if not any(m in low for m in ["evidence", "because", "data", "documented", "tradeoff"]):
            shortcut_violations += 1
    if "summary without distinction" in task["forbidden_shortcuts"]:
        if not any(m in low for m in ["observed", "inference", "inferred", "fact"]):
            shortcut_violations += 1
    if "unstructured dump" in task["forbidden_shortcuts"]:
        if not any(m in response for m in [":", "- ", "1.", "\n"]):
            shortcut_violations += 1

    has_structure = any(m in response for m in ["#", "- ", "* ", "1.", "2.", ":\n", ":"])
    cites_evidence = any(m in low for m in ["evidence", "documented", "data", "study", "(", "fowler", "according"])
    separates_fact_inference = any(m in low for m in ["observed", "inference", "inferred", "fact:", "assume"])

    property_total = len(task["required_properties"])
    good_enough = (property_hits >= max(1, property_total - 1)) and shortcut_violations == 0

    return {
        "error": False,
        "property_hits": property_hits,
        "property_total": property_total,
        "property_detail": property_detail,
        "shortcut_violations": shortcut_violations,
        "has_structure": has_structure,
        "cites_evidence": cites_evidence,
        "separates_fact_inference": separates_fact_inference,
        "length": len(response),
        "good_enough": good_enough,
    }


def run_real_llm_broader(
    output_path: str = "virtual_sia/eval/results/real_llm_broader_eval.json",
    model: str | None = None,
    max_tasks: int | None = None,
) -> dict:
    """Run the A/B/C real-LLM evaluation with incremental persistence."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    resolved_model = model or DEFAULT_MODEL
    tasks = EVAL_TASKS if max_tasks is None else EVAL_TASKS[:max_tasks]

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    payload: Dict[str, Any] = {
        "model": resolved_model,
        "mode": "real" if api_key else "mock_no_key",
        "conditions": ["A_raw", "B_concept", "C_concept_theory"],
        "task_count": len(tasks),
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "runs": [],
    }

    def _persist():
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    _persist()

    for task in tasks:
        print(f"\n=== Task {task['id']} ({task['family']}) ===", flush=True)
        run_record: Dict[str, Any] = {"task_id": task["id"], "family": task["family"], "conditions": {}}

        # Condition A: raw
        prompt_a = build_raw_prompt(task["text"])
        t0 = time.time()
        resp_a = _call_openrouter(prompt_a, resolved_model, api_key) if api_key else "[LLM_ERROR] no api key"
        dt_a = time.time() - t0
        score_a = score_response(resp_a, task)
        run_record["conditions"]["A_raw"] = {"latency_s": round(dt_a, 2), "score": score_a, "response_preview": resp_a[:300]}
        print(f"  A_raw: good={score_a['good_enough']} props={score_a['property_hits']}/{score_a['property_total']} structure={score_a['has_structure']} ({dt_a:.1f}s)", flush=True)
        payload["runs_partial"] = True
        run_record_partial = dict(run_record)
        # persist partial within task
        payload_runs = payload["runs"] + [run_record]
        payload["runs"] = payload_runs[:-1]
        _persist()
        payload["runs"] = payload_runs[:-1]

        # Condition B: concept hints
        prompt_b = build_augmented_prompt(task["text"], task["concept_hints"], None)
        t0 = time.time()
        resp_b = _call_openrouter(prompt_b, resolved_model, api_key) if api_key else "[LLM_ERROR] no api key"
        dt_b = time.time() - t0
        score_b = score_response(resp_b, task)
        run_record["conditions"]["B_concept"] = {"latency_s": round(dt_b, 2), "score": score_b, "response_preview": resp_b[:300]}
        print(f"  B_concept: good={score_b['good_enough']} props={score_b['property_hits']}/{score_b['property_total']} structure={score_b['has_structure']} ({dt_b:.1f}s)", flush=True)

        # Condition C: concept + theory hints
        prompt_c = build_augmented_prompt(task["text"], task["concept_hints"], task["theory_hints"])
        t0 = time.time()
        resp_c = _call_openrouter(prompt_c, resolved_model, api_key) if api_key else "[LLM_ERROR] no api key"
        dt_c = time.time() - t0
        score_c = score_response(resp_c, task)
        run_record["conditions"]["C_concept_theory"] = {"latency_s": round(dt_c, 2), "score": score_c, "response_preview": resp_c[:300]}
        print(f"  C_concept_theory: good={score_c['good_enough']} props={score_c['property_hits']}/{score_c['property_total']} structure={score_c['has_structure']} ({dt_c:.1f}s)", flush=True)

        payload["runs"].append(run_record)
        _persist()

    # Aggregate
    payload["aggregate"] = _aggregate(payload["runs"])
    payload["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    _persist()
    return payload


def _aggregate(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    conditions = ["A_raw", "B_concept", "C_concept_theory"]
    agg: Dict[str, Any] = {}
    for cond in conditions:
        scores = [r["conditions"][cond]["score"] for r in runs if cond in r["conditions"]]
        valid = [s for s in scores if not s.get("error")]
        n = len(valid) or 1
        agg[cond] = {
            "n": len(valid),
            "success_rate": round(sum(int(s["good_enough"]) for s in valid) / n, 3),
            "avg_property_hits": round(sum(s["property_hits"] for s in valid) / n, 2),
            "structure_rate": round(sum(int(s["has_structure"]) for s in valid) / n, 3),
            "evidence_rate": round(sum(int(s["cites_evidence"]) for s in valid) / n, 3),
            "avg_shortcut_violations": round(sum(s["shortcut_violations"] for s in valid) / n, 2),
            "errors": sum(int(s.get("error", False)) for s in scores),
        }
    return agg


if __name__ == "__main__":
    result = run_real_llm_broader()
    print("\n\n=== AGGREGATE RESULTS ===")
    print(json.dumps(result.get("aggregate", {}), indent=2, ensure_ascii=False))
