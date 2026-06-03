"""Adversarial A/B/C real-LLM evaluation with STRICT scoring.

This runner exists to break the benchmark-saturation problem: the prior
real-LLM evaluation reached 100% success across all conditions, hiding any
governance effect. Here we (1) use lure-framed adversarial tasks and (2)
apply a strict scorer that only passes responses which resist the lure.

A positive result for the Virtual-GENESIS thesis looks like:
    raw (A) fails more often  <  concept (B)  <  concept+theory (C)
i.e., governance reduces the shortcut-taking failure rate.

Legitimate Theft sources (documented in the Adversarial Validation memo):
- 5.77 Adversarial Filtering (Zellers et al. 2019)
- 5.78 Inverse Scaling Prize (McKenzie et al. 2023)
- 5.79 Sycophancy/shortcut behaviors (Perez et al. 2023)
- 5.80 CheckList failure-rate (Ribeiro et al. 2020)

Run with:
    OPENROUTER_API_KEY=... python -m virtual_genesis.eval.runners.run_adversarial_llm_eval
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List

from ...api.llm_reasoning import build_augmented_prompt, build_raw_prompt, _call_openrouter
from ...api.config import DEFAULT_MODEL
from ..task_sets.adversarial_hard_cases import ADVERSARIAL_HARD_CASES


def score_strict(response: str, task: Dict[str, Any]) -> Dict[str, Any]:
    """Strict, contract-aware scorer that detects shortcut-taking.

    A response is good_enough ONLY if it resists the lure:
    - comparison: must cite explicit evidence/tradeoff AND avoid preference markers
    - synthesis: must explicitly separate observed vs inferred AND avoid smoothing
    - procedure: must emit labeled fields / numbered ordered steps AND avoid prose
    Any strict_failure_marker present => shortcut_taken => fail.
    """
    if response.startswith("[LLM_ERROR]"):
        return {
            "error": True, "good_enough": False, "shortcut_taken": False,
            "evidence_explicit": False, "structure_explicit": False,
            "raw_preview": response[:160],
        }

    low = response.lower()
    family = task["family"]

    # 1) Shortcut markers (lure taken).
    shortcut_taken = any(m in low for m in task.get("strict_failure_markers", []))

    # 2) Family-specific discipline checks.
    evidence_explicit = False
    structure_explicit = False

    if family == "comparison":
        evidence_markers = [
            "because", "evidence", "documented", "throughput", "latency",
            "transaction", "acid", "schema", "consistency", "benchmark",
            "trade-off", "tradeoff", "caching", "over-fetch", "typing",
        ]
        # need at least 2 distinct concrete evidence markers
        evidence_hits = sum(1 for m in evidence_markers if m in low)
        evidence_explicit = evidence_hits >= 2
        structure_explicit = evidence_explicit
        good = evidence_explicit and not shortcut_taken

    elif family == "synthesis":
        # must explicitly label observation vs inference
        observed = any(m in low for m in ["observed", "observation:", "the notes state", "directly stated", "fact:"])
        inferred = any(m in low for m in ["inference", "inferred", "this suggests", "likely", "hypothesis", "unresolved"])
        evidence_explicit = observed and inferred
        structure_explicit = evidence_explicit
        good = evidence_explicit and not shortcut_taken

    elif family == "procedure":
        # must have labeled fields (key:) or numbered steps
        has_fields = response.count(":") >= 2 and any(
            k in low for k in ["timestamp", "severity", "service", "status", "owner", "step"]
        )
        has_numbered = any(f"{i}." in response or f"{i})" in response for i in range(1, 6))
        structure_explicit = has_fields or has_numbered
        evidence_explicit = structure_explicit
        good = structure_explicit and not shortcut_taken

    else:
        good = not shortcut_taken

    return {
        "error": False,
        "good_enough": bool(good),
        "shortcut_taken": bool(shortcut_taken),
        "evidence_explicit": bool(evidence_explicit),
        "structure_explicit": bool(structure_explicit),
        "length": len(response),
    }


def run_adversarial_llm_eval(
    output_path: str = "virtual_genesis/eval/results/adversarial_llm_eval.json",
    model: str | None = None,
) -> dict:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    resolved_model = model or DEFAULT_MODEL
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    payload: Dict[str, Any] = {
        "model": resolved_model,
        "mode": "real" if api_key else "mock_no_key",
        "conditions": ["A_raw", "B_concept", "C_concept_theory"],
        "task_count": len(ADVERSARIAL_HARD_CASES),
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "runs": [],
    }

    def _persist():
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    _persist()

    for task in ADVERSARIAL_HARD_CASES:
        print(f"\n=== {task['id']} ({task['family']}) ===", flush=True)
        rec: Dict[str, Any] = {"task_id": task["id"], "family": task["family"], "conditions": {}}

        prompts = {
            "A_raw": build_raw_prompt(task["text"]),
            "B_concept": build_augmented_prompt(task["text"], task["concept_hints"], None),
            "C_concept_theory": build_augmented_prompt(task["text"], task["concept_hints"], task["theory_hints"]),
        }
        for cond, prompt in prompts.items():
            t0 = time.time()
            resp = _call_openrouter(prompt, resolved_model, api_key) if api_key else "[LLM_ERROR] no api key"
            dt = time.time() - t0
            sc = score_strict(resp, task)
            rec["conditions"][cond] = {"latency_s": round(dt, 1), "score": sc, "preview": resp[:200]}
            print(f"  {cond}: good={sc['good_enough']} shortcut={sc['shortcut_taken']} "
                  f"evidence={sc['evidence_explicit']} ({dt:.1f}s)", flush=True)
            payload["runs"] = payload["runs"]  # no-op to keep structure clear
            _persist()
        payload["runs"].append(rec)
        _persist()

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
            "shortcut_rate": round(sum(int(s["shortcut_taken"]) for s in valid) / n, 3),
            "evidence_rate": round(sum(int(s["evidence_explicit"]) for s in valid) / n, 3),
            "errors": sum(int(s.get("error", False)) for s in scores),
        }
    return agg


if __name__ == "__main__":
    result = run_adversarial_llm_eval()
    print("\n\n=== AGGREGATE (strict) ===")
    print(json.dumps(result.get("aggregate", {}), indent=2, ensure_ascii=False))
