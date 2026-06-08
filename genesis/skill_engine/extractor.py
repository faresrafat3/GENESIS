"""
GENESIS Skill Engine — Skill Extractor
========================================
Component: SKILL_ENGINE.extractor
Source: MUSE-Autoskill + EvoSkill

STOLEN_FROM:
  MUSE-Autoskill (arXiv:2605.27366):
    - Skills created from successful agent trajectories
    - Skill creation = structured pipeline: SKILL.md → scripts → tests

  EvoSkill (arXiv:2603.02766):
    - FailureCollector: collects cases where score < threshold
    - Failure analysis feeds ProposerAgent
    - Structured failure cases: question, output, expected, trace

GENESIS_ADAPTATION:
  - SkillExtractor reads target_agent.py (not runtime traces)
  - Extracts reusable Python patterns (functions, strategies)
  - LLM identifies what made the agent successful
  - FailureCollector reads gen artifacts (open_task_eval, evaluation_results)

CALLED_BY:
  - genesis/orchestrator.py Section 5a.1 (on success: score > threshold)
  - genesis/skill_engine/evolver.py (FailureCollector for ProposerAgent)

CALLS:
  - LLM (for pattern identification)
  - genesis/skill_engine/skill.py (Skill, SkillFolder)
  - genesis/skill_engine/evaluator.py (SkillEvaluator — validates before register)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from genesis.skill_engine.skill import Skill, SkillContract, SkillFolder

logger = logging.getLogger(__name__)

EXTRACTION_THRESHOLD = 70.0   # only extract from high-scoring gens
FAILURE_THRESHOLD = 0.6       # collect failures below this score


# ─── FailureCase (EvoSkill) ───────────────────────────────────────────────────

@dataclass
class FailureCase:
    """
    EvoSkill FailureCollector: structured failure for ProposerAgent.
    Contains enough info for diagnosis without ground-truth leakage.
    """
    gen: int
    task_description: str
    agent_output_excerpt: str     # first 500 chars of output
    score: float
    hallucination_rate: float
    error_trace: str              # from open_task_eval.json or evaluation_results
    criterion_failures: list[str] = field(default_factory=list)


class FailureCollector:
    """
    EvoSkill Proposer input: collect failures for diagnosis.
    Reads gen artifacts (open_task_eval.json, evaluation_results.json).
    """

    def collect(
        self,
        run_dir: str,
        current_gen: int,
        threshold: float = FAILURE_THRESHOLD,
    ) -> list[FailureCase]:
        """
        Collect failure cases from all gens up to current_gen.
        EvoSkill: scores below threshold → failure case.
        """
        failures = []
        run_path = Path(run_dir)

        for gen in range(1, current_gen + 1):
            gen_dir = run_path / f"gen_{gen}"
            if not gen_dir.exists():
                continue

            # Try open_task_eval.json (open tasks)
            eval_path = gen_dir / "open_task_eval.json"
            if eval_path.exists():
                try:
                    with open(eval_path) as f:
                        data = json.load(f)
                    score = data.get("overall_score", 100.0) / 100.0
                    if score < threshold:
                        failures.append(self._make_failure_case(gen, data, gen_dir))
                except Exception as e:
                    logger.warning(f"Could not read open_task_eval.json gen {gen}: {e}")

            # Try evaluation_results.json (closed tasks)
            elif (gen_dir / "evaluation_results.json").exists():
                try:
                    with open(gen_dir / "evaluation_results.json") as f:
                        data = json.load(f)
                    accuracy = data.get("accuracy", 1.0)
                    if accuracy < threshold:
                        failures.append(FailureCase(
                            gen=gen,
                            task_description="Multiple choice evaluation",
                            agent_output_excerpt=f"accuracy={accuracy:.2f}",
                            score=accuracy,
                            hallucination_rate=0.0,
                            error_trace=json.dumps(data.get("domain_breakdown", {}))[:500],
                        ))
                except Exception as e:
                    logger.warning(f"Could not read evaluation_results.json gen {gen}: {e}")

        logger.info(f"Collected {len(failures)} failure cases (threshold={threshold})")
        return failures

    def _make_failure_case(self, gen: int, eval_data: dict, gen_dir: Path) -> FailureCase:
        """Build FailureCase from open_task_eval.json data."""
        checklist = eval_data.get("checklist", [])
        criterion_failures = [
            c.get("criterion", "")
            for c in checklist
            if not c.get("met", True)
        ]

        # Try to get output excerpt
        output_excerpt = ""
        for fname in ["micro_task_report.md", "report.md", "output.md"]:
            fpath = gen_dir / fname
            if fpath.exists():
                output_excerpt = fpath.read_text(encoding="utf-8")[:500]
                break
        if not output_excerpt:
            results_dir = gen_dir / "results"
            for fname in ["micro_task_report.md", "report.md"]:
                fpath = results_dir / fname if results_dir.exists() else None
                if fpath and fpath.exists():
                    output_excerpt = fpath.read_text(encoding="utf-8")[:500]
                    break

        return FailureCase(
            gen=gen,
            task_description=eval_data.get("task_name", "unknown task"),
            agent_output_excerpt=output_excerpt,
            score=eval_data.get("overall_score", 0.0) / 100.0,
            hallucination_rate=eval_data.get("hallucination_rate", 0.0),
            error_trace=eval_data.get("error", "")[:500],
            criterion_failures=criterion_failures[:5],
        )


# ─── SkillExtractor ───────────────────────────────────────────────────────────

class SkillExtractor:
    """
    Extracts reusable skills from successful target_agent.py.
    MUSE pattern: create skill from successful trajectory.
    Genesis adaptation: source = target_agent.py (not runtime traces).
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def extract_from_agent(
        self,
        agent_path: str,
        score: float,
        run_id: str = "",
        gen_id: int = 0,
    ) -> list[Skill]:
        """
        Extract reusable skills from a successful target_agent.py.
        Only extract if score > EXTRACTION_THRESHOLD.

        Steps:
          1. Read agent code
          2. LLM: identify reusable patterns
          3. For each pattern: build Skill object
          4. Return list (caller will evaluate + register)
        """
        if score < EXTRACTION_THRESHOLD:
            logger.info(f"Score {score:.1f} < threshold {EXTRACTION_THRESHOLD} — no extraction")
            return []

        if not os.path.exists(agent_path):
            logger.warning(f"Agent file not found: {agent_path}")
            return []

        agent_code = open(agent_path, encoding="utf-8").read()
        logger.info(f"Extracting skills from agent (score={score:.1f}, {len(agent_code)} chars)")

        if self.llm_client:
            return self._llm_extraction(agent_code, score, run_id, gen_id)
        else:
            return self._heuristic_extraction(agent_code, score, run_id, gen_id)

    def _llm_extraction(
        self, code: str, score: float, run_id: str, gen_id: int
    ) -> list[Skill]:
        """LLM-based skill extraction."""
        prompt = f"""
Analyze this successful agent code (score={score:.1f}/100) and identify 1-3 reusable skills.

A skill = a specific, reusable code pattern that:
  - Solves a recurring problem
  - Can be used in future agents independently
  - Has clear inputs, outputs, and use cases

CODE:
{code[:4000]}

For each skill, output JSON:
{{
  "skills": [
    {{
      "name": "snake_case_skill_name",
      "description": "one-line description",
      "domain": "research|coding|analysis|grounding",
      "task_types": ["list", "of", "task", "types"],
      "when_to_use": ["bullet 1", "bullet 2"],
      "core_principles": ["principle 1", "principle 2"],
      "recommended_tools": ["tool names"],
      "workflow": "step by step instructions",
      "preconditions": ["what must be true to use this"],
      "operation": "what this skill does",
      "artifact_type": "what it produces (json|text|list)",
      "validator": "how to verify output",
      "failure_modes": ["known failures"]
    }}
  ]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.llm_client.chat.completions.create(
                model=os.getenv("TASK_MODEL", "openai/gpt-oss-20b:free"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.1,
            )
            raw = response.choices[0].message.content or ""
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start < 0 or end <= start:
                return self._heuristic_extraction(code, score, run_id, gen_id)

            data = json.loads(raw[start:end])
            skills = []
            for s_data in data.get("skills", [])[:3]:
                skill = self._build_skill_from_llm(s_data, score, run_id, gen_id)
                if skill:
                    skills.append(skill)
            return skills

        except Exception as e:
            logger.warning(f"LLM extraction failed: {e} — using heuristic")
            return self._heuristic_extraction(code, score, run_id, gen_id)

    def _build_skill_from_llm(
        self, data: dict, score: float, run_id: str, gen_id: int
    ) -> Skill | None:
        """Build Skill from LLM extraction output."""
        name = data.get("name", "").strip().replace(" ", "_").lower()
        if not name:
            return None

        contract = SkillContract(
            preconditions=data.get("preconditions", []),
            operation=data.get("operation", ""),
            artifact_type=data.get("artifact_type", ""),
            validator=data.get("validator", ""),
            failure_modes=data.get("failure_modes", []),
        )

        return Skill(
            name=name,
            description=data.get("description", ""),
            domain=data.get("domain", "general"),
            task_types=data.get("task_types", []),
            when_to_use=data.get("when_to_use", []),
            core_principles=data.get("core_principles", []),
            recommended_tools=data.get("recommended_tools", []),
            workflow=data.get("workflow", ""),
            contract=contract,
            performance_score=score,
            source_run=run_id,
            source_gen=gen_id,
        )

    def _heuristic_extraction(
        self, code: str, score: float, run_id: str, gen_id: int
    ) -> list[Skill]:
        """
        Heuristic extraction without LLM.
        Detects: web_search usage, evidence_log pattern, multi-turn pattern.
        """
        skills = []

        # Pattern: web search + evidence tracking
        if "web_search" in code and "EvidenceLog" in code:
            skills.append(Skill(
                name=f"web_search_evidence_{gen_id}",
                description="Search web and track evidence with credibility scoring",
                domain="research",
                task_types=["research", "fact_finding", "verification"],
                when_to_use=[
                    "Task requires real-world information",
                    "Platform availability needs verification",
                    "Claims need source citation",
                ],
                core_principles=[
                    "Search globally first, filter locally after",
                    "Every claim needs a source URL",
                    "Mark unverified claims explicitly",
                ],
                recommended_tools=["web_search", "extract_keywords"],
                workflow=(
                    "1. Extract keywords from query\n"
                    "2. Search globally (mode=quick)\n"
                    "3. Deep read top results (mode=read)\n"
                    "4. Log each claim in EvidenceLog\n"
                    "5. Save evidence_log.json"
                ),
                contract=SkillContract(
                    preconditions=["SERPER_API_KEY available"],
                    operation="web search + evidence tracking",
                    artifact_type="evidence_log.json",
                    validator="evidence_log.json exists with hallucination_rate field",
                    failure_modes=["Rate limit", "No results", "No API key"],
                ),
                performance_score=score,
                source_run=run_id,
                source_gen=gen_id,
            ))

        # Pattern: multi-turn critique
        if "self-critique" in code.lower() or "critique" in code.lower():
            skills.append(Skill(
                name=f"multi_turn_critique_{gen_id}",
                description="Generate output then self-critique and refine",
                domain="analysis",
                task_types=["report_generation", "analysis", "research"],
                when_to_use=[
                    "Output quality needs improvement",
                    "Hallucination rate should be minimized",
                ],
                core_principles=[
                    "Always critique your own output",
                    "Second pass improves accuracy significantly",
                ],
                workflow=(
                    "1. Generate initial output\n"
                    "2. Critique: identify hallucinations and gaps\n"
                    "3. Refine based on critique\n"
                    "4. Save final version"
                ),
                performance_score=score,
                source_run=run_id,
                source_gen=gen_id,
            ))

        return skills
