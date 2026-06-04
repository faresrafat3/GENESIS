#!/usr/bin/env python3
"""
GPQA Pure Baseline — Direct LLM, No GENESIS, No Pipeline
=========================================================
Purpose:
    اختبار الحد الأقصى الحقيقي للنموذج لوحده على GPQA Diamond،
    بدون أي بنية GENESIS أو pipeline أو evolution.
    هذا هو "السقف" الذي يجب أن نقترب منه أو نتجاوزه عند استخدام البنية.

Usage:
    export OPENROUTER_API_KEY=sk-or-...
    python tools/gpqa_pure_baseline.py \
        --model openai/gpt-oss-120b:free \
        --questions_path genesis/tasks/gpqa/data/private/diamond_questions.json \
        --output_path results/gpqa_pure_baseline_<model_tag>.json \
        --limit 0           # 0 = كل الـ 198
        --reasoning high    # high | medium | low (لو النموذج يدعم)
        --max_tokens 4096   # عشان نسمح بـ chain-of-thought كامل

تصميم عام (general): لا يحتوي على أي تخصيص لـ gpqa بخلاف اسم الـ JSON.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import openai  # type: ignore
except ImportError:
    print("ERROR: openai package not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)


SYSTEM_PROMPT = """You are an expert scientist taking a graduate-level multiple-choice exam (GPQA Diamond).
For each question:
1. Think carefully and step by step about the underlying physics/chemistry/biology.
2. Eliminate clearly wrong options.
3. At the very end, output a single line in EXACTLY this format:
ANSWER: <LETTER>
where <LETTER> is one of A, B, C, or D. Nothing after that line."""


def extract_letter(text: str) -> str:
    """يستخرج الحرف من رد النموذج. يفضّل سطر 'ANSWER: X'، ثم آخر حرف A-D."""
    if not text:
        return ""
    # 1) ابحث عن ANSWER: X
    m = re.search(r"ANSWER\s*:\s*([ABCD])", text, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    # 2) ابحث عن **X** أو (X) في آخر 200 حرف
    tail = text[-300:]
    m = re.search(r"\*\*\s*([ABCD])\s*\*\*", tail)
    if m:
        return m.group(1).upper()
    m = re.search(r"\b\(?([ABCD])\)?\b", tail[::-1])  # آخر حرف
    if m:
        return m.group(1).upper()
    return ""


def build_prompt(q: dict[str, Any]) -> str:
    """يبني الـ prompt من سؤال GPQA. عام: يجرب 'Question' ثم 'question'."""
    qtext = q.get("Question") or q.get("question") or q.get("text") or ""
    options = q.get("options") or {}
    opts_str = ""
    if isinstance(options, dict):
        for k in sorted(options.keys()):
            opts_str += f"{k}) {options[k]}\n"
    elif isinstance(options, list):
        for i, opt in enumerate(options):
            opts_str += f"{chr(65+i)}) {opt}\n"
    return f"{qtext.strip()}\n\nOptions:\n{opts_str}"


def call_model(
    client: "openai.OpenAI",
    model: str,
    user_msg: str,
    *,
    max_tokens: int = 4096,
    temperature: float = 0.0,
    reasoning_effort: str | None = None,
    retries: int = 3,
) -> tuple[str, dict[str, Any]]:
    """يستدعي النموذج مع retry. يرجع (full_text, meta)."""
    last_err = None
    for attempt in range(retries):
        try:
            kwargs = {
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            # OpenRouter يمرر reasoning effort عبر extra_body
            if reasoning_effort:
                kwargs["extra_body"] = {"reasoning": {"effort": reasoning_effort}}
            resp = client.chat.completions.create(**kwargs)
            txt = resp.choices[0].message.content or ""
            meta = {
                "finish_reason": resp.choices[0].finish_reason,
                "model_used": resp.model,
            }
            try:
                meta["usage"] = {
                    "prompt_tokens": resp.usage.prompt_tokens,
                    "completion_tokens": resp.usage.completion_tokens,
                }
            except Exception:
                pass
            return txt, meta
        except Exception as e:
            last_err = e
            print(f"  [retry {attempt+1}/{retries}] {type(e).__name__}: {e}", file=sys.stderr)
            time.sleep(2 ** attempt)
    return "", {"error": str(last_err)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Model id (e.g. openai/gpt-oss-120b:free)")
    parser.add_argument("--questions_path", required=True, help="Path to GPQA-style JSON list")
    parser.add_argument("--output_path", required=True, help="Where to save full results JSON")
    parser.add_argument("--limit", type=int, default=0, help="0 = all; else first N")
    parser.add_argument("--reasoning", choices=["low", "medium", "high"], default=None)
    parser.add_argument("--max_tokens", type=int, default=4096)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--base_url", default=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"))
    parser.add_argument("--api_key_env", default="OPENROUTER_API_KEY",
                        help="Env var name for API key (also tries OPENAI_API_KEY)")
    parser.add_argument("--verbose_first", type=int, default=2,
                        help="Print full prompt+response for the first N questions")
    args = parser.parse_args()

    api_key = os.getenv(args.api_key_env) or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(f"ERROR: No API key found in ${args.api_key_env} or $OPENAI_API_KEY", file=sys.stderr)
        return 2

    questions_path = Path(args.questions_path)
    if not questions_path.exists():
        print(f"ERROR: questions file not found: {questions_path}", file=sys.stderr)
        return 2
    with questions_path.open(encoding="utf-8") as f:
        questions = json.load(f)
    if args.limit > 0:
        questions = questions[: args.limit]

    print(f"=== GPQA Pure Baseline ===")
    print(f"Model:       {args.model}")
    print(f"Base URL:    {args.base_url}")
    print(f"Reasoning:   {args.reasoning or '(default)'}")
    print(f"Max tokens:  {args.max_tokens}")
    print(f"Questions:   {len(questions)}")
    print(f"Output:      {args.output_path}")
    print("=" * 60)

    client = openai.OpenAI(api_key=api_key, base_url=args.base_url)

    results: list[dict[str, Any]] = []
    correct = invalid = 0
    domain_stats: dict[str, dict[str, int]] = {}

    t0 = time.time()
    for i, q in enumerate(questions, 1):
        qid = q.get("id", i)
        correct_letter = (q.get("correct_answer_letter") or "").upper().strip()
        domain = q.get("domain", "unknown")
        domain_stats.setdefault(domain, {"total": 0, "correct": 0})
        domain_stats[domain]["total"] += 1

        user_msg = build_prompt(q)

        if i <= args.verbose_first:
            print(f"\n--- Question {i}/{len(questions)} (id={qid}, domain={domain}) ---")
            print("PROMPT:")
            print(user_msg[:600] + ("..." if len(user_msg) > 600 else ""))

        txt, meta = call_model(
            client, args.model, user_msg,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            reasoning_effort=args.reasoning,
        )
        pred = extract_letter(txt)
        ok = (pred == correct_letter) if pred else False
        if pred not in ("A", "B", "C", "D"):
            invalid += 1
        if ok:
            correct += 1
            domain_stats[domain]["correct"] += 1

        if i <= args.verbose_first:
            print(f"RESPONSE (last 400 chars):\n...{txt[-400:]}")
            print(f"PARSED: {pred!r}   CORRECT: {correct_letter!r}   OK: {ok}")

        results.append({
            "question_id": qid,
            "domain": domain,
            "subdomain": q.get("subdomain"),
            "correct_answer_letter": correct_letter,
            "predicted_letter": pred,
            "is_correct": ok,
            "response_excerpt": (txt[:500] + "...") if len(txt) > 500 else txt,
            "meta": meta,
        })
        elapsed = time.time() - t0
        rate = i / elapsed if elapsed > 0 else 0
        print(f"[{i:3d}/{len(questions)}] id={qid} domain={domain[:12]:12s} "
              f"pred={pred or '?':>1s} truth={correct_letter} "
              f"{'✓' if ok else '✗'} | acc so far: {correct/i*100:5.2f}% "
              f"| {rate:.2f} q/s")

    total = len(questions)
    acc = correct / total if total else 0.0
    summary = {
        "model": args.model,
        "base_url": args.base_url,
        "reasoning_effort": args.reasoning,
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "total_questions": total,
        "correct": correct,
        "incorrect": total - correct - invalid,
        "invalid": invalid,
        "accuracy": acc,
        "accuracy_percent": acc * 100,
        "per_domain": {
            d: {
                "total": v["total"],
                "correct": v["correct"],
                "accuracy_percent": (v["correct"] / v["total"] * 100) if v["total"] else 0.0,
            }
            for d, v in domain_stats.items()
        },
        "elapsed_seconds": time.time() - t0,
        "timestamp": datetime.now().isoformat(),
    }

    out_path = Path(args.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump({"summary": summary, "details": results}, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("PURE BASELINE COMPLETE")
    print("=" * 60)
    print(f"Total:    {total}")
    print(f"Correct:  {correct}")
    print(f"Invalid:  {invalid}")
    print(f"Accuracy: {acc*100:.2f}%")
    print("Per-domain:")
    for d, v in summary["per_domain"].items():
        print(f"  {d:20s} {v['correct']:3d}/{v['total']:3d} ({v['accuracy_percent']:5.2f}%)")
    print(f"Saved to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
