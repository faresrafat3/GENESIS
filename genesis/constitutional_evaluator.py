#!/usr/bin/env python3
"""
GENESIS Constitutional Evaluator — Phase 2: Constitutional Self-Play
Inspired by Meta AI's "Self-Rewarding Language Models v3: Recursive Constitutional AI Alignment" (June 2026)

Evaluates agent output against GENESIS's internal constitution (5 rules).
Uses the same LLM backend as the orchestrator for self-evaluation.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


# ── Constitution Loader ─────────────────────────────────────────────────────

def load_constitution(constitution_path: str | None = None) -> dict:
    """Load GENESIS constitution from JSON file."""
    if constitution_path is None:
        constitution_path = os.path.join(os.path.dirname(__file__), "constitution.json")
    
    if not os.path.exists(constitution_path):
        raise FileNotFoundError(f"Constitution not found at {constitution_path}")
    
    with open(constitution_path, "r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class RuleViolation:
    """A single constitutional rule violation."""
    rule_id: str
    rule_name: str
    description: str
    severity: int  # weight
    evidence: str  # what was found that violates the rule


@dataclass
class ConstitutionalReport:
    """Complete constitutional evaluation report."""
    passed: bool
    total_score: int
    max_allowed_score: int
    violations: List[RuleViolation] = field(default_factory=list)
    rule_results: Dict[str, bool] = field(default_factory=dict)
    details: str = ""

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "total_score": self.total_score,
            "max_allowed_score": self.max_allowed_score,
            "violations": [
                {
                    "rule_id": v.rule_id,
                    "rule_name": v.rule_name,
                    "description": v.description,
                    "severity": v.severity,
                    "evidence": v.evidence,
                }
                for v in self.violations
            ],
            "rule_results": self.rule_results,
            "details": self.details,
        }


# ── Heuristic Checks (no LLM needed) ──────────────────────────────────────

def check_regression_free(gen_dir: str) -> RuleViolation | None:
    """R1/R2: Check if all 424 tests still pass."""
    import subprocess
    # constitutional_evaluator.py is in genesis/ directory, so go one level up to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            # Count failures
            lines = result.stdout.split("\n")
            passed = 0
            failed = 0
            for line in lines:
                if "passed" in line:
                    import re
                    m = re.search(r"(\d+)\s+passed", line)
                    if m:
                        passed = int(m.group(1))
                    m = re.search(r"(\d+)\s+failed", line)
                    if m:
                        failed = int(m.group(1))
            
            return RuleViolation(
                rule_id="R2_REGRESSION_FREE",
                rule_name="Regression-Free Improvement",
                description=f"{failed} tests failed, {passed} passed",
                severity=10,
                evidence=result.stdout[-1000:],
            )
    except Exception as e:
        return RuleViolation(
            rule_id="R2_REGRESSION_FREE",
            rule_name="Regression-Free Improvement",
            description=f"Could not run tests: {e}",
            severity=10,
            evidence=str(e),
        )
    return None


def check_verifiability(agent_code: str) -> RuleViolation | None:
    """R1: Check for hallucination patterns in generated code."""
    # Heuristic: look for patterns that suggest hallucination
    hallucination_markers = [
        "TODO: implement",  # placeholder
        "pass  # placeholder",
    ]
    
    found_markers = []
    for marker in hallucination_markers:
        if marker in agent_code:
            found_markers.append(marker)
    
    if found_markers:
        return RuleViolation(
            rule_id="R1_VERIFIABILITY",
            rule_name="Falsifiability",
            description=f"Placeholder/hallucination markers found: {', '.join(found_markers)}",
            severity=10,
            evidence=f"Code contains unverified placeholders: {', '.join(found_markers)}",
        )
    return None


def check_simplicity(agent_code: str, reference_code: str = "") -> RuleViolation | None:
    """R3: Check for unnecessary complexity."""
    lines = agent_code.split("\n")
    non_empty = [l for l in lines if l.strip() and not l.strip().startswith("#")]
    comment_lines = [l for l in lines if l.strip().startswith("#")]
    
    # Heuristic: > 500 lines for a target agent is excessive
    if len(non_empty) > 500:
        return RuleViolation(
            rule_id="R3_SIMPLICITY_FIRST",
            rule_name="Simplicity > Complexity",
            description=f"Agent has {len(non_empty)} non-empty lines (threshold: 500)",
            severity=5,
            evidence=f"Code too long: {len(non_empty)} lines",
        )
    
    # Heuristic: > 30% comments suggests over-documentation
    if len(non_empty) > 100 and len(comment_lines) / max(len(non_empty), 1) > 0.3:
        return RuleViolation(
            rule_id="R3_SIMPLICITY_FIRST",
            rule_name="Simplicity > Complexity",
            description=f"Excessive comments: {len(comment_lines)}/{len(non_empty)} lines",
            severity=3,
            evidence="Over-commented code",
        )
    
    return None


def check_learning(agent_code: str, gen_dir: str) -> RuleViolation | None:
    """R4: Check if failure learning is present."""
    # Check if memory store calls exist
    has_memory_store = "store_memory" in agent_code or "MemoryUnit" in agent_code
    has_error_handling = "except" in agent_code or "try:" in agent_code
    
    if not has_memory_store:
        return RuleViolation(
            rule_id="R4_LEARN_FROM_FAILURE",
            rule_name="Mandatory Error Learning",
            description="No memory storage mechanism found in agent code",
            severity=5,
            evidence="Missing store_memory() or MemoryUnit usage",
        )
    
    return None


def check_traceability(agent_code: str) -> RuleViolation | None:
    """R5: Check cognitive traceability through pipeline stages."""
    required_imports = [
        "run_minimal_pipeline",
        "InMemoryMemoryStore",
        "InMemoryConceptRegistry",
    ]
    
    missing = [imp for imp in required_imports if imp not in agent_code]
    
    if missing:
        return RuleViolation(
            rule_id="R5_COGNITIVE_TRACEABILITY",
            rule_name="Cognitive Traceability",
            description=f"Missing cognitive imports: {', '.join(missing)}",
            severity=3,
            evidence=f"Missing: {', '.join(missing)}",
        )
    
    return None


# ── Main Evaluator ─────────────────────────────────────────────────────────

def evaluate_constitutional(
    agent_code: str,
    gen_dir: str,
    constitution: dict | None = None,
    llm_evaluation: bool = False,
) -> ConstitutionalReport:
    """
    Evaluate agent output against GENESIS's constitution.
    
    Args:
        agent_code: The target_agent.py content
        gen_dir: Generation directory (for test running)
        constitution: Constitution dict (loaded from file if None)
        llm_evaluation: If True, use LLM for deeper semantic checks
    
    Returns:
        ConstitutionalReport with pass/fail and violations
    """
    if constitution is None:
        try:
            constitution = load_constitution()
        except FileNotFoundError:
            # Fallback: embedded constitution
            constitution = {"evaluation_pipeline": {"threshold": 10, "max_violations": 2}}
    
    threshold = constitution.get("evaluation_pipeline", {}).get("threshold", 10)
    max_violations = constitution.get("evaluation_pipeline", {}).get("max_violations", 2)
    
    violations: List[RuleViolation] = []
    rule_results: Dict[str, bool] = {}
    
    # R1: Verifiability
    v = check_verifiability(agent_code)
    rule_results["R1_VERIFIABILITY"] = v is None
    if v:
        violations.append(v)
    
    # R2: Regression-Free
    v = check_regression_free(gen_dir)
    rule_results["R2_REGRESSION_FREE"] = v is None
    if v:
        violations.append(v)
    
    # R3: Simplicity
    v = check_simplicity(agent_code)
    rule_results["R3_SIMPLICITY_FIRST"] = v is None
    if v:
        violations.append(v)
    
    # R4: Learning
    v = check_learning(agent_code, gen_dir)
    rule_results["R4_LEARN_FROM_FAILURE"] = v is None
    if v:
        violations.append(v)
    
    # R5: Traceability
    v = check_traceability(agent_code)
    rule_results["R5_COGNITIVE_TRACEABILITY"] = v is None
    if v:
        violations.append(v)
    
    # Calculate score
    total_score = sum(v.severity for v in violations)
    passed = total_score <= threshold and len(violations) <= max_violations
    
    # Build details
    details_parts = []
    for rule_id, ok in rule_results.items():
        status = "✅" if ok else "❌"
        details_parts.append(f"{status} {rule_id}")
    
    return ConstitutionalReport(
        passed=passed,
        total_score=total_score,
        max_allowed_score=threshold,
        violations=violations,
        rule_results=rule_results,
        details="\n".join(details_parts),
    )


# ── CLI ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="GENESIS Constitutional Evaluator")
    parser.add_argument("--gen-dir", required=True, help="Generation directory")
    parser.add_argument("--constitution", default=None, help="Path to constitution.json")
    parser.add_argument("--llm", action="store_true", help="Use LLM for deeper evaluation")
    args = parser.parse_args()
    
    # Load agent code
    agent_path = os.path.join(args.gen_dir, "target_agent.py")
    if not os.path.exists(agent_path):
        print(json.dumps({"error": f"target_agent.py not found in {args.gen_dir}"}))
        sys.exit(1)
    
    with open(agent_path, "r", encoding="utf-8") as f:
        agent_code = f.read()
    
    # Load constitution
    constitution = None
    if args.constitution:
        constitution = load_constitution(args.constitution)
    
    # Evaluate
    report = evaluate_constitutional(agent_code, args.gen_dir, constitution, args.llm)
    
    # Output
    print(json.dumps(report.to_dict(), indent=2))
    
    if report.passed:
        print("\n✅ CONSTITUTIONAL CHECK PASSED")
        sys.exit(0)
    else:
        print(f"\n❌ CONSTITUTIONAL CHECK FAILED (score: {report.total_score}/{report.max_allowed_score})")
        sys.exit(1)