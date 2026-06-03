#!/usr/bin/env python3
"""
Evaluate target_agent.py for Virtual-GENESIS Cognitive-LLM Integration (Phase 1).

Checks:
1. Uses run_minimal_pipeline() from Virtual-GENESIS
2. Calls an LLM (not template-based reasoning)
3. Stores negative memories on failure
4. Passes all 424 existing tests
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path


def check_file_exists(gen_dir: str, filename: str) -> dict:
    """Check if a file exists and return its content."""
    filepath = os.path.join(gen_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return {"exists": True, "content": content, "path": filepath}
    return {"exists": False, "content": "", "path": filepath}


def check_cognitive_integration(content: str) -> dict:
    """Check if target_agent.py uses Virtual-GENESIS's cognitive pipeline."""
    checks = {
        "imports_run_minimal_pipeline": "from virtual_genesis.runtime.pipeline.minimal_run import run_minimal_pipeline" in content,
        "calls_run_minimal_pipeline": "run_minimal_pipeline(" in content,
        "imports_memory_store": "InMemoryMemoryStore" in content,
        "imports_concept_registry": "InMemoryConceptRegistry" in content,
        "imports_theory_registry": "InMemoryTheoryRegistry" in content,
        "uses_memory_pack": "memory_pack" in content,
        "uses_concept_items": "concept_items" in content,
        "uses_tier_decision": "tier_decision" in content,
    }
    return checks


def check_llm_integration(content: str) -> dict:
    """Check if target_agent.py calls an LLM (not template-based)."""
    checks = {
        "imports_openai": "import openai" in content or "from openai" in content,
        "creates_client": "AsyncOpenAI" in content or "OpenAI" in content,
        "calls_chat_completion": "chat.completions.create" in content or "chat.completions.create" in content,
        "has_cognitive_context": "cognitive" in content.lower() or "hint" in content.lower() or "context" in content.lower(),
        "no_template_reasoning": "_render_comparison" not in content and "_render_synthesis" not in content,
    }
    return checks


def check_memory_formation(content: str) -> dict:
    """Check if target_agent.py stores memories (especially negative ones)."""
    checks = {
        "stores_memory": "store_memory" in content or "store.store" in content,
        "creates_memory_unit": "MemoryUnit" in content or "memory_unit" in content.lower(),
        "handles_failure": "failure" in content.lower() or "negative" in content.lower() or "good_enough" in content.lower(),
    }
    return checks


def run_existing_tests() -> dict:
    """Run the 424 existing tests to ensure zero regressions."""
    try:
        # evaluate.py is at genesis/tasks/genesis_cognitive_integration/data/public/
        # Go up 6 levels to reach project root
        from pathlib import Path
        project_root = str(Path(__file__).resolve().parent.parent.parent.parent.parent.parent)
        
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=project_root,
        )
        return {
            "passed": result.returncode == 0,
            "output": result.stdout[-500:] if result.stdout else "",
            "errors": result.stderr[-500:] if result.stderr else "",
        }
    except Exception as e:
        return {"passed": False, "output": "", "errors": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Evaluate Phase 1 cognitive-LLM integration")
    parser.add_argument("--gen-dir", required=True, help="Path to generation directory")
    args = parser.parse_args()

    gen_dir = args.gen_dir
    results = {}

    # Check if target_agent.py exists
    target_agent = check_file_exists(gen_dir, "target_agent.py")
    if not target_agent["exists"]:
        print("ERROR: target_agent.py not found")
        sys.exit(1)

    content = target_agent["content"]

    # Run all checks
    results["cognitive_integration"] = check_cognitive_integration(content)
    results["llm_integration"] = check_llm_integration(content)
    results["memory_formation"] = check_memory_formation(content)

    # Calculate scores
    cognitive_score = sum(results["cognitive_integration"].values()) / len(results["cognitive_integration"])
    llm_score = sum(results["llm_integration"].values()) / len(results["llm_integration"])
    memory_score = sum(results["memory_formation"].values()) / len(results["memory_formation"])

    # Run existing tests
    print("Running existing tests (424 tests)...")
    test_results = run_existing_tests()
    results["test_results"] = test_results

    # Calculate overall score
    overall_score = (cognitive_score + llm_score + memory_score) / 3
    if not test_results["passed"]:
        overall_score *= 0.5  # Penalty for test failures

    # Print results
    print("\n" + "=" * 60)
    print("PHASE 1 EVALUATION RESULTS")
    print("=" * 60)

    print(f"\n📊 Cognitive Integration: {cognitive_score:.1%}")
    for check, passed in results["cognitive_integration"].items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")

    print(f"\n📊 LLM Integration: {llm_score:.1%}")
    for check, passed in results["llm_integration"].items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")

    print(f"\n📊 Memory Formation: {memory_score:.1%}")
    for check, passed in results["memory_formation"].items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")

    print(f"\n📊 Test Results: {'✅ PASSED' if test_results['passed'] else '❌ FAILED'}")
    if test_results["output"]:
        print(f"  Last lines: {test_results['output'][-200:]}")

    print(f"\n{'=' * 60}")
    print(f"🏆 OVERALL SCORE: {overall_score:.1%}")
    print(f"{'=' * 60}")

    # Save results
    results_path = os.path.join(gen_dir, "evaluation_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump({
            "cognitive_score": cognitive_score,
            "llm_score": llm_score,
            "memory_score": memory_score,
            "test_passed": test_results["passed"],
            "overall_score": overall_score,
            "checks": results,
        }, f, indent=2)

    print(f"\n📁 Results saved to: {results_path}")

    # Return exit code based on score
    if overall_score >= 0.7:
        print("\n✅ PHASE 1 EVALUATION PASSED")
        sys.exit(0)
    else:
        print("\n❌ PHASE 1 EVALUATION FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
