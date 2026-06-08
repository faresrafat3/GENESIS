"""
GENESIS Skill Engine — Skill Definition
=========================================
Component: SKILL_ENGINE.skill
Source: Multiple papers 2026

STOLEN_FROM:
  MUSE-Autoskill (arXiv:2605.27366, ByteDance+Rochester):
    - SKILL.md format (Anthropic Agent Skills standard)
    - .memory.md per skill (accumulated experience across tasks)
    - Progressive disclosure: catalog = name+description only in system prompt
    - Skill directory structure: SKILL.md + scripts/ + tests/ + resources/

  SkillOps (arXiv:2605.13716, Emory+UIUC):
    - SkillContract (P,O,A,V,F): Precondition, Operation, Artifact, Validator, Failure
    - Contract-based skill representation for graph reasoning

  EvoSkill (arXiv:2603.02766, Sentient+VT):
    - Skill lineage: parent_skill, generation (mutation depth)
    - frontier_rank for Pareto selection

  SoK: Agentic Skills (arXiv:2602.20867):
    - Formal definition: S = (C, π, T, R)
    - Termination criteria concept

GENESIS_ADAPTATION:
  - Skills = agent code patterns (not Minecraft functions)
  - Extracted from successful target_agent.py generations
  - performance_score feeds from CRITIC_ENGINE (open_task_eval.json)
  - EvidenceLog from GROUNDING_ENGINE informs skill quality

CALLED_BY:
  - genesis/skill_engine/library.py (SkillLibrary)
  - genesis/skill_engine/evaluator.py (SkillEvaluator)
  - genesis/skill_engine/extractor.py (SkillExtractor)
  - genesis/tool_hub/__init__.py (skill_use tool — Phase 2 end)
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


# ─── Skill Contract (P, O, A, V, F) ──────────────────────────────────────────

@dataclass
class SkillContract:
    """
    SkillOps contract model: (P, O, A, V, F)
    Enables: precondition checking, type validation, failure anticipation.
    validation_gap = validator == "" (no correctness check).
    """
    preconditions: list[str] = field(default_factory=list)   # P: when applicable
    operation: str = ""                                        # O: what it does
    artifact_type: str = ""                                    # A: what it produces
    validator: str = ""                                        # V: how to verify ("" = gap)
    failure_modes: list[str] = field(default_factory=list)    # F: known failures

    @property
    def has_validation_gap(self) -> bool:
        """SkillOps: V = ∅ → validation gap."""
        return not self.validator.strip()

    def check_preconditions(self, context: dict) -> tuple[bool, list[str]]:
        """
        Check if preconditions are met.
        Returns (met: bool, unmet_conditions: list[str]).
        Simple string-matching check — override for complex logic.
        """
        unmet = []
        for pc in self.preconditions:
            pc_lower = pc.lower()
            if "api_key" in pc_lower or "_key" in pc_lower or "env" in pc_lower:
                # Check env var existence — match any WORD_KEY or WORD_API_KEY pattern
                key_match = re.search(r'\b([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*_(?:API_)?KEY)\b', pc)
                if not key_match:
                    # Fallback: match any ALL_CAPS_WORD that ends in KEY
                    key_match = re.search(r'([A-Z_]+KEY[A-Z_]*)', pc)
                if key_match:
                    env_key = key_match.group(1).upper()
                    if not os.getenv(env_key):
                        unmet.append(f"Missing env var: {env_key}")
        return len(unmet) == 0, unmet

    def to_dict(self) -> dict:
        return {
            "preconditions": self.preconditions,
            "operation": self.operation,
            "artifact_type": self.artifact_type,
            "validator": self.validator,
            "failure_modes": self.failure_modes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SkillContract":
        return cls(**data)


# ─── Skill ────────────────────────────────────────────────────────────────────

@dataclass
class Skill:
    """
    A single skill — the core unit of SKILL_ENGINE.

    Stolen from:
      - MUSE: SKILL.md format + .memory.md + lifecycle
      - SkillOps: contract (P,O,A,V,F) + typed artifacts
      - EvoSkill: lineage (parent, generation, frontier_rank)
      - SoK: formal definition S = (C, π, T, R)

    Genesis adaptation:
      - Skills are code patterns from successful target_agent.py
      - performance_score from CRITIC_ENGINE (not manual rating)
      - domain/task_types enable SkillRetriever to find relevant skills
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    name: str
    version: str = "1.0.0"
    domain: str = "general"           # research | coding | analysis | grounding
    task_types: list[str] = field(default_factory=list)

    # ── SKILL.md content ──────────────────────────────────────────────────────
    description: str = ""             # CATALOG ONLY — minimal tokens
    when_to_use: list[str] = field(default_factory=list)
    core_principles: list[str] = field(default_factory=list)
    recommended_tools: list[str] = field(default_factory=list)
    workflow: str = ""                # step-by-step in SKILL.md
    instructions: str = ""            # full body (loaded on demand)

    # ── SkillOps contract ─────────────────────────────────────────────────────
    contract: SkillContract = field(default_factory=SkillContract)

    # ── Filesystem ────────────────────────────────────────────────────────────
    skill_dir: Path = field(default=None)

    # ── Metrics ───────────────────────────────────────────────────────────────
    performance_score: float = 0.0    # from CRITIC_ENGINE (0-100)
    usage_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_used_at: str = ""

    # ── Lineage (EvoSkill) ────────────────────────────────────────────────────
    source_run: str = ""
    source_gen: int = 0
    generation: int = 0               # mutation depth from root (0 = original)
    parent_skill: str | None = None   # name of parent skill
    frontier_rank: int | None = None  # rank in EvoSkill frontier (None = not in frontier)

    def __post_init__(self):
        if self.skill_dir is not None:
            self.skill_dir = Path(self.skill_dir)

    # ── Filesystem paths ──────────────────────────────────────────────────────

    @property
    def skill_md_path(self) -> Path | None:
        if self.skill_dir:
            return self.skill_dir / "SKILL.md"
        return None

    @property
    def scripts_dir(self) -> Path | None:
        if self.skill_dir:
            return self.skill_dir / "scripts"
        return None

    @property
    def tests_dir(self) -> Path | None:
        if self.skill_dir:
            return self.skill_dir / "tests"
        return None

    @property
    def resources_dir(self) -> Path | None:
        if self.skill_dir:
            return self.skill_dir / "resources"
        return None

    @property
    def memory_file(self) -> Path | None:
        """MUSE: .memory.md — accumulated experience, hidden from catalog."""
        if self.skill_dir:
            return self.skill_dir / ".memory.md"
        return None

    @property
    def has_scripts(self) -> bool:
        return self.scripts_dir is not None and self.scripts_dir.exists()

    @property
    def has_tests(self) -> bool:
        return self.tests_dir is not None and self.tests_dir.exists()

    # ── Catalog & Discovery ───────────────────────────────────────────────────

    def get_catalog_entry(self) -> str:
        """
        MUSE progressive disclosure: catalog = name + description only.
        This is what goes in META_AGENT_PROMPT system prompt.
        """
        score_str = f" [score:{self.performance_score:.0f}]" if self.performance_score > 0 else ""
        usage_str = f" [used:{self.usage_count}x]" if self.usage_count > 0 else ""
        return f"  {self.name}: {self.description}{score_str}{usage_str}"

    def get_full_body(self) -> str:
        """Full SKILL.md content — loaded on demand (progressive disclosure)."""
        if self.skill_md_path and self.skill_md_path.exists():
            return self.skill_md_path.read_text(encoding="utf-8")
        return self._build_skill_md()

    def _build_skill_md(self) -> str:
        """Build SKILL.md content from dataclass fields."""
        lines = [
            f"---",
            f"name: {self.name}",
            f"description: {self.description}",
            f"domain: {self.domain}",
            f"version: {self.version}",
            f"---",
            f"",
            f"# {self.name}",
            f"",
        ]
        if self.when_to_use:
            lines.append("## When to use")
            for item in self.when_to_use:
                lines.append(f"- {item}")
            lines.append("")

        if self.core_principles:
            lines.append("## Core principles")
            for i, p in enumerate(self.core_principles, 1):
                lines.append(f"{i}. {p}")
            lines.append("")

        if self.recommended_tools:
            lines.append("## Recommended tools")
            for t in self.recommended_tools:
                lines.append(f"- {t}")
            lines.append("")

        if self.workflow:
            lines.append("## Workflow")
            lines.append(self.workflow)
            lines.append("")

        return "\n".join(lines)

    # ── Memory (MUSE .memory.md) ──────────────────────────────────────────────

    def read_memory(self) -> str:
        """Read accumulated experience from .memory.md."""
        if self.memory_file and self.memory_file.exists():
            return self.memory_file.read_text(encoding="utf-8")
        return ""

    def append_memory(self, note: str, task_context: str = "") -> None:
        """
        MUSE: append note to .memory.md after each use.
        Notes accumulate across tasks — not cleared on reset.
        """
        if self.memory_file is None:
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n## [{timestamp}]"
        if task_context:
            entry += f" Task: {task_context}"
        entry += f"\n{note}\n"
        mode = "a" if self.memory_file.exists() else "w"
        self.memory_file.open(mode, encoding="utf-8").write(entry)

    # ── Metrics ───────────────────────────────────────────────────────────────

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

    def record_use(self, success: bool, note: str = "") -> None:
        """Record a use (updates counts and optionally memory)."""
        self.usage_count += 1
        self.last_used_at = datetime.now().isoformat()
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        if note:
            self.append_memory(note)

    # ── Content Hash ──────────────────────────────────────────────────────────

    @property
    def body_hash(self) -> str:
        """
        SkillOps: body-hash for redundancy detection.
        Uses instructions field only (not SKILL.md which includes name/description).
        Skills with same instructions = redundant.
        """
        content = self.instructions if self.instructions.strip() else self.workflow
        return hashlib.md5(content.encode()).hexdigest()[:8]

    # ── Serialization ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """JSON-serializable dict. schema_version for Artifact Registry."""
        return {
            "schema_version": "1.0",
            "component": "SKILL_ENGINE",
            "name": self.name,
            "version": self.version,
            "domain": self.domain,
            "task_types": self.task_types,
            "description": self.description,
            "when_to_use": self.when_to_use,
            "core_principles": self.core_principles,
            "recommended_tools": self.recommended_tools,
            "workflow": self.workflow,
            "contract": self.contract.to_dict(),
            "skill_dir": str(self.skill_dir) if self.skill_dir else None,
            "performance_score": self.performance_score,
            "usage_count": self.usage_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "created_at": self.created_at,
            "last_used_at": self.last_used_at,
            "source_run": self.source_run,
            "source_gen": self.source_gen,
            "generation": self.generation,
            "parent_skill": self.parent_skill,
            "frontier_rank": self.frontier_rank,
            "body_hash": self.body_hash,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Skill":
        data = dict(data)
        data.pop("schema_version", None)
        data.pop("component", None)
        data.pop("body_hash", None)
        contract_data = data.pop("contract", {})
        skill_dir = data.pop("skill_dir", None)
        skill = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        skill.contract = SkillContract.from_dict(contract_data) if contract_data else SkillContract()
        if skill_dir:
            skill.skill_dir = Path(skill_dir)
        return skill


# ─── SkillFolder ──────────────────────────────────────────────────────────────

class SkillFolder:
    """
    Creates and reads skill folder packages (filesystem).
    Stolen from: MUSE-Autoskill directory structure + Anthropic Agent Skills format.

    Structure:
      skill_name/
        SKILL.md          ← instructions (YAML frontmatter + body)
        scripts/          ← executable Python/Bash
        tests/            ← pytest-compatible
        resources/        ← data files, templates
        .memory.md        ← accumulated experience (hidden from catalog)
    """

    @staticmethod
    def create(
        base_dir: Path,
        skill: Skill,
        scripts: dict[str, str] | None = None,
        tests: dict[str, str] | None = None,
        resources: dict[str, str] | None = None,
    ) -> Path:
        """
        Create skill folder from Skill object.
        Returns path to created folder.
        """
        skill_path = base_dir / skill.name
        skill_path.mkdir(parents=True, exist_ok=True)

        # SKILL.md
        (skill_path / "SKILL.md").write_text(skill._build_skill_md(), encoding="utf-8")

        # scripts/
        if scripts:
            scripts_dir = skill_path / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            for fname, content in scripts.items():
                (scripts_dir / fname).write_text(content, encoding="utf-8")

        # tests/
        if tests:
            tests_dir = skill_path / "tests"
            tests_dir.mkdir(exist_ok=True)
            for fname, content in tests.items():
                (tests_dir / fname).write_text(content, encoding="utf-8")

        # resources/
        if resources:
            res_dir = skill_path / "resources"
            res_dir.mkdir(exist_ok=True)
            for fname, content in resources.items():
                (res_dir / fname).write_text(content, encoding="utf-8")

        skill.skill_dir = skill_path
        return skill_path

    @staticmethod
    def from_path(skill_dir: Path) -> Skill:
        """Load Skill from existing folder (reads SKILL.md)."""
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

        content = skill_md.read_text(encoding="utf-8")
        name, description, domain, version, body = SkillFolder._parse_skill_md(content)

        skill = Skill(
            name=name or skill_dir.name,
            description=description,
            domain=domain,
            version=version,
            workflow=body,
            skill_dir=skill_dir,
        )
        return skill

    @staticmethod
    def _parse_skill_md(content: str) -> tuple[str, str, str, str, str]:
        """Parse SKILL.md: extract YAML frontmatter + body."""
        name = description = domain = ""
        version = "1.0.0"
        body = content

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                body = parts[2].strip()
                for line in frontmatter.strip().splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        k, v = k.strip(), v.strip()
                        if k == "name": name = v
                        elif k == "description": description = v
                        elif k == "domain": domain = v
                        elif k == "version": version = v
        return name, description, domain, version, body

    @staticmethod
    def validate_structure(skill_dir: Path) -> list[str]:
        """Check skill folder structure. Returns list of issues."""
        issues = []
        if not skill_dir.exists():
            return [f"Skill dir does not exist: {skill_dir}"]
        if not (skill_dir / "SKILL.md").exists():
            issues.append("Missing SKILL.md")
        tests_dir = skill_dir / "tests"
        if not tests_dir.exists():
            issues.append("Missing tests/ directory (validation gap)")
        scripts_dir = skill_dir / "scripts"
        if (skill_dir / "scripts").exists():
            py_files = list(scripts_dir.glob("*.py"))
            if not py_files:
                issues.append("scripts/ exists but has no .py files")
        return issues
