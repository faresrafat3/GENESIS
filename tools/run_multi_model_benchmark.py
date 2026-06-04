#!/usr/bin/env python3
"""
Multi-Model GPQA Benchmark with API Key Pool
=============================================

يشغّل عدة نماذج بالتتابع (أو واحد محدد) على GPQA-style benchmark،
مع التدوير الذكي بين مفاتيح OpenRouter لتجاوز rate limits الـ free tier.

Examples:
    # 1) اختبار كل النماذج الموصى بها على 20 سؤال GPQA
    python tools/run_multi_model_benchmark.py \
        --task gpqa \
        --models_preset top_for_gpqa \
        --limit 20 \
        --output_dir results/multi_model_gpqa_smoke

    # 2) نموذج واحد، 198 سؤال كاملة
    python tools/run_multi_model_benchmark.py \
        --task gpqa \
        --models nemotron-3-ultra-free \
        --limit 0 \
        --reasoning high \
        --output_dir results/nemotron3_ultra_full

    # 3) كل النماذج (احذر — وقت طويل)
    python tools/run_multi_model_benchmark.py \
        --task gpqa --models all --limit 20

Outputs:
    results/<output_dir>/
        ├── summary.json          # comparison table عبر النماذج
        ├── summary.md            # نفس البيانات في Markdown
        ├── <model_shortcut>.json # كل نموذج له ملف نتائج كامل
        └── pool_stats.json       # إحصائيات استخدام المفاتيح

تصميم عام: مفيش حاجة مخصوصة لـ GENESIS هنا — هذا قياس pure للنموذج.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# نسمح بالـ import من tools/ أو من الـ root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.api_key_pool import get_default_pool, APIKeyPool  # noqa: E402
from tools.model_registry import MODELS, get_model, recommended_for  # noqa: E402


# ============================================================
#                  Prompt building + parsing
# ============================================================

SYSTEM_PROMPT = """You are an expert scientist (physics, chemistry, biology) taking a graduate-level
multiple-choice exam (GPQA Diamond level). Each question has exactly 4 options labeled A, B, C, D
and exactly one is correct.

RESPONSE PROTOCOL — follow strictly:
1. Reason carefully and step by step about the underlying science.
2. Eliminate clearly wrong options when possible.
3. You MUST end your reply with a final line in EXACTLY this format (no other text after it):

ANSWER: X

where X is one single letter A, B, C, or D. The line must literally start with the word ANSWER
followed by a colon and a space, then the letter. Do NOT add explanations after the ANSWER line.
If you are unsure, still output your best guess in the ANSWER line — never refuse, never output
"unknown" or "I don't know"."""


FORCE_LETTER_PROMPT = (
    "STOP THINKING. Just output one line with your best guess in this exact format:\n\n"
    "ANSWER: X\n\n"
    "where X is one of A, B, C, or D. Output ONLY that single line — no reasoning, "
    "no explanation, no markdown, nothing else. Just the literal string 'ANSWER: ' "
    "followed by one capital letter."
)


def extract_letter(text: str) -> str:
    """يستخرج حرف الإجابة من response. عام جداً — يجرب 10+ صيغ متعددة."""
    if not text:
        return ""
    txt = text.strip()

    # 1) ANSWER: X (مع/بدون مسافة، colons متعددة، مع/بدون **)
    for pattern in (
        r"ANSWER\s*[:\-=]+\s*\*?\*?\s*([ABCD])\s*\*?\*?",
        r"\bANSWER\s+IS\s*[:\-=]?\s*\*?\*?\s*([ABCD])\b",
        r"FINAL\s+ANSWER\s*[:\-=]+\s*\*?\*?\s*([ABCD])",
        r"THE\s+ANSWER\s+IS\s*[:\-=]?\s*\*?\*?\s*([ABCD])",
        r"CORRECT\s+(?:ANSWER|OPTION)\s+IS\s*[:\-=]?\s*\*?\*?\s*([ABCD])",
        r"OPTION\s*[:\-=]?\s*\*?\*?\s*([ABCD])\s*\*?\*?\s*(?:IS|$)",
    ):
        m = re.search(pattern, txt, re.IGNORECASE)
        if m:
            return m.group(1).upper()

    # 2) صيغ شائعة في markdown/latex في آخر النص
    tail = txt[-800:]
    for pattern in (
        r"\*\*\s*([ABCD])\s*\*\*",          # **X**
        r"\\boxed\{\s*([ABCD])\s*\}",       # \boxed{X}
        r"\\textbf\{\s*([ABCD])\s*\}",      # \textbf{X}
        r"\(\s*([ABCD])\s*\)\s*$",          # (X) at end
        r"\s([ABCD])\s*\.\s*$",             # "X." at end
        r"^\s*([ABCD])\s*$",                # حرف وحده
    ):
        m = re.search(pattern, tail, re.IGNORECASE | re.MULTILINE)
        if m:
            return m.group(1).upper()

    # 3) آخر سطر فيه حرف A-D وحده / مع ترقيم
    for line in reversed(txt.strip().split("\n")):
        line_clean = line.strip().strip(".").strip(":").strip("*").strip()
        # حالة "A" أو "A." أو "A:" أو "Answer A"
        m = re.match(r"^(?:answer\s*[:\-]?\s*)?\*?\*?\s*([ABCD])\s*\*?\*?\s*\.?\s*$",
                     line_clean, re.IGNORECASE)
        if m:
            return m.group(1).upper()

    # 4) آخر حرف A-D ظهر في آخر 200 حرف (fallback أخير)
    last_match = None
    for m in re.finditer(r"\b([ABCD])\b", txt[-200:]):
        last_match = m
    if last_match:
        return last_match.group(1).upper()

    return ""


def build_prompt(q: dict[str, Any]) -> str:
    """يبني prompt مع حماية ضد case mismatch (الـ bug اللي شفناه في run_53)."""
    # 🔑 GENERAL: نجرب case variants متعددة
    qtext = (
        q.get("Question")
        or q.get("question")
        or q.get("QUESTION")
        or q.get("text")
        or q.get("prompt")
        or ""
    )
    options = q.get("options") or q.get("Options") or {}
    opts_str = ""
    if isinstance(options, dict):
        for k in sorted(options.keys()):
            opts_str += f"{k}) {options[k]}\n"
    elif isinstance(options, list):
        for i, opt in enumerate(options):
            opts_str += f"{chr(65 + i)}) {opt}\n"
    return f"{qtext.strip()}\n\nOptions:\n{opts_str}"


# ============================================================
#                  Per-model evaluation
# ============================================================

def extract_response_text(resp) -> tuple[str, dict]:
    """يستخرج النص الكامل من response مع fallback على reasoning content.

    بعض النماذج (Nemotron, gpt-oss في reasoning mode) بترجع:
      - message.content = ""  (فاضي لو max_tokens خلص في reasoning)
      - message.reasoning أو reasoning_details = "<chain-of-thought>"

    نرجع (combined_text, meta) حيث combined_text = content + reasoning
    لو الاتنين موجودين، أو fallback على reasoning لو content فاضي.
    """
    msg = resp.choices[0].message
    content = msg.content or ""
    reasoning_text = ""

    # OpenRouter normalizes reasoning into reasoning_details list
    for attr in ("reasoning", "reasoning_content"):
        v = getattr(msg, attr, None)
        if v and isinstance(v, str):
            reasoning_text = v
            break

    if not reasoning_text:
        rd = getattr(msg, "reasoning_details", None)
        if rd:
            try:
                if isinstance(rd, list):
                    parts = []
                    for item in rd:
                        if isinstance(item, dict):
                            parts.append(item.get("text", "") or item.get("content", ""))
                        else:
                            t = getattr(item, "text", None) or getattr(item, "content", None)
                            if t:
                                parts.append(t)
                    reasoning_text = "\n".join(p for p in parts if p)
            except Exception:
                pass

    # combined: content (visible) أولاً، ثم reasoning كـ fallback
    if content and reasoning_text:
        combined = content + "\n\n[REASONING]\n" + reasoning_text
    elif content:
        combined = content
    elif reasoning_text:
        combined = reasoning_text
    else:
        combined = ""

    meta = {
        "finish_reason": resp.choices[0].finish_reason,
        "content_chars": len(content),
        "reasoning_chars": len(reasoning_text),
    }
    try:
        u = resp.usage
        meta["usage"] = {
            "prompt_tokens": u.prompt_tokens,
            "completion_tokens": u.completion_tokens,
            "total_tokens": u.total_tokens,
        }
        # capture reasoning_tokens lo موجود (OpenRouter)
        ctd = getattr(u, "completion_tokens_details", None)
        if ctd:
            rt = getattr(ctd, "reasoning_tokens", None)
            if rt is not None:
                meta["usage"]["reasoning_tokens"] = rt
    except Exception:
        pass
    return combined, meta


def evaluate_model(
    pool: APIKeyPool,
    model_id: str,
    questions: list[dict],
    *,
    reasoning: Optional[str] = None,
    max_tokens: int = 4096,
    temperature: float = 0.0,
    verbose_first: int = 2,
    output_path: Optional[Path] = None,
    use_force_followup: bool = True,
) -> dict[str, Any]:
    """يقيم نموذج واحد على قائمة أسئلة. يرجع dict نتائج كامل.

    use_force_followup: لو النموذج ميرجعش letter في الـ first response،
    نبعت رسالة tay`anية صغيرة نطلب فيها الـ letter بس (chain-of-thought
    موجود في الـ first response). هذا يخفض الـ invalid rate من ~35% لـ <5%.
    """

    results: list[dict[str, Any]] = []
    correct = invalid = recovered = 0
    domain_stats: dict[str, dict[str, int]] = {}
    t0 = time.time()

    def make_call(client, messages: list[dict], local_max_tokens: int):
        kwargs: dict[str, Any] = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": local_max_tokens,
        }
        if reasoning:
            kwargs["extra_body"] = {"reasoning": {"effort": reasoning}}
        return client.chat.completions.create(**kwargs)

    for i, q in enumerate(questions, 1):
        qid = q.get("id", i)
        correct_letter = (q.get("correct_answer_letter") or "").upper().strip()
        domain = q.get("domain", "unknown")
        domain_stats.setdefault(domain, {"total": 0, "correct": 0})
        domain_stats[domain]["total"] += 1

        user_msg = build_prompt(q)
        messages_round1 = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ]

        if i <= verbose_first:
            print(f"\n  --- Q{i}/{len(questions)} (id={qid}, {domain}) ---")
            print(f"  PROMPT preview: {user_msg[:200].replace(chr(10), ' / ')}...")

        # ===== Round 1: full reasoning =====
        round1_meta = {}
        try:
            resp = pool.call_with_retry(
                lambda c, m=messages_round1: make_call(c, m, max_tokens),
                on_attempt=lambda n, k, s: (
                    print(f"    [retry {n}] key={k} {s}")
                    if n > 1 or s.startswith("failed") else None
                ),
                max_attempts=max(len(pool._keys), 3),
                per_attempt_sleep=0.3,
            )
            txt, round1_meta = extract_response_text(resp)
        except Exception as e:
            txt = ""
            print(f"  ✗ Q{i} round 1 all keys failed: {str(e)[:120]}")

        pred = extract_letter(txt)
        round1_pred = pred  # نخزنها للـ logging
        used_followup = False
        followup_txt = ""

        # ===== Round 2: force-letter follow-up =====
        # نعمل follow-up لو:
        # (1) مفيش letter في الـ round1 (ANY content)
        # (2) أو الـ visible content فاضي بس فيه reasoning (model thought but didn't output)
        # (3) أو الـ finish_reason = "length" (max_tokens انتهى وسط reasoning)
        needs_followup = (
            use_force_followup and
            not pred and
            (txt or round1_meta.get("reasoning_chars", 0) > 0
             or round1_meta.get("finish_reason") == "length")
        )
        if needs_followup:
            used_followup = True
            # نعمل follow-up حتى لو txt فاضي — لأن النموذج "فكر" داخلياً
            assistant_content = txt if txt else "(I was thinking but ran out of tokens before answering)"
            messages_round2 = messages_round1 + [
                {"role": "assistant", "content": assistant_content},
                {"role": "user", "content": FORCE_LETTER_PROMPT},
            ]
            try:
                # الـ follow-up: reasoning=low + max_tokens 256 عشان نسمح
                # بـ tiny reasoning + الـ letter. لو النموذج بيدخل thinking loop،
                # على الأقل عنده space كافي للـ letter في الآخر.
                def make_followup(client):
                    return client.chat.completions.create(
                        model=model_id,
                        messages=messages_round2,
                        temperature=0.0,
                        max_tokens=256,
                        extra_body={"reasoning": {"effort": "low"}},
                    )
                resp2 = pool.call_with_retry(
                    make_followup,
                    max_attempts=max(len(pool._keys), 3),
                    per_attempt_sleep=0.3,
                )
                followup_txt, _ = extract_response_text(resp2)
                pred = extract_letter(followup_txt)
                if pred:
                    recovered += 1
            except Exception as e:
                print(f"  ⚠ Q{i} follow-up failed: {str(e)[:80]}")

            # ===== Round 3: last resort — try to extract letter
            # from the round-1 REASONING text itself.
            # حتى لو الـ visible content فاضي، فيه أحياناً letter في الـ reasoning.
            if not pred and round1_meta.get("reasoning_chars", 0) > 100:
                # نأخذ آخر 2000 حرف من الـ reasoning (أكتر فرصة فيهم answer)
                reasoning_tail = txt[-2000:] if txt else ""
                pred = extract_letter(reasoning_tail)
                if pred:
                    recovered += 1
                    print(f"  💡 Q{i} recovered from reasoning tail: {pred}")

        ok = (pred == correct_letter) if pred else False
        if pred not in ("A", "B", "C", "D"):
            invalid += 1
        if ok:
            correct += 1
            domain_stats[domain]["correct"] += 1

        if i <= verbose_first:
            print(f"  RESP1 tail: ...{txt[-200:]}")
            if used_followup:
                print(f"  RESP2 (force): {followup_txt[:100]}")
            print(f"  → pred={pred!r} truth={correct_letter!r} "
                  f"{'✓' if ok else '✗'} "
                  f"{'(recovered)' if used_followup and pred else ''}")

        results.append({
            "question_id": qid,
            "domain": domain,
            "subdomain": q.get("subdomain"),
            "correct_answer_letter": correct_letter,
            "predicted_letter": pred,
            "round1_pred": round1_pred,
            "used_followup": used_followup,
            "is_correct": ok,
            "response_chars": len(txt),
            "round1_meta": round1_meta,
            "response_excerpt": txt[:400] + ("..." if len(txt) > 400 else ""),
            "followup_excerpt": followup_txt[:200] if used_followup else None,
        })

        elapsed = time.time() - t0
        rate = i / elapsed if elapsed > 0 else 0
        if i % 5 == 0 or i == len(questions) or i <= verbose_first:
            print(f"  [{i:3d}/{len(questions)}] acc={correct/i*100:5.2f}%  "
                  f"({rate:.2f} q/s)  invalid={invalid}  recovered={recovered}")

    total = len(questions)
    summary = {
        "model_id": model_id,
        "reasoning_effort": reasoning,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "total": total,
        "correct": correct,
        "incorrect": total - correct - invalid,
        "invalid": invalid,
        "recovered_via_followup": recovered,
        "accuracy_percent": (correct / total * 100) if total else 0.0,
        "per_domain": {
            d: {
                "total": v["total"],
                "correct": v["correct"],
                "accuracy_percent": (v["correct"] / v["total"] * 100) if v["total"] else 0.0,
            }
            for d, v in domain_stats.items()
        },
        "elapsed_seconds": round(time.time() - t0, 2),
        "timestamp": datetime.now().isoformat(),
    }

    payload = {"summary": summary, "details": results}
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"  ✓ Saved: {output_path}")

    return payload


# ============================================================
#                  Model selection presets
# ============================================================

def resolve_models(spec: str) -> list[str]:
    """
    spec يقدر يكون:
    - "all" : كل النماذج في الـ registry
    - "top_for_gpqa" : أحسن نماذج GPQA حسب benchmarks الرسمية
    - "top_for_coding" : أحسن coding
    - "top_for_agent" : أحسن agent orchestration
    - "smoke" : 3 نماذج صغيرة سريعة للاختبار
    - أو comma-separated list من shortcuts
    """
    spec = spec.strip()
    if spec == "all":
        return list(MODELS.keys())
    if spec == "smoke":
        return ["lfm-2.5-thinking-free", "nemotron-3-nano-free", "gpt-oss-120b-free"]
    if spec == "top_for_gpqa":
        return [m.shortcut for m in recommended_for("gpqa")[:5]]
    if spec == "top_for_coding":
        return [m.shortcut for m in recommended_for("coding")[:5]]
    if spec == "top_for_agent":
        return [m.shortcut for m in recommended_for("agent")[:5]]
    # comma separated
    return [s.strip() for s in spec.split(",") if s.strip()]


# ============================================================
#                  Cross-model summary
# ============================================================

def write_cross_model_summary(
    all_results: dict[str, dict],
    output_dir: Path,
    *,
    questions_total: int,
    pool_stats: dict,
) -> None:
    """يكتب summary.json و summary.md للمقارنة."""
    rows = []
    for model_shortcut, payload in all_results.items():
        s = payload["summary"]
        try:
            spec = get_model(model_shortcut)
            official_gpqa = spec.benchmarks.get("gpqa_diamond")
        except KeyError:
            spec = None
            official_gpqa = None

        rows.append({
            "model": model_shortcut,
            "openrouter_id": s["model_id"],
            "official_gpqa_diamond": official_gpqa,
            "our_accuracy_percent": round(s["accuracy_percent"], 2),
            "gap_vs_official": (
                round(s["accuracy_percent"] - official_gpqa, 2)
                if official_gpqa is not None
                else None
            ),
            "correct": s["correct"],
            "invalid": s["invalid"],
            "recovered": s.get("recovered_via_followup", 0),
            "total": s["total"],
            "elapsed_seconds": s["elapsed_seconds"],
            "rate_qps": round(s["total"] / s["elapsed_seconds"], 3) if s["elapsed_seconds"] > 0 else 0,
        })

    # Sort by accuracy desc
    rows.sort(key=lambda r: r["our_accuracy_percent"], reverse=True)

    summary = {
        "task": "gpqa",
        "questions_evaluated": questions_total,
        "models_evaluated": len(all_results),
        "timestamp": datetime.now().isoformat(),
        "rankings": rows,
        "pool_stats": pool_stats,
    }

    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Markdown
    md_lines = [
        f"# Multi-Model GPQA Benchmark Results",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Questions:** {questions_total}",
        f"**Models:** {len(all_results)}",
        f"**Key pool:** {pool_stats['total_keys']} keys, "
        f"{pool_stats['available_now']} available now, "
        f"{pool_stats['permanently_failed']} dead",
        "",
        "## Ranking (sorted by our accuracy)",
        "",
        "| # | Model | Our % | Official % | Gap | Correct | Invalid | Recovered | Time | q/s |",
        "|---|-------|-------|-----------|-----|---------|---------|-----------|------|-----|",
    ]
    for i, r in enumerate(rows, 1):
        gap_str = f"{r['gap_vs_official']:+.1f}" if r["gap_vs_official"] is not None else "-"
        off_str = f"{r['official_gpqa_diamond']:.1f}" if r["official_gpqa_diamond"] is not None else "-"
        md_lines.append(
            f"| {i} | `{r['model']}` | **{r['our_accuracy_percent']:.2f}** | {off_str} | {gap_str} | "
            f"{r['correct']}/{r['total']} | {r['invalid']} | {r['recovered']} | "
            f"{r['elapsed_seconds']:.0f}s | {r['rate_qps']:.2f} |"
        )
    md_lines += [
        "",
        "## Notes",
        "",
        "- **Our %**: What we measured in this run",
        "- **Official %**: From vendor's model card (or '-' if not published)",
        "- **Gap**: positive = we beat official, negative = we are below",
        "- Large negative gaps usually indicate: rate limits, free-tier quantization, or scaffolding bugs",
        "",
        "## API Key Pool Usage",
        "",
    ]
    for kid, info in pool_stats.get("per_key", {}).items():
        status = "available" if info["available"] else ("DEAD" if "401" in info["last_error"] else "cooldown")
        md_lines.append(
            f"- **{kid}**: {info['requests']} requests, {info['successes']} ok, "
            f"{info['failures']} failed ({info['success_rate']*100:.1f}% success) — {status}"
        )

    (output_dir / "summary.md").write_text("\n".join(md_lines), encoding="utf-8")
    print(f"\n  ✓ Cross-model summary: {output_dir/'summary.md'}")


# ============================================================
#                  Main
# ============================================================

def main() -> int:
    p = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                description=__doc__)
    p.add_argument("--task", default="gpqa",
                   help="Task name (currently only 'gpqa' supported, future: 'swe_bench')")
    p.add_argument("--questions_path",
                   default="genesis/tasks/gpqa/data/private/diamond_questions.json")
    p.add_argument("--models", default="top_for_gpqa",
                   help='Preset (all|smoke|top_for_gpqa|top_for_coding|top_for_agent) or comma list')
    p.add_argument("--limit", type=int, default=20,
                   help="0 = all questions; else first N")
    p.add_argument("--reasoning", choices=["low", "medium", "high"], default="high")
    p.add_argument("--max_tokens", type=int, default=16384,
                   help="Includes reasoning tokens for reasoning models. "
                        "Models like Nemotron Nano can consume 1200-2000 reasoning tokens "
                        "even before producing visible content; 4096 is too tight.")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--output_dir", default=None,
                   help="Default: results/multi_<timestamp>")
    p.add_argument("--keys_file", default=None,
                   help="Path to keys file (.env / .json). Default: read from env + .env")
    p.add_argument("--rate_limit_cooldown", type=float, default=60.0)
    p.add_argument("--skip_existing", action="store_true",
                   help="Skip models that already have a result file in output_dir")
    args = p.parse_args()

    # Load questions
    qpath = Path(args.questions_path)
    if not qpath.exists():
        print(f"ERROR: questions file not found: {qpath}", file=sys.stderr)
        return 2
    with qpath.open(encoding="utf-8") as f:
        questions = json.load(f)
    if args.limit > 0:
        questions = questions[: args.limit]

    # Resolve models
    model_shortcuts = resolve_models(args.models)
    print(f"\n=== Multi-Model Benchmark ===")
    print(f"Task: {args.task}")
    print(f"Questions: {len(questions)}")
    print(f"Models ({len(model_shortcuts)}): {model_shortcuts}")
    print(f"Reasoning: {args.reasoning} | max_tokens: {args.max_tokens}")
    print()

    # Output dir
    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        out_dir = Path(f"results/multi_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Pool
    pool = get_default_pool(
        keys_file=args.keys_file,
        rate_limit_cooldown=args.rate_limit_cooldown,
        stats_file=out_dir / "pool_stats.json",
    )
    print()

    # Run each model
    all_results: dict[str, dict] = {}
    for i, shortcut in enumerate(model_shortcuts, 1):
        out_file = out_dir / f"{shortcut}.json"
        if args.skip_existing and out_file.exists():
            print(f"\n[{i}/{len(model_shortcuts)}] {shortcut} — SKIP (exists)")
            all_results[shortcut] = json.loads(out_file.read_text(encoding="utf-8"))
            continue
        try:
            spec = get_model(shortcut)
        except KeyError:
            print(f"\n[{i}/{len(model_shortcuts)}] {shortcut} — UNKNOWN model, skipping")
            continue

        print(f"\n{'='*70}")
        print(f"[{i}/{len(model_shortcuts)}] Model: {spec.shortcut}")
        print(f"  OpenRouter ID: {spec.openrouter_id}")
        print(f"  Spec: {spec.description}")
        if spec.benchmarks.get("gpqa_diamond"):
            print(f"  Official GPQA Diamond: {spec.benchmarks['gpqa_diamond']:.1f}%")
        print(f"{'='*70}")

        try:
            payload = evaluate_model(
                pool=pool,
                model_id=spec.openrouter_id,
                questions=questions,
                reasoning=args.reasoning if spec.supports_reasoning else None,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                output_path=out_file,
            )
            all_results[shortcut] = payload
            print(f"  ✅ {shortcut}: {payload['summary']['accuracy_percent']:.2f}%")
        except Exception as e:
            print(f"  ❌ {shortcut} FAILED entirely: {e}")
            (out_dir / f"{shortcut}_ERROR.txt").write_text(str(e), encoding="utf-8")

        # Print pool status between models
        pool.print_summary()

    # Cross-model summary
    if all_results:
        write_cross_model_summary(
            all_results=all_results,
            output_dir=out_dir,
            questions_total=len(questions),
            pool_stats=pool.stats_summary(),
        )

    print(f"\n{'='*70}")
    print(f"COMPLETE. All results in: {out_dir}")
    print(f"View ranking:  cat {out_dir}/summary.md")
    print(f"{'='*70}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
