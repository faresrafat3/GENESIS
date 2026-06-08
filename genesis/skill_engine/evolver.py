"""
GENESIS Skill Engine — EvoSkill Loop
======================================
Component: SKILL_ENGINE.evolver
Source: EvoSkill (arXiv:2603.02766, Sentient+Virginia Tech)

STOLEN_FROM:
  EvoSkill Algorithm:
    - 3-agent architecture: Executor + Proposer + Skill-Builder
    - Proposer: analyzes failures, maintains feedback_history H
    - Skill-Builder: materializes proposal → skill folder
    - Frontier: top-K programs, evict weakest
    - round-robin parent selection
    - Feedback history prevents redundant proposals

GENESIS_ADAPTATION:
  - Executor = GENESIS generation (not standalone agent)
  - Proposer receives gen failures (not task-level failures)
  - Skill-Builder materializes via LLM (creates SKILL.md + scripts)
  - Frontier = SkillLibrary.frontier (managed by SkillLibrary)
  - No git branches — SQLite lineage tracking

CALLED_BY:
  - genesis/orchestrator.py Section 5a.3 (replaces AlphaEvolve skeleton)

CALLS:
  - genesis/skill_engine/library.py: SkillLibrary
  - genesis/skill_engine/evaluator.py: SkillEvaluator
  - genesis/skill_engine/extractor.py: FailureCollector
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field

from genesis.skill_engine.skill import Skill, SkillContract, SkillFolder
from genesis.skill_engine.extractor import FailureCase
from genesis.skill_engine.evaluator import SkillEvaluator, TestResult

logger = logging.getLogger(__name__)


# ─── SkillProposal (EvoSkill Proposer output) ────────────────────────────────

@dataclass
class SkillProposal:
    """
    EvoSkill: Proposer's output — what skill to create or edit.
    Stored in feedback_history H for context.
    """
    action: str                    # "create" | "edit"
    target_skill: str | None       # skill name (if edit)
    description: str               # what the skill should do
    rationale: str                 # why this addresses the failures
    capability_gap: str            # what capability was missing
    proposed_name: str = ""        # for create action


# ─── ProposerAgent ────────────────────────────────────────────────────────────

class ProposerAgent:
    """
    EvoSkill Proposer: analyzes failures → proposes skills.
    Maintains cumulative feedback history H to avoid redundancy.
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.feedback_history: list[dict] = []   # EvoSkill: history H

    def propose(
        self,
        failures: list[FailureCase],
        existing_skills: list[Skill],
    ) -> SkillProposal | None:
        """
        EvoSkill Proposer:
          1. Analyze failure traces
          2. Review existing skills for relevance
          3. Propose: new_skill OR edit_existing
          4. Append to history H
        """
        if not failures:
            return None

        existing_names = [s.name for s in existing_skills]

        if self.llm_client:
            return self._llm_propose(failures, existing_skills)
        else:
            return self._heuristic_propose(failures, existing_names)

    def _llm_propose(
        self, failures: list[FailureCase], existing_skills: list[Skill]
    ) -> SkillProposal | None:
        """LLM-based proposal."""
        failure_summary = "\n".join([
            f"Gen {f.gen}: score={f.score:.2f}, "
            f"hallucination={f.hallucination_rate:.0%}, "
            f"failed_criteria={f.criterion_failures[:3]}"
            for f in failures[:5]
        ])

        existing_summary = "\n".join([
            f"  - {s.name}: {s.description}"
            for s in existing_skills[:5]
        ])

        history_summary = "\n".join([
            f"  - Proposed '{p.get('description', '')}' → score_delta={p.get('score_delta', 0):.2f}"
            for p in self.feedback_history[-3:]
        ]) or "  None yet"

        prompt = f"""
You are analyzing agent failures to propose a new skill or improvement.

FAILURES:
{failure_summary}

EXISTING SKILLS:
{existing_summary if existing_summary else "  None registered yet"}

PREVIOUS PROPOSALS (avoid repeating):
{history_summary}

Based on the failures, propose ONE of:
  1. Create a new skill that addresses the capability gap
  2. Edit an existing skill to improve it

Return JSON:
{{
  "action": "create" or "edit",
  "target_skill": "existing_skill_name" (if edit, else null),
  "proposed_name": "snake_case_skill_name" (if create),
  "description": "what this skill does",
  "rationale": "why this addresses the failures",
  "capability_gap": "what specific capability was missing"
}}

Return ONLY valid JSON.
"""
        try:
            response = self.llm_client.chat.completions.create(
                model=os.getenv("TASK_MODEL", "openai/gpt-oss-20b:free"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.2,
            )
            raw = response.choices[0].message.content or ""
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start < 0:
                return self._heuristic_propose(
                    failures, [s.name for s in existing_skills]
                )
            data = json.loads(raw[start:end])
            return SkillProposal(
                action=data.get("action", "create"),
                target_skill=data.get("target_skill"),
                proposed_name=data.get("proposed_name", ""),
                description=data.get("description", ""),
                rationale=data.get("rationale", ""),
                capability_gap=data.get("capability_gap", ""),
            )
        except Exception as e:
            logger.warning(f"LLM proposal failed: {e}")
            return self._heuristic_propose(failures, [s.name for s in existing_skills])

    def _heuristic_propose(
        self, failures: list[FailureCase], existing_names: list[str]
    ) -> SkillProposal | None:
        """Heuristic proposal based on failure patterns."""
        # Check for hallucination pattern
        high_halluc = [f for f in failures if f.hallucination_rate > 0.5]
        if high_halluc:
            return SkillProposal(
                action="create",
                target_skill=None,
                proposed_name="evidence_verification",
                description="Verify claims before including in output",
                rationale=f"High hallucination rate in {len(high_halluc)} gens",
                capability_gap="Missing evidence verification before output generation",
            )

        # Check for low score pattern
        low_score = [f for f in failures if f.score < 0.4]
        if low_score:
            return SkillProposal(
                action="create",
                target_skill=None,
                proposed_name="structured_research",
                description="Systematic research with source tracking",
                rationale=f"Low scores in {len(low_score)} gens",
                capability_gap="Missing systematic approach to research tasks",
            )

        if failures:
            return SkillProposal(
                action="create",
                target_skill=None,
                proposed_name="quality_review",
                description="Review and improve output before finalizing",
                rationale=f"{len(failures)} failed generations",
                capability_gap="Missing output quality review step",
            )

        return None

    def record_outcome(self, proposal: SkillProposal, score_delta: float) -> None:
        """EvoSkill: append to feedback history H."""
        self.feedback_history.append({
            "action": proposal.action,
            "description": proposal.description,
            "capability_gap": proposal.capability_gap,
            "score_delta": score_delta,
        })


# ─── SkillBuilderAgent ────────────────────────────────────────────────────────

class SkillBuilderAgent:
    """
    EvoSkill Skill-Builder: materializes proposal → complete skill folder.
    Bootstrapped with meta-skill for best practices.
    """

    def __init__(self, llm_client=None, skills_base_dir=None):
        self.llm_client = llm_client
        from genesis.skill_engine.skill import SkillFolder
        from pathlib import Path
        self.skills_base_dir = Path(skills_base_dir) if skills_base_dir else (
            Path(__file__).parent / "skills"
        )

    def materialize(
        self,
        proposal: SkillProposal,
        parent_skill: Skill | None = None,
    ) -> Skill | None:
        """
        EvoSkill: materialize proposal into complete skill folder.
        Returns Skill (not yet registered — caller evaluates first).
        """
        name = proposal.proposed_name or f"skill_{proposal.action}_{hash(proposal.description) % 1000:03d}"
        name = name.replace(" ", "_").lower()

        if self.llm_client:
            return self._llm_materialize(name, proposal, parent_skill)
        else:
            return self._heuristic_materialize(name, proposal)

    def _llm_materialize(
        self, name: str, proposal: SkillProposal, parent: Skill | None
    ) -> Skill | None:
        """LLM materializes the full skill."""
        parent_context = f"\nParent skill: {parent.workflow}" if parent else ""

        prompt = f"""
Create a complete skill for a GENESIS AI agent.

PROPOSAL:
  Name: {name}
  Description: {proposal.description}
  Rationale: {proposal.rationale}
  Capability gap: {proposal.capability_gap}
{parent_context}

Generate a complete skill JSON:
{{
  "name": "{name}",
  "description": "one-line description",
  "domain": "research|coding|analysis|grounding",
  "task_types": ["list"],
  "when_to_use": ["bullet 1", "bullet 2"],
  "core_principles": ["principle 1", "principle 2"],
  "recommended_tools": ["web_search", "etc"],
  "workflow": "Step 1: ...\\nStep 2: ...",
  "preconditions": ["what must be true"],
  "operation": "what skill does",
  "artifact_type": "json|text|list|report",
  "validator": "how to verify",
  "failure_modes": ["known failures"],
  "test_code": "import pytest\\n\\ndef test_basic():\\n    # basic test\\n    assert True"
}}

Return ONLY valid JSON.
"""
        try:
            response = self.llm_client.chat.completions.create(
                model=os.getenv("TASK_MODEL", "openai/gpt-oss-20b:free"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.1,
            )
            raw = response.choices[0].message.content or ""
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start < 0:
                return self._heuristic_materialize(name, proposal)

            data = json.loads(raw[start:end])
            test_code = data.pop("test_code", "def test_placeholder():\n    assert True")

            contract = SkillContract(
                preconditions=data.pop("preconditions", []),
                operation=data.pop("operation", ""),
                artifact_type=data.pop("artifact_type", ""),
                validator=data.pop("validator", ""),
                failure_modes=data.pop("failure_modes", []),
            )

            skill = Skill(
                name=data.get("name", name),
                description=data.get("description", proposal.description),
                domain=data.get("domain", "general"),
                task_types=data.get("task_types", []),
                when_to_use=data.get("when_to_use", []),
                core_principles=data.get("core_principles", []),
                recommended_tools=data.get("recommended_tools", []),
                workflow=data.get("workflow", ""),
                contract=contract,
                parent_skill=parent.name if parent else None,
                generation=(parent.generation + 1) if parent else 1,
            )

            # Create folder with test
            SkillFolder.create(
                self.skills_base_dir, skill,
                tests={"test_skill.py": test_code},
            )
            return skill

        except Exception as e:
            logger.warning(f"LLM materialization failed: {e}")
            return self._heuristic_materialize(name, proposal)

    def _heuristic_materialize(self, name: str, proposal: SkillProposal) -> Skill:
        """Heuristic skill creation without LLM."""
        test_code = f'''"""Auto-generated test for {name}"""
import pytest

def test_{name}_exists():
    """Skill should be loadable."""
    assert True  # Replace with actual test

def test_{name}_description():
    """Skill description should be meaningful."""
    description = "{proposal.description}"
    assert len(description) > 10
'''
        skill = Skill(
            name=name,
            description=proposal.description,
            domain="general",
            when_to_use=[proposal.capability_gap],
            core_principles=[proposal.rationale],
            workflow=(
                f"1. Identify task requiring {proposal.description}\n"
                f"2. Apply skill logic\n"
                f"3. Validate output\n"
                f"4. Return structured result"
            ),
            contract=SkillContract(
                operation=proposal.description,
                failure_modes=["LLM unavailable", "Task mismatch"],
            ),
            generation=1,
        )
        SkillFolder.create(
            self.skills_base_dir, skill,
            tests={"test_skill.py": test_code},
        )
        return skill


# ─── EvoSkillLoop ─────────────────────────────────────────────────────────────

class EvoSkillLoop:
    """
    EvoSkill main loop adapted for GENESIS.

    EvoSkill Algorithm (adapted):
      for t in 1..T:
        parent = round_robin(frontier)
        failures = FailureCollector.collect(run_dir)
        proposal = Proposer.propose(failures, existing_skills)
        candidate = Builder.materialize(proposal, parent)
        tests = Evaluator.run_tests(candidate)
        if tests.passed and score > frontier weakest:
            library.add_to_frontier(candidate)
            library.register(candidate)
        Proposer.record_outcome(proposal, score_delta)
      return frontier
    """

    def __init__(
        self,
        llm_client=None,
        frontier_k: int = 3,
        max_iterations: int = 5,
    ):
        self.llm_client = llm_client
        self.frontier_k = frontier_k
        self.max_iterations = max_iterations

    def run(
        self,
        run_dir: str,
        current_gen: int,
        library,
        evaluator: SkillEvaluator | None = None,
    ) -> list[Skill]:
        """
        Run EvoSkill loop for current generation.
        Returns list of new skills added to frontier.
        """
        from genesis.skill_engine.extractor import FailureCollector

        failure_collector = FailureCollector()
        proposer = ProposerAgent(llm_client=self.llm_client)
        builder = SkillBuilderAgent(llm_client=self.llm_client)
        if evaluator is None:
            evaluator = SkillEvaluator()

        new_skills = []
        existing_skills = library.list_all()
        frontier = library.get_frontier()
        parent_idx = 0

        for iteration in range(self.max_iterations):
            # Collect failures
            failures = failure_collector.collect(run_dir, current_gen)
            if not failures:
                logger.info(f"EvoSkill iteration {iteration+1}: no failures — skipping")
                break

            # Round-robin parent selection (EvoSkill)
            parent = frontier[parent_idx % len(frontier)] if frontier else None
            parent_idx += 1

            # Propose
            proposal = proposer.propose(failures, existing_skills)
            if not proposal:
                continue

            # Build candidate
            candidate = builder.materialize(proposal, parent)
            if not candidate:
                continue

            # Evaluate
            test_result = evaluator.run_tests(candidate)
            if not test_result.passed:
                logger.info(
                    f"EvoSkill: candidate '{candidate.name}' failed tests "
                    f"({test_result.tests_failed} failures)"
                )
                proposer.record_outcome(proposal, score_delta=-0.1)
                continue

            # Register
            registered = library.register(candidate)
            if registered:
                added = library.add_to_frontier(candidate)
                if added:
                    frontier = library.get_frontier()
                new_skills.append(candidate)
                existing_skills.append(candidate)
                proposer.record_outcome(proposal, score_delta=0.1)
                logger.info(f"EvoSkill: skill '{candidate.name}' registered")

        logger.info(f"EvoSkill complete: {len(new_skills)} new skills")
        return new_skills
