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

def main():
    parser = argparse.ArgumentParser(description="Run GENESIS benchmark on OpenRouter with gpt-oss-120b:free + evo")
    parser.add_argument("--task", type=str, default="spaceship-titanic", help="Bundled task (options: spaceship-titanic, gpqa, lawbench, longcot-chess)")
    parser.add_argument("--max_gen", type=int, default=3)
    parser.add_argument("--run_id", type=int, default=1)
    parser.add_argument("--use_evolutionary_discovery", action="store_true", help="Enable AlphaEvolve engine")
    args = parser.parse_args()

    # Force OpenRouter + free model
    os.environ.setdefault("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY to your OpenRouter key")
        sys.exit(1)

    cmd = [
        sys.executable, "-m", "genesis.orchestrator",
        "--task", args.task,
        "--max_gen", str(args.max_gen),
        "--run_id", str(args.run_id),
        "--backend", "openai",
        "--meta_model", "openai/gpt-oss-120b:free",
        "--task_model", "openai/gpt-oss-120b:free",
    ]
    if args.use_evolutionary_discovery:
        cmd.append("--use_evolutionary_discovery")

    print("Running GENESIS benchmark on OpenRouter...")
    print("Command:", " ".join(cmd))
    print("Model: openai/gpt-oss-120b:free (free tier)")
    print("This will exercise the new Evolutionary Discovery Engine (Task 6).")

    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        print("\n✅ Run completed successfully!")
        print("Check runs/run_{}/ for results, evolutionary_discovery.json, evolved_target_agent.py".format(args.run_id))
        print("Compare to baseline 98.6% to see impact of legitimate thefts (AlphaEvolve + prior).")
    else:
        print("\n❌ Run failed with code", result.returncode)

if __name__ == "__main__":
    main()