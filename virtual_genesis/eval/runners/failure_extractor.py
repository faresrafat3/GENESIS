"""Failure Extractor — convert evaluation results into Negative Memory records.

Scans generation directories for evaluation_results.json (the real accuracy
data) and agent_execution.json (the execution metadata), then extracts
individual failure records suitable for feeding into
generate_from_negative_memory().

This is the bridge between the orchestrator's per-generation artifacts and
the Negative Memory → Adversarial Test pipeline (T-13 → H8).

Sources extracted:
    1. evaluation_results.json → wrong_answer failures (per question)
    2. agent_execution.json → structural failures (pipeline issues)
    3. Cross-generation recurrence tracking

Reference: GENESIS/PAPER/analysis/REGIME_TRANSITION_INJECTION_ROADMAP.md Phase 2
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple


# ── Types ─────────────────────────────────────────────────────────────────

FailureRecord = Dict[str, Any]


# ── Main Extractor ────────────────────────────────────────────────────────


def extract_failures_from_generation(
    gen_dir: str,
    *,
    gen_num: int = 0,
    max_failures: int = 50,
) -> List[FailureRecord]:
    """Extract all failure records from a single generation directory.

    Looks for:
    - evaluation_results.json → wrong_answer failures (per-question)
    - agent_execution.json → structural failures

    Args:
        gen_dir: path to the generation directory (e.g., runs/run_1/gen_2)
        gen_num: generation number for metadata
        max_failures: cap on number of failures to return (avoid overload)

    Returns:
        List of failure dicts compatible with generate_from_negative_memory().
    """
    failures: List[FailureRecord] = []

    # Source 1: evaluation_results.json — per-question wrong answers
    failures.extend(
        _extract_from_eval_results(gen_dir, gen_num=gen_num)
    )

    # Source 2: agent_execution.json — structural/pipeline failures
    failures.extend(
        _extract_from_execution_log(gen_dir, gen_num=gen_num)
    )

    # Cap to avoid overwhelming the system
    if len(failures) > max_failures:
        # Keep the most severe ones
        failures.sort(key=lambda f: f.get("severity", 0.5), reverse=True)
        failures = failures[:max_failures]

    return failures


def extract_failures_across_generations(
    run_dir: str,
    max_gen: int = 10,
    *,
    max_total: int = 100,
) -> Tuple[List[FailureRecord], Dict[str, int]]:
    """Extract failures from all generations in a run, with recurrence tracking.

    Scans gen_1 through gen_{max_gen}, extracts failures from each, then
    counts recurrence: if the same question_id was wrong in multiple gens,
    its recurrence_count is incremented.

    Args:
        run_dir: path to the run directory (e.g., runs/run_1)
        max_gen: maximum generation number to scan
        max_total: cap on total failures returned

    Returns:
        Tuple of (failures, stats) where stats has extraction metadata.
    """
    all_failures: List[FailureRecord] = []
    # Track recurrence by question_id
    recurrence_map: Dict[str, int] = {}
    stats = {
        "generations_scanned": 0,
        "total_failures_extracted": 0,
        "recurring_failures": 0,
    }

    for gen_num in range(1, max_gen + 1):
        gen_dir = os.path.join(run_dir, f"gen_{gen_num}")
        if not os.path.isdir(gen_dir):
            break

        gen_failures = extract_failures_from_generation(gen_dir, gen_num=gen_num)
        stats["generations_scanned"] += 1

        for failure in gen_failures:
            # Use a stable key that doesn't include gen_num for recurrence tracking
            qid = str(failure.get("id", ""))
            # Strip _genN suffix for stable recurrence key
            stable_qid = qid.rsplit("_gen", 1)[0] if "_gen" in qid else qid
            key = f"{failure.get('task_family', '')}|{stable_qid}"

            if key in recurrence_map:
                recurrence_map[key] += 1
            else:
                recurrence_map[key] = 1

            all_failures.append(failure)

    # Update recurrence_count on each failure
    for failure in all_failures:
        qid = str(failure.get("id", ""))
        key = f"{failure.get('task_family', '')}|{qid}"
        failure["recurrence_count"] = recurrence_map.get(key, 1)

    stats["total_failures_extracted"] = len(all_failures)
    stats["recurring_failures"] = sum(
        1 for v in recurrence_map.values() if v > 1
    )

    # Deduplicate: keep the one with highest recurrence from each key
    if len(all_failures) > max_total:
        seen: Dict[str, FailureRecord] = {}
        for f in all_failures:
            qid = str(f.get("id", ""))
            key = f"{f.get('task_family', '')}|{qid}"
            existing = seen.get(key)
            if existing is None or f.get("recurrence_count", 0) > existing.get("recurrence_count", 0):
                seen[key] = f
        all_failures = list(seen.values())
        # Sort by severity * recurrence
        all_failures.sort(
            key=lambda f: f.get("severity", 0.5) * f.get("recurrence_count", 1),
            reverse=True,
        )
        all_failures = all_failures[:max_total]

    return all_failures, stats


def extract_accuracy_from_gen(
    gen_dir: str,
) -> Optional[float]:
    """Extract accuracy from a generation's evaluation results.

    Looks in evaluation_results.json first (real accuracy), then falls back
    to agent_execution.json.

    Returns:
        Accuracy as a float 0.0-1.0, or None if not found.
    """
    # Priority 1: evaluation_results.json
    eval_path = os.path.join(gen_dir, "evaluation_results.json")
    if os.path.exists(eval_path):
        try:
            with open(eval_path, encoding="utf-8") as f:
                data = json.load(f)
            if "accuracy" in data:
                return float(data["accuracy"])
            if "accuracy_percent" in data:
                return float(data["accuracy_percent"]) / 100.0
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

    # Priority 2: results.json
    results_path = os.path.join(gen_dir, "results.json")
    if os.path.exists(results_path):
        try:
            with open(results_path, encoding="utf-8") as f:
                data = json.load(f)
            if "accuracy" in data:
                acc = data["accuracy"]
                if isinstance(acc, str):
                    return float(acc.rstrip("%")) / 100.0
                return float(acc)
            if "overall_score" in data:
                return float(data["overall_score"])
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

    # Priority 3: agent_execution.json
    exec_path = os.path.join(gen_dir, "agent_execution.json")
    if os.path.exists(exec_path):
        try:
            with open(exec_path, encoding="utf-8") as f:
                data = json.load(f)
            if "accuracy" in data:
                acc = data["accuracy"]
                if isinstance(acc, (int, float)) and acc > 0:
                    # Could be 0-1 or 0-100
                    if acc > 1.0:
                        return acc / 100.0
                    return float(acc)
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

    return None


def build_accuracy_history(
    run_dir: str,
    max_gen: int = 10,
) -> List[float]:
    """Build chronological accuracy history from a run's generations.

    Returns:
        List of accuracy values, one per generation that has eval data.
    """
    history: List[float] = []
    for gen_num in range(1, max_gen + 1):
        gen_dir = os.path.join(run_dir, f"gen_{gen_num}")
        if not os.path.isdir(gen_dir):
            break
        acc = extract_accuracy_from_gen(gen_dir)
        if acc is not None:
            history.append(acc)
    return history


# ── Internal Extractors ───────────────────────────────────────────────────


def _extract_from_eval_results(
    gen_dir: str,
    *,
    gen_num: int = 0,
) -> List[FailureRecord]:
    """Extract wrong_answer failures from evaluation_results.json."""
    eval_path = os.path.join(gen_dir, "evaluation_results.json")
    if not os.path.exists(eval_path):
        return []

    try:
        with open(eval_path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []

    failures: List[FailureRecord] = []
    details = data.get("details", [])

    for item in details:
        if not isinstance(item, dict):
            continue

        status = item.get("status", "")
        if status != "incorrect":
            continue

        qid = item.get("question_id", "unknown")
        domain = item.get("domain", "unknown")
        model_answer = item.get("model_answer", "")
        correct_answer = item.get("correct_answer", "")

        failures.append({
            "id": f"q_{qid}_gen{gen_num}",
            "task_family": domain.lower().replace(" ", "_") if domain else "unknown",
            "failure_type": "wrong_answer",
            "context_summary": (
                f"Question {qid}: answered {model_answer}, correct was {correct_answer}. "
                f"Domain: {domain}"
            ),
            "expected_behavior": f"Answer {correct_answer} for question {qid}",
            "actual_behavior": f"Answered {model_answer}",
            "severity": 0.7,
            "recurrence_count": 1,
        })

    return failures


def _extract_from_execution_log(
    gen_dir: str,
    *,
    gen_num: int = 0,
) -> List[FailureRecord]:
    """Extract structural failures from agent_execution.json."""
    exec_path = os.path.join(gen_dir, "agent_execution.json")
    if not os.path.exists(exec_path):
        return []

    try:
        with open(exec_path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError):
        # Parse error = structural failure
        return [{
            "id": f"exec_parse_gen{gen_num}",
            "task_family": "unknown",
            "failure_type": "missed_edge_case",
            "context_summary": f"Execution log was malformed in gen {gen_num}",
            "expected_behavior": "Valid JSON execution log",
            "actual_behavior": "JSON parse error",
            "severity": 0.5,
            "recurrence_count": 1,
        }]

    failures: List[FailureRecord] = []

    # Check for explicit error field
    if data.get("error"):
        failures.append({
            "id": f"exec_error_gen{gen_num}",
            "task_family": data.get("task_family", "unknown"),
            "failure_type": "missed_edge_case",
            "context_summary": f"Execution error in gen {gen_num}: {data['error']}",
            "expected_behavior": "Successful execution",
            "actual_behavior": f"Error: {data['error']}",
            "severity": 0.8,
            "recurrence_count": 1,
        })

    # Check for zero accuracy with many questions = systematic issue
    accuracy = data.get("accuracy", 0)
    if isinstance(accuracy, (int, float)) and accuracy == 0.0:
        task_type = data.get("detected_task_type", "unknown")
        if task_type in ("qa", "classification"):
            failures.append({
                "id": f"zero_acc_gen{gen_num}",
                "task_family": "unknown",
                "failure_type": "shortcut",
                "context_summary": f"Zero accuracy in gen {gen_num} for {task_type} task — possible systematic failure",
                "expected_behavior": "Non-zero accuracy on evaluated questions",
                "actual_behavior": "0% accuracy — answers missing or all wrong",
                "severity": 0.9,
                "recurrence_count": 1,
            })

    return failures
