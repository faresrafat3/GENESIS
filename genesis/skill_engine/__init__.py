"""
GENESIS Skill Engine
======================
Component: SKILL_ENGINE
Source: MUSE-Autoskill + EvoSkill + SkillOps + SoK

Clean public API — ONLY import point for orchestrator:

  from genesis.skill_engine import register, retrieve, get_catalog, run_evo

Orchestrator integration:
  Section 3:    get_catalog() → SKILL_SECTION in META_AGENT_PROMPT
  Section 5a.1: register(skill) on high score
  Section 5a.3: run_evo() replaces AlphaEvolve skeleton
  Section 5b:   retrieve(query) → SKILL_FEEDBACK in feedback prompt

Full docs: AGENT_DEVELOPMENT_CONTEXT.md → COMPONENT_ID: SKILL_ENGINE
"""

from __future__ import annotations

import logging
from pathlib import Path

from genesis.skill_engine.skill import Skill, SkillContract, SkillFolder
from genesis.skill_engine.library import SkillLibrary, HealthReport
from genesis.skill_engine.evaluator import SkillEvaluator, TestResult
from genesis.skill_engine.extractor import SkillExtractor, FailureCollector, FailureCase
from genesis.skill_engine.retriever import SkillRetriever
from genesis.skill_engine.evolver import EvoSkillLoop, ProposerAgent, SkillBuilderAgent

logger = logging.getLogger(__name__)

# ─── Singleton instances ───────────────────────────────────────────────────────
_DEFAULT_SKILLS_DIR = Path(__file__).parent / "skills"
_library = SkillLibrary(skills_dir=_DEFAULT_SKILLS_DIR)
_evaluator = SkillEvaluator()
_retriever = SkillRetriever()

# ─── Public API ───────────────────────────────────────────────────────────────

def register(skill: Skill, skip_eval: bool = False) -> bool:
    """
    Register a skill. Evaluates tests first (MUSE create→evaluate→register).
    skip_eval=True: register without testing (use for pre-validated skills).
    Returns True if registered.
    """
    if not skip_eval and skill.has_tests:
        result = _evaluator.run_tests(skill)
        if not result.passed:
            logger.warning(
                f"Skill '{skill.name}' failed tests — not registered. "
                f"Failures: {result.failures[:3]}"
            )
            return False
    return _library.register(skill)


def retrieve(
    query: str,
    top_k: int = 3,
    domain: str | None = None,
    task_type: str | None = None,
    context: dict | None = None,
) -> list[Skill]:
    """
    Retrieve relevant skills via hybrid BM25+semantic (SkillOps).
    Returns ranked list of Skill objects.
    """
    return _retriever.retrieve(
        query, _library, top_k=top_k,
        domain_filter=domain, task_type_filter=task_type, context=context
    )


def get_catalog() -> str:
    """
    Get skill catalog for META_AGENT_PROMPT injection.
    Progressive disclosure: name + description only (MUSE).
    """
    return _library.get_catalog_prompt()


def get_catalog_yaml() -> str:
    """YAML format catalog."""
    return _library.get_catalog_yaml()


def get_skill(name: str) -> Skill | None:
    """Get skill by name."""
    return _library.get(name)


def run_evo(
    run_dir: str,
    current_gen: int,
    llm_client=None,
    max_iterations: int = 3,
) -> list[Skill]:
    """
    Run EvoSkill loop (EvoSkill Proposer+Builder+Evaluator).
    Returns new skills added to frontier.
    Used in orchestrator Section 5a.3 (replaces AlphaEvolve skeleton).
    """
    loop = EvoSkillLoop(
        llm_client=llm_client,
        max_iterations=max_iterations,
    )
    return loop.run(run_dir, current_gen, _library, _evaluator)


def extract_from_agent(
    agent_path: str,
    score: float,
    run_id: str = "",
    gen_id: int = 0,
    llm_client=None,
) -> list[Skill]:
    """
    Extract skills from successful target_agent.py.
    Returns extracted+validated skills (not yet registered).
    Caller decides whether to register.
    """
    extractor = SkillExtractor(llm_client=llm_client)
    return extractor.extract_from_agent(agent_path, score, run_id, gen_id)


def health_check() -> HealthReport:
    """SkillOps health diagnosis."""
    return _library.health_check()


def run_maintenance() -> int:
    """SkillOps O(N) maintenance pass. Returns actions taken."""
    return _library.run_maintenance()


def get_stats() -> dict:
    """Library statistics for Telemetry Engine."""
    return _library.get_stats()


def get_frontier() -> list[Skill]:
    """EvoSkill: get top-K frontier skills."""
    return _library.get_frontier()


def retire(name: str) -> bool:
    """SkillOps retire action: remove skill."""
    return _library.retire(name)


# ─── Re-exports ───────────────────────────────────────────────────────────────
__all__ = [
    # Classes
    "Skill", "SkillContract", "SkillFolder",
    "SkillLibrary", "HealthReport",
    "SkillEvaluator", "TestResult",
    "SkillExtractor", "FailureCollector", "FailureCase",
    "SkillRetriever",
    "EvoSkillLoop", "ProposerAgent", "SkillBuilderAgent",
    # Functions
    "register", "retrieve", "get_catalog", "get_catalog_yaml",
    "get_skill", "run_evo", "extract_from_agent",
    "health_check", "run_maintenance", "get_stats",
    "get_frontier", "retire",
]
