#!/usr/bin/env python3
"""
Diagnose run_53 — لماذا حصلنا 30% فقط على GPQA بدلاً من 67-80% الرسمية؟
========================================================================

يفحص:
1. هل الـ target_agent.py بيقرأ السؤال صح من الـ JSON؟
2. هل بيبعت الـ prompt صح للنموذج؟
3. هل بيستخدم chain-of-thought كافي؟
4. هل بيستفيد فعلاً من GENESIS pipeline في الإجابة؟

تصميم عام: يمكن إعادة استخدامه لأي run_XX على gpqa.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path


def check_question_field_bug(agent_src: str, questions_sample: dict) -> dict:
    """يفحص هل الـ agent بيستخدم الـ key الصحيح للسؤال."""
    used_keys = re.findall(r"q\.get\(['\"](\w+)['\"]\)", agent_src)
    actual_keys = list(questions_sample.keys())
    qtext_extraction = re.search(r"qtext\s*=\s*(.+?)$", agent_src, re.MULTILINE)
    extraction_line = qtext_extraction.group(0) if qtext_extraction else "(not found)"

    # الـ key الفعلي اللي فيه السؤال
    actual_q_key = next((k for k in actual_keys if "question" in k.lower()), None)
    # هل الـ agent بيدوّر عليه بنفس الحالة؟
    used_question_keys = [k for k in used_keys if "question" in k.lower()]
    case_mismatch = actual_q_key not in used_question_keys if used_question_keys else False

    return {
        "bug": "question_field_case_mismatch",
        "severity": "CRITICAL" if case_mismatch else "OK",
        "actual_keys_in_json": actual_keys,
        "actual_question_key": actual_q_key,
        "keys_agent_tries": used_question_keys,
        "extraction_line": extraction_line.strip(),
        "impact": ("Empty question string sent to LLM → model guesses randomly from options"
                   if case_mismatch else "OK"),
    }


def check_chain_of_thought(agent_src: str) -> dict:
    """يفحص هل الـ prompt يسمح بـ chain-of-thought."""
    max_tokens_match = re.search(r"max_tokens\s*=\s*(\d+)", agent_src)
    max_tokens = int(max_tokens_match.group(1)) if max_tokens_match else None
    has_only_letter = "ONLY the letter" in agent_src or "only the letter" in agent_src.lower()
    has_step_by_step = "step by step" in agent_src.lower()

    severity = "OK"
    issues = []
    if max_tokens and max_tokens < 1000:
        severity = "HIGH"
        issues.append(f"max_tokens={max_tokens} is too low for graduate-level reasoning")
    if has_only_letter and not has_step_by_step:
        severity = "MEDIUM" if severity == "OK" else severity
        issues.append("Prompts model to 'output ONLY the letter' without explicit reasoning")
    if has_only_letter:
        issues.append("'ONLY the letter' instruction can suppress CoT even with step-by-step")

    return {
        "bug": "no_chain_of_thought",
        "severity": severity,
        "max_tokens": max_tokens,
        "has_step_by_step_instruction": has_step_by_step,
        "has_only_letter_constraint": has_only_letter,
        "issues": issues,
        "impact": ("Model cannot reason through hard graduate-level questions"
                   if severity != "OK" else "OK"),
    }


def check_pipeline_usage(agent_src: str) -> dict:
    """هل الـ GENESIS pipeline بيتم استخدامه فعلاً للإجابة؟"""
    runs_pipeline = "run_minimal_pipeline" in agent_src
    # هل ناتج الـ pipeline (tier_decision, theory_prediction, blackboard) بيتحقن في الـ prompt؟
    pipeline_in_prompt = bool(re.search(
        r"prompt\s*=.*(?:tier|blackboard|theory_pred|verification|concept)",
        agent_src, re.IGNORECASE | re.DOTALL
    ))
    # الـ pipeline بيتنادى مرة واحدة بس لكل المهمة؟ أم مرة لكل سؤال؟
    pipeline_call_count = len(re.findall(r"run_minimal_pipeline\s*\(", agent_src))
    pipeline_inside_loop = False
    # heuristic: لو فيه `for ... in questions` وبعدها `run_minimal_pipeline` قبل end of file
    loop_match = re.search(r"for\s+\w+,?\s*\w*\s+in\s+enumerate\(questions\)", agent_src)
    if loop_match:
        after_loop = agent_src[loop_match.end():]
        if "run_minimal_pipeline" in after_loop:
            pipeline_inside_loop = True

    severity = "OK"
    if runs_pipeline and not pipeline_in_prompt:
        severity = "HIGH"

    return {
        "bug": "pipeline_not_used_in_answer",
        "severity": severity,
        "runs_pipeline": runs_pipeline,
        "pipeline_called_n_times": pipeline_call_count,
        "pipeline_in_question_loop": pipeline_inside_loop,
        "pipeline_output_injected_in_prompt": pipeline_in_prompt,
        "impact": ("GENESIS pipeline runs once for whole task, its output is printed "
                   "but NOT passed to the LLM that answers each question. So the "
                   "pipeline cannot influence answers — only adds overhead."
                   if severity == "HIGH" else "OK"),
    }


def check_invalid_fallback(agent_src: str) -> dict:
    """لو النموذج رد بحاجة غير A/B/C/D، إيه اللي بيحصل؟"""
    fallback_match = re.search(
        r"if\s+answer\s+not\s+in\s+\[?['\"]A['\"].*?:\s*\n(.+?)(?=\n[A-Za-z]|$)",
        agent_src, re.DOTALL
    )
    fallback_block = fallback_match.group(1).strip() if fallback_match else "(none)"
    defaults_to_A = '"A"' in fallback_block and 'else' in fallback_block
    return {
        "bug": "invalid_answer_defaults_to_A",
        "severity": "MEDIUM" if defaults_to_A else "LOW",
        "fallback_block": fallback_block[:300],
        "impact": ("All invalid/empty responses become 'A' → biases ~25% baseline upward only if A happens to be correct often"
                   if defaults_to_A else "OK"),
    }


def analyze_predictions(eval_results_path: Path) -> dict:
    """يحلل توزيع التنبؤات vs الإجابات الصحيحة."""
    if not eval_results_path.exists():
        return {"error": f"Not found: {eval_results_path}"}
    with eval_results_path.open() as f:
        data = json.load(f)
    details = data.get("details", [])
    if not details:
        return {"error": "No details in evaluation_results.json"}

    pred_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "other": 0}
    truth_dist = {"A": 0, "B": 0, "C": 0, "D": 0}
    correct_by_letter = {"A": 0, "B": 0, "C": 0, "D": 0}
    for d in details:
        p = d.get("model_answer", "")
        t = d.get("correct_answer", "")
        if p in pred_dist:
            pred_dist[p] += 1
        else:
            pred_dist["other"] += 1
        if t in truth_dist:
            truth_dist[t] += 1
        if d.get("is_correct") and t in correct_by_letter:
            correct_by_letter[t] += 1

    # هل التوزيع مشابه للعشوائي؟
    total = len(details)
    expected_random = total / 4
    chi_like = sum(((pred_dist[k] - expected_random) ** 2) / expected_random for k in "ABCD")
    looks_random = chi_like < 20  # threshold تقريبي

    return {
        "total": total,
        "accuracy_percent": data.get("accuracy_percent"),
        "prediction_distribution": pred_dist,
        "truth_distribution": truth_dist,
        "correct_by_truth_letter": correct_by_letter,
        "chi_like_vs_uniform": round(chi_like, 2),
        "predictions_look_uniform_random": looks_random,
        "interpretation": (
            "Predictions are nearly uniform (~25% each letter) → model is guessing"
            if looks_random else
            "Predictions are skewed → model has some signal"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_dir", required=True,
                        help="e.g. runs/run_53/gen_1")
    parser.add_argument("--questions_path",
                        default="genesis/tasks/gpqa/data/private/diamond_questions.json")
    parser.add_argument("--output_path", default=None,
                        help="Where to save full diagnosis JSON (default: <run_dir>/diagnosis.json)")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(f"ERROR: {run_dir} not found", file=sys.stderr)
        return 2

    agent_path = run_dir / "target_agent.py"
    eval_path = run_dir / "evaluation_results.json"
    questions_path = Path(args.questions_path)

    if not agent_path.exists():
        print(f"ERROR: {agent_path} not found", file=sys.stderr)
        return 2

    agent_src = agent_path.read_text(encoding="utf-8")
    with questions_path.open(encoding="utf-8") as f:
        questions = json.load(f)
    q_sample = questions[0]

    print("=" * 70)
    print(f"DIAGNOSIS: {run_dir}")
    print("=" * 70)

    findings = []
    for check_fn in (
        check_question_field_bug,
        check_chain_of_thought,
        check_pipeline_usage,
        check_invalid_fallback,
    ):
        if check_fn is check_question_field_bug:
            result = check_fn(agent_src, q_sample)
        else:
            result = check_fn(agent_src)
        findings.append(result)
        print(f"\n[{result['severity']}] {result['bug']}")
        for k, v in result.items():
            if k in ("bug", "severity"):
                continue
            print(f"  {k}: {v}")

    print("\n" + "-" * 70)
    print("PREDICTION ANALYSIS (from evaluation_results.json):")
    print("-" * 70)
    pred_analysis = analyze_predictions(eval_path)
    for k, v in pred_analysis.items():
        print(f"  {k}: {v}")

    # خلاصة
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    critical = [f for f in findings if f["severity"] == "CRITICAL"]
    high = [f for f in findings if f["severity"] == "HIGH"]
    if critical:
        print(f"⚠️  {len(critical)} CRITICAL bug(s) found — these likely explain the gap.")
        for f in critical:
            print(f"    - {f['bug']}: {f['impact']}")
    if high:
        print(f"⚠️  {len(high)} HIGH-severity issue(s):")
        for f in high:
            print(f"    - {f['bug']}: {f['impact']}")
    if not (critical or high):
        print("✓ No critical/high issues detected in agent code.")

    # save
    out_path = Path(args.output_path) if args.output_path else (run_dir / "diagnosis.json")
    full = {
        "run_dir": str(run_dir),
        "findings": findings,
        "prediction_analysis": pred_analysis,
    }
    out_path.write_text(json.dumps(full, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nFull diagnosis saved to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
