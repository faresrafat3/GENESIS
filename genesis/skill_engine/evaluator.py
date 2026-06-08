"""
GENESIS Skill Engine — Skill Evaluator
========================================
Component: SKILL_ENGINE.evaluator
Source: MUSE-Autoskill (arXiv:2605.27366)

STOLEN_FROM:
  MUSE-Autoskill:
    - create→evaluate→register loop
    - pytest-based skill validation
    - Only register if ALL tests pass
    - Failed tests → trigger refinement (update_skill)
    - SandboxExecutor isolation per skill test run

GENESIS_ADAPTATION:
  - Uses genesis/tool_hub SandboxExecutor (tmpdir, not Docker)
  - TestResult includes error_trace for ProposerAgent in EvoSkill
  - SkillContract validator check (SkillOps V dimension)
  - Timeout configurable (free tier constraint)

CALLED_BY:
  - genesis/skill_engine/__init__.py: register() calls evaluate() first
  - genesis/skill_engine/evolver.py: EvoSkillLoop validates candidates
  - genesis/skill_engine/extractor.py: validates extracted skills

CALLS:
  - genesis/tool_hub/executor.py: SandboxExecutor.run_pytest()
"""

from __future__ import annotations

import logging
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from genesis.tool_hub.executor import SandboxExecutor
from genesis.skill_engine.skill import Skill, SkillFolder

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


# ─── TestResult ───────────────────────────────────────────────────────────────

@dataclass
class TestResult:
    """
    Result from skill test execution.
    Stolen from: MUSE create→evaluate loop output.
    """
    passed: bool
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    failures: list[str] = field(default_factory=list)
    error_trace: str = ""              # for ProposerAgent diagnosis
    execution_time_ms: float = 0.0
    sandbox_stdout: str = ""
    sandbox_stderr: str = ""

    @property
    def pass_rate(self) -> float:
        return self.tests_passed / self.tests_run if self.tests_run > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "failures": self.failures,
            "error_trace": self.error_trace[:2000],
            "execution_time_ms": self.execution_time_ms,
            "pass_rate": self.pass_rate,
        }


# ─── SkillEvaluator ───────────────────────────────────────────────────────────

class SkillEvaluator:
    """
    Validates skills before registration.
    MUSE pattern: create → evaluate → register (only if tests pass).

    Uses SandboxExecutor (tmpdir subprocess) for isolation.
    """

    def __init__(self, timeout_sec: int = DEFAULT_TIMEOUT):
        self.timeout_sec = timeout_sec

    def run_tests(self, skill: Skill) -> TestResult:
        """
        Run pytest on skill's tests/ directory.
        MUSE: gates registration — only pass if tests pass.
        """
        if not skill.has_tests:
            # No tests = validation gap (SkillOps V = ∅)
            logger.warning(f"Skill '{skill.name}' has no tests — validation gap!")
            return TestResult(
                passed=True,  # allow through but mark gap
                error_trace="No tests directory — validation gap (SkillOps V = ∅)",
            )

        sb = SandboxExecutor(timeout_sec=self.timeout_sec)
        sandbox_id = sb.create()

        try:
            # Copy skill folder into sandbox
            if skill.skill_dir and skill.skill_dir.exists():
                sb.upload_dir(sandbox_id, str(skill.skill_dir), "skill")
            else:
                # Build from scratch
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmp_path = Path(tmpdir) / skill.name
                    SkillFolder.create(Path(tmpdir), skill)
                    sb.upload_dir(sandbox_id, str(tmp_path), "skill")

            # Run pytest
            result = sb.run_pytest(sandbox_id, test_dir="skill/tests")
            return self._parse_pytest_result(result)

        except Exception as e:
            logger.error(f"Test run failed for '{skill.name}': {e}")
            return TestResult(
                passed=False,
                error_trace=str(e),
            )
        finally:
            sb.close(sandbox_id)

    def _parse_pytest_result(self, sandbox_result) -> TestResult:
        """Parse pytest output into TestResult."""
        stdout = sandbox_result.stdout or ""
        stderr = sandbox_result.stderr or ""
        combined = stdout + stderr

        # Parse pytest summary line: "X passed, Y failed"
        import re
        passed_match = re.search(r'(\d+) passed', combined)
        failed_match = re.search(r'(\d+) failed', combined)
        error_match = re.search(r'(\d+) error', combined)

        n_passed = int(passed_match.group(1)) if passed_match else 0
        n_failed = int(failed_match.group(1)) if failed_match else 0
        n_errors = int(error_match.group(1)) if error_match else 0
        n_total = n_passed + n_failed + n_errors

        # Extract failure details
        failures = []
        fail_sections = re.findall(r'FAILED (.+)', combined)
        failures.extend(fail_sections[:10])

        passed = sandbox_result.success and n_failed == 0 and n_errors == 0

        return TestResult(
            passed=passed,
            tests_run=n_total,
            tests_passed=n_passed,
            tests_failed=n_failed + n_errors,
            failures=failures,
            error_trace=combined[:3000] if not passed else "",
            execution_time_ms=sandbox_result.execution_time_ms,
            sandbox_stdout=stdout[:1000],
            sandbox_stderr=stderr[:1000],
        )

    def validate_contract(self, skill: Skill, context: dict) -> tuple[bool, list[str]]:
        """
        SkillOps: check preconditions (P) before execution.
        Returns (can_execute, issues).
        """
        return skill.contract.check_preconditions(context)

    def validate_artifact(self, skill: Skill, artifact_path: str) -> tuple[bool, str]:
        """
        SkillOps: validate produced artifact (V validator).
        Returns (valid, message).
        """
        if skill.contract.has_validation_gap:
            return True, "No validator defined (validation gap)"

        import os
        if not os.path.exists(artifact_path):
            return False, f"Artifact not found: {artifact_path}"

        # Type-based validation
        artifact_type = skill.contract.artifact_type.lower()
        if "json" in artifact_type:
            try:
                import json
                with open(artifact_path) as f:
                    json.load(f)
                return True, "Valid JSON artifact"
            except Exception as e:
                return False, f"Invalid JSON: {e}"
        elif "yaml" in artifact_type:
            try:
                import yaml
                with open(artifact_path) as f:
                    yaml.safe_load(f)
                return True, "Valid YAML artifact"
            except Exception as e:
                return False, f"Invalid YAML: {e}"

        # Default: file exists is enough
        return True, f"Artifact exists: {artifact_path}"
