"""
GENESIS Skill Engine — Skill Library
======================================
Component: SKILL_ENGINE.library
Source: Multiple papers 2026

STOLEN_FROM:
  MUSE-Autoskill (arXiv:2605.27366):
    - Skill Bank: register, retrieve, maintain
    - Catalog injection (progressive disclosure)
    - Refinement + merging + pruning

  EvoSkill (arXiv:2603.02766):
    - Frontier management: top-K best skills
    - Evict weakest when frontier full
    - frontier_k = 3 default

  SkillOps (arXiv:2605.13716):
    - Health dimensions: utility, redundancy, compatibility, failure-risk, validation-gap
    - Maintenance actions: merge, repair, retire, add_validator
    - O(N) maintenance pass (nearly zero LLM calls)

GENESIS_ADAPTATION:
  - Skills stored as filesystem folders (genesis/skill_engine/skills/)
  - SQLite registry for metadata + stats (not git branches like EvoSkill)
  - catalog.yaml auto-generated from registry
  - frontier management via performance_score (not EM score like EvoSkill)

CALLED_BY:
  - genesis/skill_engine/__init__.py (singleton)
  - genesis/orchestrator.py Section 3 (catalog) + 5a.1 (register) + 5b (retrieve)
  - genesis/skill_engine/evolver.py (frontier management)

ARTIFACT_OUT:
  - genesis/skill_engine/skills/catalog.yaml (auto-generated)
  - genesis/skill_engine/skills/{name}/ (per skill)
  - skill_registry.db (SQLite, gitignored)
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from genesis.skill_engine.skill import Skill, SkillContract, SkillFolder

logger = logging.getLogger(__name__)

DEFAULT_FRONTIER_K = 3
DEFAULT_SKILLS_DIR = Path(__file__).parent / "skills"
DEFAULT_DB_PATH = DEFAULT_SKILLS_DIR / "skill_registry.db"


# ─── Health Report (SkillOps) ─────────────────────────────────────────────────

@dataclass
class HealthReport:
    """SkillOps: library health across 5 dimensions."""
    total_skills: int = 0
    validation_gaps: list[str] = field(default_factory=list)   # V = ∅
    redundant_pairs: list[tuple[str, str]] = field(default_factory=list)
    low_utility: list[str] = field(default_factory=list)        # usage_count = 0
    high_failure_risk: list[str] = field(default_factory=list)  # failure_rate > 0.5
    maintenance_actions_taken: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def is_healthy(self) -> bool:
        return (
            len(self.validation_gaps) == 0
            and len(self.redundant_pairs) == 0
        )

    def to_dict(self) -> dict:
        return {
            "total_skills": self.total_skills,
            "validation_gaps": self.validation_gaps,
            "redundant_pairs": [list(p) for p in self.redundant_pairs],
            "low_utility": self.low_utility,
            "high_failure_risk": self.high_failure_risk,
            "maintenance_actions_taken": self.maintenance_actions_taken,
            "is_healthy": self.is_healthy,
            "timestamp": self.timestamp,
        }


# ─── SkillLibrary ─────────────────────────────────────────────────────────────

class SkillLibrary:
    """
    The Skill Bank — filesystem + SQLite.

    MUSE pattern: register → retrieve → maintain lifecycle
    EvoSkill pattern: frontier management (top-K)
    SkillOps pattern: health diagnosis + typed maintenance actions
    """

    def __init__(
        self,
        skills_dir: Path = DEFAULT_SKILLS_DIR,
        db_path: Path = DEFAULT_DB_PATH,
        frontier_k: int = DEFAULT_FRONTIER_K,
    ):
        self.skills_dir = Path(skills_dir)
        self.db_path = Path(db_path)
        self.frontier_k = frontier_k
        self._frontier: list[Skill] = []

        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._load_frontier()

    # ── DB Init ───────────────────────────────────────────────────────────────

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    name TEXT PRIMARY KEY,
                    version TEXT,
                    domain TEXT,
                    task_types TEXT,
                    description TEXT,
                    performance_score REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    body_hash TEXT,
                    created_at TEXT,
                    last_used_at TEXT,
                    source_run TEXT,
                    source_gen INTEGER,
                    generation INTEGER DEFAULT 0,
                    parent_skill TEXT,
                    frontier_rank INTEGER,
                    skill_dir TEXT,
                    metadata_json TEXT
                )
            """)
            conn.commit()

    # ── Core CRUD ─────────────────────────────────────────────────────────────

    def register(self, skill: Skill, overwrite: bool = False) -> bool:
        """
        MUSE create→evaluate→register: only register evaluated skills.
        Returns True if registered, False if already exists (use overwrite=True to update).
        """
        existing = self.get(skill.name)
        if existing and not overwrite:
            logger.info(f"Skill '{skill.name}' already exists. Use overwrite=True to update.")
            return False

        # Ensure skill folder exists
        if skill.skill_dir is None or not skill.skill_dir.exists():
            skill.skill_dir = self.skills_dir / skill.name
            SkillFolder.create(self.skills_dir, skill)

        self._save_to_db(skill)
        self._rebuild_catalog()
        logger.info(f"Skill registered: {skill.name} (score={skill.performance_score:.1f})")
        return True

    def get(self, name: str) -> Skill | None:
        """Get skill by name. Returns None if not found."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM skills WHERE name = ?", (name,)
            ).fetchone()
            if row is None:
                return None
            return self._row_to_skill(row)

    def update(self, skill: Skill) -> None:
        """MUSE update_skill: update existing skill's metadata and files."""
        if not self.get(skill.name):
            logger.warning(f"Skill '{skill.name}' not found. Use register() instead.")
            return
        self._save_to_db(skill)
        self._rebuild_catalog()
        logger.info(f"Skill updated: {skill.name}")

    def retire(self, name: str) -> bool:
        """
        SkillOps retire action: remove skill + edges + catalog entry.
        Returns True if retired, False if not found.
        """
        skill = self.get(name)
        if not skill:
            return False

        # Remove from filesystem
        if skill.skill_dir and skill.skill_dir.exists():
            shutil.rmtree(skill.skill_dir, ignore_errors=True)

        # Remove from DB
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM skills WHERE name = ?", (name,))
            conn.commit()

        # Remove from frontier
        self._frontier = [s for s in self._frontier if s.name != name]
        self._rebuild_catalog()
        logger.info(f"Skill retired: {name}")
        return True

    def list_all(self) -> list[Skill]:
        """Get all registered skills."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM skills ORDER BY performance_score DESC").fetchall()
            return [self._row_to_skill(r) for r in rows]

    def count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]

    # ── Frontier Management (EvoSkill) ────────────────────────────────────────

    def add_to_frontier(self, skill: Skill) -> bool:
        """
        EvoSkill frontier: add skill if better than weakest OR frontier not full.
        Returns True if added to frontier.
        """
        if len(self._frontier) < self.frontier_k:
            self._frontier.append(skill)
            self._sort_frontier()
            self._update_frontier_ranks()
            return True

        weakest = min(self._frontier, key=lambda s: s.performance_score)
        if skill.performance_score > weakest.performance_score:
            self._frontier.remove(weakest)
            weakest.frontier_rank = None
            self.update(weakest)
            self._frontier.append(skill)
            self._sort_frontier()
            self._update_frontier_ranks()
            return True
        return False

    def get_frontier(self) -> list[Skill]:
        """EvoSkill: get top-K best skills."""
        return list(self._frontier)

    def _sort_frontier(self) -> None:
        self._frontier.sort(key=lambda s: s.performance_score, reverse=True)

    def _update_frontier_ranks(self) -> None:
        for i, s in enumerate(self._frontier):
            s.frontier_rank = i + 1
            self._save_to_db(s)

    def _load_frontier(self) -> None:
        """Load frontier from DB on startup."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM skills WHERE frontier_rank IS NOT NULL ORDER BY frontier_rank"
            ).fetchall()
            self._frontier = [self._row_to_skill(r) for r in rows[:self.frontier_k]]

    # ── Maintenance (SkillOps) ────────────────────────────────────────────────

    def merge(self, skill_a: Skill, skill_b: Skill) -> Skill:
        """
        SkillOps merge action: collapse redundant pair.
        Keeps higher-performing skill, updates description.
        """
        winner = skill_a if skill_a.performance_score >= skill_b.performance_score else skill_b
        loser = skill_b if winner.name == skill_a.name else skill_a

        # Update winner description to mention both
        winner.description = f"{winner.description} (merged with {loser.name})"
        winner.usage_count += loser.usage_count
        winner.success_count += loser.success_count

        self.update(winner)
        self.retire(loser.name)
        logger.info(f"Skills merged: {loser.name} → {winner.name}")
        return winner

    def health_check(self) -> HealthReport:
        """
        SkillOps health diagnosis: O(N), nearly zero LLM calls.
        Checks: utility, redundancy, failure-risk, validation-gap.
        """
        skills = self.list_all()
        report = HealthReport(total_skills=len(skills))

        # Validation gaps (V = ∅)
        report.validation_gaps = [
            s.name for s in skills if s.contract.has_validation_gap
        ]

        # Redundancy (same body_hash)
        hash_to_skills: dict[str, list[str]] = {}
        for s in skills:
            h = s.body_hash
            if h not in hash_to_skills:
                hash_to_skills[h] = []
            hash_to_skills[h].append(s.name)
        for names in hash_to_skills.values():
            if len(names) > 1:
                for i in range(len(names)):
                    for j in range(i + 1, len(names)):
                        report.redundant_pairs.append((names[i], names[j]))

        # Low utility (never used)
        report.low_utility = [s.name for s in skills if s.usage_count == 0 and s.source_gen > 0]

        # High failure risk
        report.high_failure_risk = [
            s.name for s in skills
            if (s.success_count + s.failure_count) > 3 and s.success_rate < 0.5
        ]

        return report

    def run_maintenance(self) -> int:
        """
        SkillOps O(N) maintenance pass.
        Applies: merge redundant, retire high-failure.
        Returns number of actions taken.
        """
        report = self.health_check()
        actions = 0

        # Merge redundant pairs
        merged = set()
        for name_a, name_b in report.redundant_pairs:
            if name_a in merged or name_b in merged:
                continue
            skill_a = self.get(name_a)
            skill_b = self.get(name_b)
            if skill_a and skill_b:
                self.merge(skill_a, skill_b)
                merged.add(name_b)
                actions += 1

        # Retire consistently failing skills
        for name in report.high_failure_risk:
            skill = self.get(name)
            if skill and skill.usage_count >= 5:  # only retire if enough data
                self.retire(name)
                actions += 1

        logger.info(f"Maintenance complete: {actions} actions taken")
        return actions

    # ── Catalog (Progressive Disclosure) ─────────────────────────────────────

    def get_catalog_yaml(self) -> str:
        """
        MUSE progressive disclosure: catalog = name + description only.
        This string goes into META_AGENT_PROMPT.
        """
        catalog_file = self.skills_dir / "catalog.yaml"
        if catalog_file.exists():
            return catalog_file.read_text(encoding="utf-8")
        return self._rebuild_catalog()

    def _rebuild_catalog(self) -> str:
        """Rebuild catalog.yaml from current skills."""
        skills = self.list_all()
        entries = []
        for s in skills:
            entries.append({
                "name": s.name,
                "description": s.description,
                "domain": s.domain,
                "score": round(s.performance_score, 1),
                "used": s.usage_count,
            })
        catalog = yaml.dump(
            {"skills": entries, "count": len(entries)},
            allow_unicode=True, default_flow_style=False
        )
        catalog_file = self.skills_dir / "catalog.yaml"
        catalog_file.write_text(catalog, encoding="utf-8")
        return catalog

    def get_catalog_prompt(self) -> str:
        """Format catalog as plain text for META_AGENT_PROMPT injection."""
        skills = self.list_all()
        if not skills:
            return "AVAILABLE SKILLS: none registered yet."
        lines = [f"AVAILABLE SKILLS ({len(skills)} registered):"]
        for s in skills:
            lines.append(s.get_catalog_entry())
        lines.append("(Use skill_use tool to execute a skill by name)")
        return "\n".join(lines)

    # ── Stats ─────────────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        return {
            "total_skills": self.count(),
            "frontier_size": len(self._frontier),
            "frontier_skills": [s.name for s in self._frontier],
            "skills_dir": str(self.skills_dir),
        }

    # ── DB Helpers ────────────────────────────────────────────────────────────

    def _save_to_db(self, skill: Skill) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO skills
                (name, version, domain, task_types, description,
                 performance_score, usage_count, success_count, failure_count,
                 body_hash, created_at, last_used_at, source_run, source_gen,
                 generation, parent_skill, frontier_rank, skill_dir, metadata_json)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                skill.name, skill.version, skill.domain,
                json.dumps(skill.task_types), skill.description,
                skill.performance_score, skill.usage_count,
                skill.success_count, skill.failure_count,
                skill.body_hash, skill.created_at, skill.last_used_at,
                skill.source_run, skill.source_gen,
                skill.generation, skill.parent_skill,
                skill.frontier_rank,
                str(skill.skill_dir) if skill.skill_dir else None,
                json.dumps({
                    "when_to_use": skill.when_to_use,
                    "core_principles": skill.core_principles,
                    "recommended_tools": skill.recommended_tools,
                    "workflow": skill.workflow,
                    "contract": skill.contract.to_dict(),
                }),
            ))
            conn.commit()

    def _row_to_skill(self, row: tuple) -> Skill:
        cols = [
            "name", "version", "domain", "task_types", "description",
            "performance_score", "usage_count", "success_count", "failure_count",
            "body_hash", "created_at", "last_used_at", "source_run", "source_gen",
            "generation", "parent_skill", "frontier_rank", "skill_dir", "metadata_json"
        ]
        data = dict(zip(cols, row))
        meta = json.loads(data.get("metadata_json") or "{}")
        contract_data = meta.pop("contract", {})

        skill = Skill(
            name=data["name"],
            version=data.get("version", "1.0.0"),
            domain=data.get("domain", "general"),
            task_types=json.loads(data.get("task_types") or "[]"),
            description=data.get("description", ""),
            performance_score=float(data.get("performance_score") or 0),
            usage_count=int(data.get("usage_count") or 0),
            success_count=int(data.get("success_count") or 0),
            failure_count=int(data.get("failure_count") or 0),
            created_at=data.get("created_at", ""),
            last_used_at=data.get("last_used_at") or "",
            source_run=data.get("source_run") or "",
            source_gen=int(data.get("source_gen") or 0),
            generation=int(data.get("generation") or 0),
            parent_skill=data.get("parent_skill"),
            frontier_rank=data.get("frontier_rank"),
            skill_dir=Path(data["skill_dir"]) if data.get("skill_dir") else None,
            **meta,
        )
        if contract_data:
            skill.contract = SkillContract.from_dict(contract_data)
        return skill
