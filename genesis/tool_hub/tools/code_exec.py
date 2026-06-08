"""
GENESIS Tool Hub — Code Execution Tool
========================================
Component: TOOL_HUB.tools.code_exec
Source: MUSE-Autoskill (arXiv:2605.27366) — sandbox_run concept

Stolen:
  - Isolated code execution per invocation
  - Results captured from stdout/stderr
  - Timeout enforcement

Genesis Adaptation:
  - Uses SandboxExecutor (tmpdir subprocess, not Docker)
  - Args passed via JSON env var GENESIS_SANDBOX_ARGS
  - Safety: max_output truncated, timeout enforced

Genesis Role:
  - Skills with scripts/ need this to execute their Python code
  - SKILL_ENGINE evaluator uses this for pytest runs
  - target_agent.py can use this for dynamic code execution

Called by: genesis/tool_hub/__init__.py (auto-registration)
"""

from __future__ import annotations

from genesis.tool_hub.executor import SandboxExecutor, run_code_isolated
from genesis.tool_hub.registry import ToolSpec


def _execute_run_code(args: dict) -> dict:
    """
    Execute Python code string in isolation.
    Args: {code: str, timeout_sec: int = 30}
    Returns: {stdout: str, stderr: str, exit_code: int, success: bool}
    """
    code = args.get("code", "")
    timeout = args.get("timeout_sec", 30)
    code_args = args.get("args", {})

    if not code.strip():
        return {"error": "code is required", "success": False}

    result = run_code_isolated(code, args=code_args, timeout_sec=timeout)
    return {
        "success": result.success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.exit_code,
        "execution_time_ms": result.execution_time_ms,
    }


def _execute_run_script(args: dict) -> dict:
    """
    Execute a script file in sandbox.
    Args: {script_path: str, timeout_sec: int = 30}
    Returns: {stdout, stderr, exit_code, success}
    """
    script_path = args.get("script_path", "")
    timeout = args.get("timeout_sec", 30)

    if not script_path:
        return {"error": "script_path is required", "success": False}

    sb = SandboxExecutor(timeout_sec=timeout)
    sid = sb.create()
    try:
        sb.upload_file(sid, script_path)
        import os
        result = sb.run(sid, os.path.basename(script_path))
        return {
            "success": result.success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
        }
    finally:
        sb.close(sid)


CODE_EXEC_TOOL = ToolSpec(
    name="code_exec",
    description="Execute Python code in isolated subprocess sandbox",
    version="1.0.0",
    input_schema={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python code to execute"},
            "timeout_sec": {"type": "integer", "default": 30, "maximum": 120},
            "args": {"type": "object", "description": "Args passed to code as JSON"},
        },
        "required": ["code"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "stdout": {"type": "string"},
            "stderr": {"type": "string"},
            "exit_code": {"type": "integer"},
        },
    },
    preconditions=["Python interpreter available"],
    failure_modes=["Timeout", "Import errors", "Runtime exceptions"],
    cost_per_call_usd=0.0,
    requires_sandbox=True,
    executor=_execute_run_code,
    source_project="MUSE-Autoskill (arXiv:2605.27366) sandbox concept",
    genesis_role="Execute skill scripts and dynamic code safely",
)

ALL_TOOLS = [CODE_EXEC_TOOL]
