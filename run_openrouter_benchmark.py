"""
OpenRouter Benchmark Runner for GENESIS with Evolutionary Discovery.

Usage (after setting env):
export OPENAI_API_KEY="sk-or-your-openrouter-key"
export OPENAI_BASE_URL="https://openrouter.ai/api/v1"

python run_openrouter_benchmark.py --task gpqa --max_gen 2 --use_evolutionary_discovery
# or spaceship-titanic for faster test

This will run the orchestrator with gpt-oss-120b:free for meta and task,
trigger the AlphaEvolve evolutionary engine if flag set,
and capture results for comparison against baseline (98.6% keyword matching).

Recommended benchmarks to test the impact of the thefts (especially AlphaEvolve evolutionary discovery + prior ones like GRASP, ExpGraph):
- spaceship-titanic: Quick tabular classification (Kaggle-style). Good baseline for agent code quality. Fast to iterate.
- gpqa: Graduate-level Google-Proof Q&A (science reasoning). Excellent for testing genuine reasoning vs keyword matching/shortcuts. Hard benchmark, perfect to measure lift from evolutionary self-improvement.
- lawbench or longcot-chess: For domain-specific long reasoning.

Run the same task with and without --use_evolutionary_discovery to isolate the effect.

See STRATEGIC_DEVELOPMENT_PLAN_2026_06.md Task 9 for real run plan.

After run, check runs/run_*/ for:
- evolutionary_discovery.json (new evo metrics: population, best fitness, lineage)
- evolved_target_agent.py (best variant applied)
- results.json, constitutional_report.json, context.md
- Compare success rates, discovery, etc. to original 98.6% on v3b_curriculum.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Recommended free/cheap models on OpenRouter (general, not GENESIS-specific)
# يمكن إضافة/إزالة أي نموذج يدعم OpenAI-compatible API
RECOMMENDED_MODELS = {
    # OpenAI's open weights — strong on GPQA (80.1% high), 131K context
    "gpt-oss-120b-free":      "openai/gpt-oss-120b:free",
    "gpt-oss-120b":           "openai/gpt-oss-120b",
    # NVIDIA Nemotron 3 (released Jun 4, 2026) — strong on agent orchestration (91% PinchBench, 82% IFBench), 1M context
    "nemotron-3-ultra-free":  "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nemotron-3-ultra":       "nvidia/nemotron-3-ultra-550b-a55b",
    "nemotron-3-super-free":  "nvidia/nemotron-3-super-120b-a12b:free",
    "nemotron-3-nano-free":   "nvidia/nemotron-3-nano-30b-a3b:free",
    # Others (for comparison only)
    "deepseek-v4-flash-free": "deepseek/deepseek-v4-flash:free",
}


def main():
    parser = argparse.ArgumentParser(description="Run GENESIS benchmark on OpenRouter + AlphaEvolve")
    parser.add_argument("--task", type=str, default="spaceship-titanic",
                        help="Bundled task (spaceship-titanic, gpqa, lawbench, longcot-chess) or 'swe_bench'. Ignored if --task_dir is provided.")
    parser.add_argument("--task_dir", type=str, default=None,
                        help="External task directory (recommended for quick subsets like tasks/gpqa_subset_20)")
    parser.add_argument("--max_gen", type=int, default=3)
    parser.add_argument("--run_id", type=int, default=1)
    parser.add_argument("--use_evolutionary_discovery", action="store_true",
                        help="Enable AlphaEvolve evolutionary engine")
    # NEW: explicit model selection (defaults preserve old behavior)
    parser.add_argument("--meta_model", type=str, default="openai/gpt-oss-120b:free",
                        help=f"Meta-agent model id. Shortcuts: {list(RECOMMENDED_MODELS.keys())}")
    parser.add_argument("--task_model", type=str, default="openai/gpt-oss-120b:free",
                        help="Target/task-agent model id. Same shortcuts as --meta_model.")
    parser.add_argument("--list_models", action="store_true",
                        help="Print recommended OpenRouter model shortcuts and exit")
    args = parser.parse_args()

    if args.list_models:
        print("Recommended OpenRouter model shortcuts (use full id or shortcut):")
        for k, v in RECOMMENDED_MODELS.items():
            print(f"  {k:30s} -> {v}")
        print("\nExample:")
        print('  python run_openrouter_benchmark.py --task gpqa --meta_model nemotron-3-ultra-free \\')
        print('      --task_model nemotron-3-ultra-free --use_evolutionary_discovery')
        sys.exit(0)

    # Resolve shortcuts -> full ids
    meta_model = RECOMMENDED_MODELS.get(args.meta_model, args.meta_model)
    task_model = RECOMMENDED_MODELS.get(args.task_model, args.task_model)

    # Force OpenRouter base url
    os.environ.setdefault("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY to your OpenRouter key (sk-or-...)")
        sys.exit(1)

    repo_root = Path(__file__).resolve().parent
    preferred_python = repo_root / ".venv" / "bin" / "python"
    python_exec = str(preferred_python) if preferred_python.exists() else sys.executable

    cmd = [
        python_exec, "-m", "genesis.orchestrator",
        "--max_gen", str(args.max_gen),
        "--run_id", str(args.run_id),
        "--backend", "openai",
        "--meta_model", meta_model,
        "--task_model", task_model,
    ]
    if args.task_dir:
        cmd += ["--task_dir", args.task_dir]
    else:
        cmd += ["--task", args.task]
    if args.use_evolutionary_discovery:
        cmd.append("--use_evolutionary_discovery")

    if (not args.task_dir) and args.task == "swe_bench":
        print("\n=== SERIOUS BENCHMARK MODE: SWE-bench (for paper/project level) ===")
        print("SWE-bench is the standard for agentic software engineering: real GitHub issues, edit code to fix bugs and pass tests.")
        print("To run properly:")
        print("1. Set up a SWE-bench task_dir (see https://github.com/princeton-nlp/SWE-bench for data).")
        print("2. Use --task_dir pointing to a SWE-bench formatted task (or use the real_llm_eval for patches).")
        print("3. The evolutionary engine will evolve better target_agent.py that uses GENESIS pipeline for reasoning on the issue.")
        print("4. Then evaluate the generated patches on SWE-bench harness.")
        print("Example command for external task:")
        print("python -m genesis.orchestrator --task_dir /path/to/swe_bench_task --backend openai --meta_model openai/gpt-oss-120b:free --task_model openai/gpt-oss-120b:free --use_evolutionary_discovery")
        print("This is for real paper-level evaluation (see Task 9).")
        sys.exit(0)  # For now, print instructions; full integration would load SWE-bench tasks

    print("Running GENESIS benchmark on OpenRouter...")
    print("Command:", " ".join(cmd))
    print(f"Python executable: {python_exec}")
    print(f"Task source: {args.task_dir if args.task_dir else args.task}")
    print(f"Meta model: {meta_model}")
    print(f"Task model: {task_model}")
    if args.use_evolutionary_discovery:
        print("Evolutionary Discovery (AlphaEvolve): ENABLED")

    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        print("\n✅ Run completed successfully!")
        print("Check runs/run_{}/ for results, evolutionary_discovery.json, evolved_target_agent.py".format(args.run_id))
        print("Compare to baseline 98.6% to see impact of legitimate thefts (AlphaEvolve + prior).")
    else:
        print("\n❌ Run failed with code", result.returncode)

if __name__ == "__main__":
    main()