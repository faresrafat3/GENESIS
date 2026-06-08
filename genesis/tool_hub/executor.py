"""
GENESIS Tool Hub — Sandbox Executor
=====================================
Component: TOOL_HUB.executor
Source: MUSE-Autoskill (arXiv:2605.27366) — sandbox lifecycle tools concept

Stolen:
  - Sandbox isolation per skill/tool invocation
  - create → run → upload/download → close lifecycle
  - Code execution isolated from main process

Genesis Adaptation:
  - Uses tmpdir subprocess (NOT Docker — free tier constraint)
  - Each sandbox = isolated Python subprocess in tmpdir
  - Outputs captured from stdout/stderr
  - Timeout enforced (prevents runaway code)

Called by:
  - genesis/tool_hub/tools/code_exec.py (direct code execution)
  - genesis/skill_engine/evaluator.py (pytest runs for skill validation)
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SEC = 30
MAX_OUTPUT_CHARS = 10_000


@dataclass
class SandboxResult:
    """Result from sandbox execution."""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: float
    sandbox_dir: str | None = None  # None if auto-cleaned


class SandboxExecutor:
    """
    Isolated execution environment.
    Stolen from: MUSE sandbox lifecycle tools concept.
    Implemented as: tmpdir subprocess (not Docker).

    Usage:
        sb = SandboxExecutor()
        sandbox_id = sb.create()
        sb.upload(sandbox_id, "script.py", code_str)
        result = sb.run(sandbox_id, "script.py", args={})
        sb.close(sandbox_id)
    """

    def __init__(self, base_dir: str | None = None, timeout_sec: int = DEFAULT_TIMEOUT_SEC):
        self.base_dir = base_dir or tempfile.gettempdir()
        self.timeout_sec = timeout_sec
        self._sandboxes: dict[str, Path] = {}  # id → tmpdir path

    def create(self, sandbox_id: str | None = None) -> str:
        """Create isolated sandbox directory."""
        sandbox_id = sandbox_id or f"sandbox_{int(time.time() * 1000)}"
        sandbox_path = Path(self.base_dir) / f"genesis_{sandbox_id}"
        sandbox_path.mkdir(parents=True, exist_ok=True)
        self._sandboxes[sandbox_id] = sandbox_path
        logger.debug(f"Sandbox created: {sandbox_id} at {sandbox_path}")
        return sandbox_id

    def upload(self, sandbox_id: str, filename: str, content: str) -> Path:
        """Write file into sandbox."""
        sandbox_path = self._get_path(sandbox_id)
        file_path = sandbox_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def upload_file(self, sandbox_id: str, source_path: str, dest_name: str | None = None) -> Path:
        """Copy existing file into sandbox."""
        sandbox_path = self._get_path(sandbox_id)
        dest = sandbox_path / (dest_name or Path(source_path).name)
        shutil.copy2(source_path, dest)
        return dest

    def upload_dir(self, sandbox_id: str, source_dir: str, dest_subdir: str | None = None) -> Path:
        """Copy directory into sandbox."""
        sandbox_path = self._get_path(sandbox_id)
        dest = sandbox_path / (dest_subdir or Path(source_dir).name)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(source_dir, dest)
        return dest

    def run(
        self,
        sandbox_id: str,
        script_name: str,
        args: dict | None = None,
        env_extra: dict | None = None,
        python_exec: str | None = None,
    ) -> SandboxResult:
        """
        Run a Python script inside the sandbox.
        Script receives args as JSON via stdin or env vars.
        """
        sandbox_path = self._get_path(sandbox_id)
        script_path = sandbox_path / script_name
        if not script_path.exists():
            return SandboxResult(
                success=False, stdout="", stderr=f"Script not found: {script_name}",
                exit_code=-1, execution_time_ms=0,
            )

        # Build environment
        env = os.environ.copy()
        if env_extra:
            env.update(env_extra)

        # Args → JSON file in sandbox
        args_file = None
        if args:
            args_file = sandbox_path / "_args.json"
            import json
            args_file.write_text(json.dumps(args), encoding="utf-8")
            env["GENESIS_SANDBOX_ARGS"] = str(args_file)

        python = python_exec or sys.executable
        cmd = [python, str(script_path)]

        start = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=str(sandbox_path),
                env=env,
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
            )
            elapsed = (time.time() - start) * 1000

            stdout = result.stdout[:MAX_OUTPUT_CHARS]
            stderr = result.stderr[:MAX_OUTPUT_CHARS]

            return SandboxResult(
                success=result.returncode == 0,
                stdout=stdout,
                stderr=stderr,
                exit_code=result.returncode,
                execution_time_ms=elapsed,
                sandbox_dir=str(sandbox_path),
            )
        except subprocess.TimeoutExpired:
            elapsed = (time.time() - start) * 1000
            return SandboxResult(
                success=False,
                stdout="",
                stderr=f"Timeout after {self.timeout_sec}s",
                exit_code=-2,
                execution_time_ms=elapsed,
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return SandboxResult(
                success=False, stdout="", stderr=str(e),
                exit_code=-3, execution_time_ms=elapsed,
            )

    def run_pytest(self, sandbox_id: str, test_dir: str = "tests") -> SandboxResult:
        """
        Run pytest inside sandbox.
        Used by SKILL_ENGINE evaluator for skill testing.
        Stolen from: MUSE create→evaluate→register loop.
        """
        sandbox_path = self._get_path(sandbox_id)
        test_path = sandbox_path / test_dir

        if not test_path.exists():
            return SandboxResult(
                success=False, stdout="", stderr=f"Test dir not found: {test_dir}",
                exit_code=-1, execution_time_ms=0,
            )

        python = sys.executable
        cmd = [python, "-m", "pytest", str(test_path), "-q", "--tb=short", "--no-header"]

        start = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=str(sandbox_path),
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
            )
            elapsed = (time.time() - start) * 1000
            return SandboxResult(
                success=result.returncode == 0,
                stdout=result.stdout[:MAX_OUTPUT_CHARS],
                stderr=result.stderr[:MAX_OUTPUT_CHARS],
                exit_code=result.returncode,
                execution_time_ms=elapsed,
                sandbox_dir=str(sandbox_path),
            )
        except subprocess.TimeoutExpired:
            elapsed = (time.time() - start) * 1000
            return SandboxResult(
                success=False, stdout="", stderr=f"Pytest timeout after {self.timeout_sec}s",
                exit_code=-2, execution_time_ms=elapsed,
            )

    def download(self, sandbox_id: str, filename: str) -> str | None:
        """Read file content from sandbox."""
        sandbox_path = self._get_path(sandbox_id)
        file_path = sandbox_path / filename
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return None

    def close(self, sandbox_id: str, keep: bool = False) -> None:
        """Cleanup sandbox. Default: delete tmpdir."""
        if sandbox_id in self._sandboxes:
            path = self._sandboxes.pop(sandbox_id)
            if not keep and path.exists():
                shutil.rmtree(path, ignore_errors=True)
                logger.debug(f"Sandbox cleaned: {sandbox_id}")

    def _get_path(self, sandbox_id: str) -> Path:
        if sandbox_id not in self._sandboxes:
            raise KeyError(f"Sandbox '{sandbox_id}' not found. Call create() first.")
        return self._sandboxes[sandbox_id]

    def __enter__(self):
        self._auto_id = self.create()
        return self._auto_id, self

    def __exit__(self, *args):
        if hasattr(self, "_auto_id"):
            self.close(self._auto_id)


# ─── Convenience: run code string directly ────────────────────────────────────

def run_code_isolated(
    code: str,
    args: dict | None = None,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC,
) -> SandboxResult:
    """
    Run a Python code string in isolation.
    Convenience wrapper for one-shot execution.
    """
    sb = SandboxExecutor(timeout_sec=timeout_sec)
    sid = sb.create()
    try:
        sb.upload(sid, "script.py", code)
        return sb.run(sid, "script.py", args=args)
    finally:
        sb.close(sid)
