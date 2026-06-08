"""
GENESIS Goal Specification Layer — Layer 3
===========================================
Section 0: runs BEFORE Meta-Agent, ONCE per run.

Stolen from:
  - MA-RAG (arXiv:2505.20096) — Planner/Step Definer architecture
  - Enterprise Deep Research (arXiv:2510.17797) — task annotation with priority+domain
  - HTN Planning (Hierarchical Task Networks) — hierarchical goal decomposition
  - SAGE (arXiv:2602.05975) — keyword extraction per sub-goal for precise search
  - Deep Research Survey (arXiv:2508.12752) — Planning → sub-goals → evidence

What it does:
  1. Reads task.md
  2. Decomposes into Primary Goal → ordered Sub-goals (MA-RAG Planner)
  3. For each sub-goal: generates search queries + keywords (Step Definer + SAGE)
  4. Tags each sub-goal: priority, domain, success_criterion
  5. Saves goal_spec.json → fed to Meta-Agent prompt

Key design decision (from your insight):
  Scope = GLOBAL first, then local filter.
  The agent searches globally (all opportunities) THEN applies local filter (Egypt).
  This prevents premature narrowing that loses global opportunities.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any

import httpx
import openai

logger = logging.getLogger(__name__)

# ─── Constants ─────────────────────────────────────────────────────────────────
DEFAULT_MODEL = "openai/gpt-oss-120b:free"
MAX_TASK_CHARS = 4000
MAX_SUB_GOALS = 6
GOAL_SPEC_FILENAME = "goal_spec.json"

# Search domains (from Enterprise Deep Research arXiv:2510.17797)
SEARCH_DOMAINS = ["web", "academic", "forum", "social", "news", "official"]


# ─── Data Classes ──────────────────────────────────────────────────────────────
@dataclass
class SubGoal:
    """
    One decomposed sub-goal.
    Stolen from MA-RAG Step Definer: each sub-goal gets its own search plan.
    """
    id: str                          # sg1, sg2, ...
    description: str                 # what needs to be found/done
    priority: int                    # 1 = highest (do first, most important)
    success_criterion: str           # how to know this sub-goal is complete
    search_queries: list[str]        # 2-3 queries for web_search()
    keywords: list[str]              # 3-5 keywords (SAGE insight: BM25 precision)
    domain: str                      # web | academic | forum | social | news
    scope: str                       # global | local | both
    local_filter: str                # e.g. "Egypt" — applied AFTER global search
    is_primary: bool = False         # is this the main goal?

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GoalSpec:
    """
    Complete goal specification for a run.
    Saved as goal_spec.json in run directory.
    Injected into Meta-Agent prompt as structured context.
    """
    task_name: str
    primary_goal: str                # one sentence: the highest-level objective
    success_criteria: list[str]      # 2-4 measurable criteria for the whole task
    priority_principle: str          # e.g. "Global opportunities first, then Egypt filter"
    scope: str                       # "global" | "local" | "global_then_local"
    local_filter: str                # e.g. "Egypt" or "" for global
    sub_goals: list[SubGoal]        # ordered by priority
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    model_used: str = ""
    task_md_hash: str = ""

    @property
    def ordered_sub_goals(self) -> list[SubGoal]:
        """Sub-goals sorted by priority (1=first)."""
        return sorted(self.sub_goals, key=lambda sg: sg.priority)

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info(f"Goal spec saved: {path} ({len(self.sub_goals)} sub-goals)")

    @classmethod
    def load(cls, path: str) -> "GoalSpec":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        sub_goals_raw = data.pop("sub_goals", [])
        spec = cls(**data, sub_goals=[])
        spec.sub_goals = [SubGoal(**sg) for sg in sub_goals_raw]
        return spec

    def to_prompt_section(self) -> str:
        """
        Format as a section to inject into Meta-Agent prompt.
        Tells the agent: here's your goal hierarchy, search in this order.
        """
        lines = [
            "═══════════════════════════════════════════════════════════",
            "🎯 GOAL SPECIFICATION (Section 0 — Pre-computed)",
            "═══════════════════════════════════════════════════════════",
            f"PRIMARY GOAL: {self.primary_goal}",
            f"SCOPE: {self.scope} → {self.priority_principle}",
            "",
            "SUCCESS CRITERIA (task is complete when ALL are met):",
        ]
        for i, sc in enumerate(self.success_criteria, 1):
            lines.append(f"  {i}. {sc}")

        lines.append("")
        lines.append("SUB-GOALS (execute in priority order — DO NOT skip any):")
        for sg in self.ordered_sub_goals:
            lines.append(f"")
            lines.append(f"  [{sg.priority}] {sg.id} — {sg.description}")
            lines.append(f"      Domain: {sg.domain} | Scope: {sg.scope}")
            lines.append(f"      Success: {sg.success_criterion}")
            lines.append(f"      Search queries: {sg.search_queries[:2]}")
            lines.append(f"      Keywords: {sg.keywords[:4]}")
            if sg.local_filter:
                lines.append(f"      Local filter (apply AFTER global): '{sg.local_filter}'")

        lines.append("")
        lines.append("CRITICAL STRATEGY (from goal decomposition):")
        lines.append(f"  • Start with GLOBAL scope — don't filter by '{self.local_filter}' immediately")
        lines.append(f"  • After finding global opportunities, check each for '{self.local_filter}' availability")
        lines.append(f"  • An opportunity with unknown local status is BETTER than no opportunity at all")
        lines.append(f"  • Be explicit: 'Available in {self.local_filter}: YES/NO/UNKNOWN'")
        lines.append("═══════════════════════════════════════════════════════════")

        return "\n".join(lines)


# ─── LLM-based Decomposition ──────────────────────────────────────────────────
DECOMPOSITION_SYSTEM = """You are a strategic research planner. Your job is to decompose a complex task into a structured goal hierarchy.

Key principles (stolen from MA-RAG + Enterprise Deep Research + HTN):
1. Primary goal = single sentence describing the highest-value outcome
2. Sub-goals = ordered by priority (what matters MOST = priority 1)
3. Scope = GLOBAL first — never pre-filter geographically before searching
4. Each sub-goal gets precise search queries (stolen from SAGE: specific keywords beat long queries)
5. Success criterion = measurable, not vague

Return ONLY valid JSON — no markdown, no extra text.
"""


def _build_decomposition_prompt(task_md: str, local_filter: str = "") -> str:
    local_hint = f"\nLocal filter to apply AFTER global search: '{local_filter}'" if local_filter else ""

    return f"""Analyze this task and decompose it into a goal hierarchy:

TASK:
{task_md[:MAX_TASK_CHARS]}
{local_hint}

Return this EXACT JSON structure:
{{
  "primary_goal": "one sentence — the highest-value outcome of this task",
  "success_criteria": [
    "measurable criterion 1",
    "measurable criterion 2",
    "measurable criterion 3"
  ],
  "priority_principle": "one sentence — strategy for ordering sub-goals (e.g. 'Global opportunities first, then filter by Egypt')",
  "scope": "global_then_local",
  "sub_goals": [
    {{
      "id": "sg1",
      "description": "what specifically needs to be found/done",
      "priority": 1,
      "success_criterion": "how to know this sub-goal is complete",
      "search_queries": [
        "precise search query 1",
        "precise search query 2"
      ],
      "keywords": ["keyword1", "keyword2", "keyword3"],
      "domain": "web",
      "scope": "global",
      "local_filter": "{local_filter}",
      "is_primary": true
    }}
  ]
}}

Rules:
- 3-6 sub-goals, ordered by priority (1=most important)
- search_queries: 2-3 per sub-goal, specific and diverse (not the same query rephrased)
- keywords: 3-5 precise terms for BM25 search (SAGE insight: shorter = more precise)
- domain options: web | academic | forum | social | news | official
- scope: "global" for sub-goals that search everywhere, "local" for sub-goals focused on specific region
- DO NOT put local filter in first 2 sub-goals — find global opportunities first
- If local_filter is not empty, add a dedicated sub-goal (last priority) for local availability check
"""


def decompose_task_with_llm(
    task_md: str,
    llm_client: openai.OpenAI,
    model: str = DEFAULT_MODEL,
    local_filter: str = "",
    retry: int = 2,
) -> dict | None:
    """
    Use LLM to decompose task into goal hierarchy (MA-RAG Planner pattern).
    Returns raw dict or None on failure.
    """
    prompt = _build_decomposition_prompt(task_md, local_filter)

    for attempt in range(retry + 1):
        try:
            response = llm_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": DECOMPOSITION_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=3000,
            )
            raw = (response.choices[0].message.content or "").strip()

            # Extract JSON
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start < 0 or end <= start:
                raise ValueError(f"No JSON in response: {raw[:200]}")

            data = json.loads(raw[start:end])
            logger.info(f"Goal decomposition: {len(data.get('sub_goals', []))} sub-goals")
            return data

        except json.JSONDecodeError as e:
            logger.warning(f"Goal decomp JSON error (attempt {attempt+1}): {e}")
            if attempt < retry:
                time.sleep(1)
        except openai.RateLimitError:
            logger.warning(f"Goal decomp rate limit (attempt {attempt+1})")
            if attempt < retry:
                time.sleep(3)
        except Exception as e:
            logger.error(f"Goal decomp error (attempt {attempt+1}): {e}")
            if attempt < retry:
                time.sleep(1)

    return None


# ─── Heuristic Fallback ───────────────────────────────────────────────────────
def _heuristic_decompose(task_md: str, task_name: str, local_filter: str) -> dict:
    """
    Fallback when LLM unavailable.
    Creates a sensible default goal spec from task.md keywords.
    Stolen from HTN planning: pattern-match task type → default decomposition.
    """
    task_lower = task_md.lower()

    # Detect task type
    is_research = any(kw in task_lower for kw in
                      ["research", "find", "discover", "search", "بحث", "ابحث", "اجد"])
    is_coding = any(kw in task_lower for kw in
                    ["code", "implement", "function", "class", "algorithm"])
    is_analysis = any(kw in task_lower for kw in
                      ["analyze", "compare", "evaluate", "assess", "تحليل"])

    if is_research:
        return {
            "primary_goal": f"Find actionable information to complete: {task_name}",
            "success_criteria": [
                "At least 3 verified sources found",
                "Key claims supported by evidence",
                "Output addresses all task requirements",
            ],
            "priority_principle": "Global search first, then apply local filters",
            "scope": "global_then_local",
            "sub_goals": [
                {
                    "id": "sg1", "priority": 1, "is_primary": True,
                    "description": "Find primary information globally",
                    "success_criterion": "3+ relevant sources found",
                    "search_queries": [task_name, f"{task_name} best options"],
                    "keywords": task_name.split()[:4],
                    "domain": "web", "scope": "global",
                    "local_filter": "",
                },
                {
                    "id": "sg2", "priority": 2, "is_primary": False,
                    "description": "Verify credibility of found information",
                    "success_criterion": "Each major claim has a source URL",
                    "search_queries": [f"{task_name} review", f"{task_name} scam OR legitimate"],
                    "keywords": ["review", "scam", "verified", "proof"],
                    "domain": "forum", "scope": "global",
                    "local_filter": "",
                },
                {
                    "id": "sg3", "priority": 3, "is_primary": False,
                    "description": f"Check local availability for: {local_filter}" if local_filter else "Summarize findings",
                    "success_criterion": f"Each item marked: available in {local_filter} YES/NO/UNKNOWN" if local_filter else "Summary complete",
                    "search_queries": [f"{task_name} {local_filter}"] if local_filter else [f"{task_name} summary"],
                    "keywords": [local_filter] + task_name.split()[:2] if local_filter else task_name.split()[:3],
                    "domain": "web", "scope": "local" if local_filter else "global",
                    "local_filter": local_filter,
                },
            ]
        }

    elif is_coding:
        return {
            "primary_goal": f"Implement a working solution for: {task_name}",
            "success_criteria": [
                "Code runs without errors",
                "Output matches required format",
                "All edge cases handled",
            ],
            "priority_principle": "Correctness first, then efficiency",
            "scope": "global",
            "sub_goals": [
                {
                    "id": "sg1", "priority": 1, "is_primary": True,
                    "description": "Understand requirements and design approach",
                    "success_criterion": "Clear implementation plan",
                    "search_queries": [task_name, f"{task_name} best approach"],
                    "keywords": task_name.split()[:4],
                    "domain": "academic", "scope": "global", "local_filter": "",
                },
                {
                    "id": "sg2", "priority": 2, "is_primary": False,
                    "description": "Implement core logic",
                    "success_criterion": "Core functionality works",
                    "search_queries": [f"{task_name} implementation", f"{task_name} example"],
                    "keywords": ["implementation", "algorithm", "code"],
                    "domain": "web", "scope": "global", "local_filter": "",
                },
            ]
        }

    else:
        # Generic analysis task
        return {
            "primary_goal": f"Complete: {task_name}",
            "success_criteria": [
                "Task requirements fully addressed",
                "Output is well-structured",
                "Key findings are verified",
            ],
            "priority_principle": "Address core requirements first",
            "scope": "global",
            "sub_goals": [
                {
                    "id": "sg1", "priority": 1, "is_primary": True,
                    "description": "Address primary task requirements",
                    "success_criterion": "All main requirements covered",
                    "search_queries": [task_name],
                    "keywords": task_name.split()[:4],
                    "domain": "web", "scope": "global", "local_filter": local_filter,
                },
            ]
        }


def _parse_goal_spec_from_dict(data: dict, task_name: str) -> GoalSpec:
    """Convert raw LLM dict into GoalSpec dataclass."""
    sub_goals = []
    for sg_data in data.get("sub_goals", [])[:MAX_SUB_GOALS]:
        sub_goals.append(SubGoal(
            id=sg_data.get("id", f"sg{len(sub_goals)+1}"),
            description=sg_data.get("description", ""),
            priority=int(sg_data.get("priority", len(sub_goals)+1)),
            success_criterion=sg_data.get("success_criterion", ""),
            search_queries=sg_data.get("search_queries", [])[:3],
            keywords=sg_data.get("keywords", [])[:5],
            domain=sg_data.get("domain", "web"),
            scope=sg_data.get("scope", "global"),
            local_filter=sg_data.get("local_filter", ""),
            is_primary=bool(sg_data.get("is_primary", False)),
        ))

    return GoalSpec(
        task_name=task_name,
        primary_goal=data.get("primary_goal", f"Complete task: {task_name}"),
        success_criteria=data.get("success_criteria", ["Task completed successfully"])[:4],
        priority_principle=data.get("priority_principle", "Priority order as listed"),
        scope=data.get("scope", "global"),
        local_filter=data.get("local_filter", ""),
        sub_goals=sub_goals,
    )


# ─── Main Entry Point ──────────────────────────────────────────────────────────
def run_goal_specification(
    task_md: str,
    task_name: str,
    run_dir: str,
    llm_client: openai.OpenAI | None = None,
    model: str = DEFAULT_MODEL,
    local_filter: str = "",
    force: bool = False,
) -> GoalSpec:
    """
    Section 0 — runs once per run, before Meta-Agent.
    
    Steps:
      1. Check cache (goal_spec.json in run_dir)
      2. Decompose task with LLM (MA-RAG Planner)
      3. Fallback to heuristic if LLM fails
      4. Save goal_spec.json
      5. Return GoalSpec (used to build Meta-Agent prompt section)

    Args:
        task_md: content of task.md
        task_name: name of the task (e.g. "micro_task")
        run_dir: run directory path (e.g. runs/run_55)
        llm_client: openai.OpenAI client
        model: model for decomposition
        local_filter: geographic filter (e.g. "Egypt") — applied AFTER global search
        force: re-run even if cache exists

    Returns:
        GoalSpec with ordered sub-goals and search plans
    """
    spec_path = os.path.join(run_dir, GOAL_SPEC_FILENAME)

    # Check cache
    if not force and os.path.exists(spec_path):
        try:
            spec = GoalSpec.load(spec_path)
            logger.info(f"Goal spec loaded from cache: {spec_path}")
            return spec
        except Exception:
            pass

    # Setup LLM client if not provided
    if llm_client is None:
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        if api_key:
            http_client = httpx.Client(headers={"Accept-Encoding": "identity"}, timeout=60)
            llm_client = openai.OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)

    # Decompose
    data = None
    used_heuristic = False
    if llm_client is not None:
        data = decompose_task_with_llm(task_md, llm_client, model, local_filter)

    if data is None:
        logger.warning("LLM decomposition failed — using heuristic fallback")
        data = _heuristic_decompose(task_md, task_name, local_filter)
        data["local_filter"] = local_filter
        used_heuristic = True

    spec = _parse_goal_spec_from_dict(data, task_name)
    spec.model_used = "heuristic" if used_heuristic else model
    spec.local_filter = local_filter

    # Save
    os.makedirs(run_dir, exist_ok=True)
    spec.save(spec_path)

    logger.info(
        f"Goal spec created: primary='{spec.primary_goal[:60]}' "
        f"sub_goals={len(spec.sub_goals)} scope={spec.scope}"
    )
    return spec
