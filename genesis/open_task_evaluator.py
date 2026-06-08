"""
GENESIS Open Task Evaluator — Layer 2
======================================
Runs when no evaluate.py exists (open-ended tasks like micro_task).
Produces unified score for Regime Detector.

Stolen from:
  - Rulers (arXiv:2601.08654) — schema-constrained judge, evidence quotes anchoring
  - InfoDeepSeek (arXiv:2505.15872) — IA@5: evidence score independent of output score
  - G-Eval (confident-ai) — step-by-step criteria evaluation
  - LLM-as-Judge best practices (arXiv:2508.08285, evidentlyai) — rubric design

Architecture:
  1. Parse task.md → extract rubric criteria (or use defaults)
  2. Parse gen_dir → find output files (report.md, submission.json, etc.)
  3. Parse evidence_log.json → hallucination_rate (from Layer 1 web search)
  4. Run LLM judge with schema-constrained output (Rulers method)
  5. Return OpenTaskResult with:
     - output_score (0-100): quality of final output
     - evidence_score (0-100): quality of evidence gathered (InfoDeepSeek IA@5)
     - hallucination_rate (0-1): from EvidenceLog
     - overall_score (0-100): weighted → Regime Detector
     - checklist: per-criterion verdict with evidence quotes
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import httpx
import openai

logger = logging.getLogger(__name__)

# ─── Constants ─────────────────────────────────────────────────────────────────
DEFAULT_JUDGE_MODEL = "openai/gpt-oss-120b:free"
MAX_OUTPUT_CHARS = 12_000   # max chars of agent output sent to judge
MAX_TASK_CHARS = 3_000      # max chars of task.md sent to judge
JUDGE_TIMEOUT = 120
OUTPUT_SCORE_WEIGHT = 0.50
EVIDENCE_SCORE_WEIGHT = 0.30
HALLUCINATION_PENALTY_WEIGHT = 0.20

# Output file candidates (searched in order)
OUTPUT_FILE_CANDIDATES = [
    "micro_task_report.md",
    "report.md",
    "output.md",
    "results/micro_task_report.md",
    "results/report.md",
    "results/output.md",
    "submission.json",
    "results.json",
    "answers.json",
    # agent_execution.json is intentionally excluded — it's a system file
]


# ─── Result Types ──────────────────────────────────────────────────────────────
@dataclass
class CriterionVerdict:
    """
    Stolen from Rulers — schema-constrained per-criterion evaluation.
    Every verdict MUST include an evidence_quote from the actual output.
    Unquoted verdicts = judge hallucination.
    """
    criterion: str
    met: bool
    score: float          # 0-1
    evidence_quote: str   # exact text from output supporting this verdict
    source_url: str | None = None  # from evidence_log if available
    explanation: str = ""


@dataclass
class OpenTaskResult:
    """
    Full evaluation result for one generation of an open task.
    Persisted as open_task_eval.json in the gen directory.
    """
    gen_dir: str
    output_file: str | None
    output_score: float        # 0-100: final output quality
    evidence_score: float      # 0-100: evidence quality (InfoDeepSeek IA@5 inspired)
    hallucination_rate: float  # 0-1: from EvidenceLog
    overall_score: float       # 0-100: weighted → Regime Detector
    checklist: list[CriterionVerdict] = field(default_factory=list)
    judge_model: str = DEFAULT_JUDGE_MODEL
    task_name: str = ""
    error: str | None = None
    skipped: bool = False
    skip_reason: str = ""

    @property
    def regime_signal(self) -> float:
        """Normalized 0-1 signal for Regime Detector."""
        return self.overall_score / 100.0

    def to_dict(self) -> dict:
        d = asdict(self)
        d["regime_signal"] = self.regime_signal
        return d

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info(f"Open task eval saved: {path} (overall={self.overall_score:.1f})")

    @classmethod
    def load(cls, path: str) -> "OpenTaskResult":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        data.pop("regime_signal", None)
        checklist_raw = data.pop("checklist", [])
        result = cls(**data)
        result.checklist = [CriterionVerdict(**c) for c in checklist_raw]
        return result

    @classmethod
    def skipped_result(cls, gen_dir: str, reason: str) -> "OpenTaskResult":
        return cls(
            gen_dir=gen_dir,
            output_file=None,
            output_score=0.0,
            evidence_score=0.0,
            hallucination_rate=0.0,
            overall_score=0.0,
            skipped=True,
            skip_reason=reason,
        )


# ─── Rubric Extraction ─────────────────────────────────────────────────────────
DEFAULT_RUBRIC = [
    "The output directly addresses the task objectives stated in task.md",
    "Claims are specific and actionable — not vague or generic",
    "The output is honest about what could not be verified (says 'unverified' explicitly)",
    "The output is well-structured with clear sections",
    "No obvious fabricated facts or hallucinated links",
]

def extract_rubric_from_task(task_md: str) -> list[str]:
    """
    Extract evaluation criteria from task.md.
    Looks for 'Evaluation Criteria', 'Scoring', or 'Criteria' sections.
    Falls back to DEFAULT_RUBRIC.
    """
    criteria = []
    lines = task_md.split("\n")
    in_criteria_section = False

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()

        # Detect criteria section headers
        if any(kw in lower for kw in [
            "evaluation criteria", "scoring", "criteria", "rubric",
            "معايير التقييم", "معايير", "التقييم"
        ]):
            in_criteria_section = True
            continue

        # Exit section on next header
        if in_criteria_section and stripped.startswith("#"):
            in_criteria_section = False

        # Extract numbered or bulleted criteria
        if in_criteria_section and stripped:
            # Remove leading bullets/numbers
            clean = stripped.lstrip("0123456789.-*•·").strip()
            if len(clean) > 10:  # ignore very short lines
                criteria.append(clean)

    return criteria[:8] if criteria else DEFAULT_RUBRIC


# ─── Output File Discovery ─────────────────────────────────────────────────────
def find_output_file(gen_dir: str) -> tuple[str | None, str]:
    """
    Find the main output file from the agent.
    Returns (path, content) or (None, "").
    """
    for candidate in OUTPUT_FILE_CANDIDATES:
        path = os.path.join(gen_dir, candidate)
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                logger.info(f"Output file found: {path} ({len(content)} chars)")
                return path, content
            except Exception as e:
                logger.warning(f"Could not read {path}: {e}")

    # System/internal files — never treat as agent output
    EXCLUDED_FILES = {
        "agent_execution.json", "constitutional_report.json",
        "regime_transition_report.json", "open_task_eval.json",
        "evidence_log.json", "evolutionary_discovery.json",
        "regime_history.json", "meta.json",
        "target_agent_stdout.log", "evaluation.log",
    }
    # Last resort: look for any .md or .json in gen_dir
    for ext in [".md", ".json"]:
        for fname in sorted(os.listdir(gen_dir)):  # sorted for determinism
            if not fname.endswith(ext):
                continue
            if fname in EXCLUDED_FILES:
                continue
                path = os.path.join(gen_dir, fname)
                try:
                    with open(path, encoding="utf-8") as f:
                        content = f.read()
                    logger.info(f"Output file found (fallback): {path}")
                    return path, content
                except Exception:
                    pass

    return None, ""


# ─── Evidence Log Loading ──────────────────────────────────────────────────────
def load_evidence_stats(gen_dir: str) -> dict:
    """
    Load hallucination_rate and evidence stats from evidence_log.json (Layer 1 output).
    Returns defaults if not found.
    """
    evidence_path = os.path.join(gen_dir, "evidence_log.json")
    if not os.path.exists(evidence_path):
        # Try results/ subdir
        evidence_path = os.path.join(gen_dir, "results", "evidence_log.json")

    if os.path.exists(evidence_path):
        try:
            with open(evidence_path, encoding="utf-8") as f:
                data = json.load(f)
            summary = data.get("summary", {})
            logger.info(f"Evidence log loaded: {evidence_path}")
            return {
                "hallucination_rate": summary.get("hallucination_rate", 0.0),
                "verified_claims": summary.get("verified_claims", 0),
                "total_claims": summary.get("total_claims", 0),
                "searches_performed": summary.get("searches_performed", 0),
                "pages_read": summary.get("pages_read", 0),
                "found": True,
            }
        except Exception as e:
            logger.warning(f"Could not load evidence log: {e}")

    return {
        "hallucination_rate": 0.0,
        "verified_claims": 0,
        "total_claims": 0,
        "searches_performed": 0,
        "pages_read": 0,
        "found": False,
    }


# ─── LLM Judge (Rulers method) ─────────────────────────────────────────────────
JUDGE_SYSTEM_PROMPT = """You are a strict, objective evaluator. Your job is to assess an AI agent's output against specific criteria.

CRITICAL RULES (stolen from Rulers arXiv:2601.08654):
1. For each criterion, you MUST provide an exact quote from the output that supports your verdict.
2. If you cannot find a quote supporting your verdict, mark met=false.
3. Do NOT hallucinate — every claim must be grounded in the actual output text.
4. Be strict: vague outputs that don't clearly meet the criterion = not met.
5. Return ONLY valid JSON — no markdown, no explanation outside JSON.
"""

def _build_judge_prompt(
    output_text: str,
    task_md: str,
    criteria: list[str],
) -> str:
    criteria_json = json.dumps(criteria, ensure_ascii=False, indent=2)
    return f"""TASK SPECIFICATION:
{task_md[:MAX_TASK_CHARS]}

---
AGENT OUTPUT TO EVALUATE:
{output_text[:MAX_OUTPUT_CHARS]}

---
EVALUATION CRITERIA:
{criteria_json}

---
Return a JSON object with this EXACT structure:
{{
  "criteria_verdicts": [
    {{
      "criterion": "exact criterion text",
      "met": true or false,
      "score": 0.0 to 1.0,
      "evidence_quote": "exact quote from the output (max 200 chars) — REQUIRED",
      "explanation": "one sentence explanation"
    }}
  ],
  "output_score": 0 to 100,
  "summary": "2-3 sentence overall assessment",
  "main_weakness": "the most important thing to fix",
  "main_strength": "the best thing the agent did"
}}

Rules:
- evidence_quote MUST be a substring of the agent output (or "NOT FOUND" if criterion not met)
- output_score = weighted average of all criterion scores * 100
- Be strict but fair
"""


def run_llm_judge(
    output_text: str,
    task_md: str,
    criteria: list[str],
    llm_client: openai.OpenAI,
    judge_model: str,
    retry: int = 2,
) -> dict:
    """
    Run LLM-as-Judge with schema-constrained output.
    Returns parsed dict or error dict.
    """
    prompt = _build_judge_prompt(output_text, task_md, criteria)

    for attempt in range(retry + 1):
        try:
            response = llm_client.chat.completions.create(
                model=judge_model,
                messages=[
                    {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=4000,
            )
            raw = (response.choices[0].message.content or "").strip()

            # Extract JSON from response
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start < 0 or end <= start:
                raise ValueError(f"No JSON found in judge response: {raw[:200]}")

            data = json.loads(raw[start:end])
            logger.info(f"Judge response parsed: output_score={data.get('output_score', '?')}")
            return {"status": "ok", "data": data}

        except json.JSONDecodeError as e:
            logger.warning(f"Judge JSON parse error (attempt {attempt+1}): {e}")
            if attempt < retry:
                time.sleep(1)
        except openai.RateLimitError:
            logger.warning(f"Judge rate limit (attempt {attempt+1})")
            if attempt < retry:
                time.sleep(3 * (attempt + 1))
        except Exception as e:
            logger.error(f"Judge error (attempt {attempt+1}): {e}")
            if attempt < retry:
                time.sleep(1)

    return {"status": "error", "error": "Judge failed after retries"}


# ─── Evidence Score (InfoDeepSeek IA@5 inspired) ──────────────────────────────
def compute_evidence_score(evidence_stats: dict, output_text: str) -> float:
    """
    Stolen from InfoDeepSeek IA@5 concept:
    Measure evidence quality INDEPENDENTLY of output quality.

    Heuristics:
      - searches_performed > 0 → agent searched (good)
      - hallucination_rate low → most claims verified
      - verified_claims > 0 → actual sources found
      - output contains URLs → evidence referenced in output
      - output contains dates → freshness of sources

    Returns 0-100.
    """
    score = 0.0

    # Did agent search at all?
    if evidence_stats["found"]:
        searches = evidence_stats.get("searches_performed", 0)
        pages = evidence_stats.get("pages_read", 0)
        verified = evidence_stats.get("verified_claims", 0)
        total = evidence_stats.get("total_claims", 0)
        hallucination_rate = evidence_stats.get("hallucination_rate", 1.0)

        # Search activity (30 points)
        if searches > 0:
            score += min(30, searches * 6)  # 5 searches = max 30 pts
        if pages > 0:
            score += min(10, pages * 5)     # 2 pages = max 10 pts

        # Claim verification (40 points)
        if total > 0:
            verification_ratio = verified / total
            score += verification_ratio * 40
        elif searches > 0:
            # Searched but didn't track claims — partial credit
            score += 15

        # Hallucination penalty (20 points)
        score += (1 - hallucination_rate) * 20

    else:
        # No evidence log — check output for URL patterns heuristically
        url_count = output_text.count("http://") + output_text.count("https://")
        date_hints = sum(1 for y in ["2024", "2025", "2026"] if y in output_text)

        if url_count > 0:
            score += min(30, url_count * 5)
        if date_hints > 0:
            score += min(15, date_hints * 5)

        # No evidence log = max 45 pts (can't verify)
        score = min(45, score)

    return min(100.0, max(0.0, score))


# ─── Main Evaluator ────────────────────────────────────────────────────────────
def run_open_task_evaluation(
    gen_dir: str,
    task_dir: str,
    llm_client: openai.OpenAI | None = None,
    judge_model: str = DEFAULT_JUDGE_MODEL,
    force: bool = False,
) -> OpenTaskResult:
    """
    Main entry point — runs when evaluate.py is missing.

    Steps:
      1. Check if evaluate.py exists → if yes, skip (let run_evaluation handle it)
      2. Find output file in gen_dir
      3. Load task.md rubric
      4. Load evidence_log.json stats (hallucination_rate)
      5. Run LLM judge (Rulers method)
      6. Compute evidence_score (InfoDeepSeek IA@5)
      7. Compute overall_score (weighted)
      8. Save open_task_eval.json

    Args:
        gen_dir: path to current generation directory
        task_dir: path to task directory (has task.md + possibly evaluate.py)
        llm_client: openai.OpenAI client — if None, uses env vars
        judge_model: model for judging
        force: run even if open_task_eval.json already exists

    Returns:
        OpenTaskResult
    """
    eval_path = os.path.join(gen_dir, "open_task_eval.json")

    # Already evaluated?
    if not force and os.path.exists(eval_path):
        try:
            result = OpenTaskResult.load(eval_path)
            logger.info(f"Open task eval loaded from cache: {eval_path}")
            return result
        except Exception:
            pass

    # Check if closed eval exists — don't duplicate
    evaluate_script = os.path.join(task_dir, "data/public/evaluate.py")
    if not os.path.exists(evaluate_script):
        evaluate_script = os.path.join(task_dir, "evaluate.py")
    if os.path.exists(evaluate_script) and not force:
        return OpenTaskResult.skipped_result(gen_dir, "evaluate.py exists — closed eval handles this")

    # Find output
    output_file, output_text = find_output_file(gen_dir)
    if not output_text:
        result = OpenTaskResult.skipped_result(gen_dir, "No output file found in gen_dir")
        result.save(eval_path)
        return result

    # Load task.md
    task_md = ""
    for candidate in ["data/public/task.md", "task.md"]:
        p = os.path.join(task_dir, candidate)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                task_md = f.read()
            break

    criteria = extract_rubric_from_task(task_md)
    logger.info(f"Rubric: {len(criteria)} criteria extracted")

    # Load evidence stats
    evidence_stats = load_evidence_stats(gen_dir)

    # Setup LLM client
    if llm_client is None:
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        if api_key:
            http_client = httpx.Client(headers={"Accept-Encoding": "identity"}, timeout=JUDGE_TIMEOUT)
            llm_client = openai.OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)
        else:
            logger.warning("No LLM client — skipping judge, using heuristic scores only")

    # Run LLM judge
    output_score = 0.0
    checklist: list[CriterionVerdict] = []
    judge_error = None

    if llm_client is not None:
        judge_result = run_llm_judge(
            output_text=output_text,
            task_md=task_md,
            criteria=criteria,
            llm_client=llm_client,
            judge_model=judge_model,
        )

        if judge_result["status"] == "ok":
            data = judge_result["data"]
            output_score = float(data.get("output_score", 0))

            for cv in data.get("criteria_verdicts", []):
                checklist.append(CriterionVerdict(
                    criterion=cv.get("criterion", ""),
                    met=bool(cv.get("met", False)),
                    score=float(cv.get("score", 0)),
                    evidence_quote=cv.get("evidence_quote", "NOT FOUND"),
                    explanation=cv.get("explanation", ""),
                ))
        else:
            judge_error = judge_result.get("error", "unknown error")
            logger.warning(f"LLM judge failed: {judge_error} — falling back to heuristic")
            # Heuristic fallback: short output = low score
            output_score = min(50, len(output_text) / 200)
    else:
        # No LLM — pure heuristic
        output_score = min(50, len(output_text) / 200)

    # Evidence score (InfoDeepSeek IA@5)
    evidence_score = compute_evidence_score(evidence_stats, output_text)

    # Hallucination rate
    hallucination_rate = evidence_stats.get("hallucination_rate", 0.0)

    # Overall score (weighted)
    # Penalty for hallucination: high hallucination_rate reduces overall
    hallucination_penalty = hallucination_rate * 100 * HALLUCINATION_PENALTY_WEIGHT
    overall_score = (
        output_score * OUTPUT_SCORE_WEIGHT
        + evidence_score * EVIDENCE_SCORE_WEIGHT
        - hallucination_penalty
    )
    overall_score = max(0.0, min(100.0, overall_score))

    result = OpenTaskResult(
        gen_dir=gen_dir,
        output_file=output_file,
        output_score=round(output_score, 2),
        evidence_score=round(evidence_score, 2),
        hallucination_rate=round(hallucination_rate, 4),
        overall_score=round(overall_score, 2),
        checklist=checklist,
        judge_model=judge_model,
        task_name=Path(task_dir).name,
        error=judge_error,
    )

    result.save(eval_path)

    logger.info(
        f"Open task eval complete: output={output_score:.1f} "
        f"evidence={evidence_score:.1f} "
        f"hallucination={hallucination_rate:.0%} "
        f"overall={overall_score:.1f}"
    )
    return result


# ─── Convenience: load result for Regime Detector ─────────────────────────────
def load_open_task_score(gen_dir: str) -> float | None:
    """
    Load the overall_score from a completed evaluation.
    Returns None if no evaluation exists.
    Used by Regime Detector as additional signal.
    """
    eval_path = os.path.join(gen_dir, "open_task_eval.json")
    if not os.path.exists(eval_path):
        return None
    try:
        result = OpenTaskResult.load(eval_path)
        return result.overall_score if not result.skipped else None
    except Exception:
        return None
