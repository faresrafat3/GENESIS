"""
Directory structure (conceptual)

orchestration/
  orchestrator.py

tasks/
  task_1/
    reference/
      reference_target_agent.py
      SAMPLE_TASK_DESCRIPTIONS.md
    data/
      public/
        train.csv
        test.csv
        task.md
      private/
  task_2/
    reference/
      reference_target_agent.py
      SAMPLE_TASK_DESCRIPTIONS.md
    data/
      public/
        task.md
      private/

tasks/_shared/                 # cross-task examples/templates (public)
  sample_agent_execution.json

runs/
  run_1/ (unique meta_agent, unique feedback_agent, unique_task, reference_target_agent, config)
    gen_1: (meta_agent, reference_target_agent) -> target_agent_1 -> gen_1
    gen_2: (feedback_agent, target_agent_1) -> target_agent_2 -> gen_2
    gen_3: (feedback_agent, target_agent_2) -> target_agent_3 -> gen_3
  run_2/ (unique meta_agent, unique feedback_agent, unique_task, reference_target_agent, config)
    gen_1: (meta_agent, reference_target_agent) -> target_agent_1 -> gen_1
    gen_2: (feedback_agent, target_agent_1) -> target_agent_2 -> gen_2
    gen_3: (feedback_agent, target_agent_2) -> target_agent_3 -> gen_3
  run_3/ (unique meta_agent, unique feedback_agent, unique_task, reference_target_agent, config)
    gen_1: (meta_agent, reference_target_agent) -> target_agent_1 -> gen_1
    gen_2: (feedback_agent, target_agent_1) -> target_agent_2 -> gen_2
    gen_3: (feedback_agent, target_agent_2) -> target_agent_3 -> gen_3
"""

import argparse
import asyncio
import glob
import json
import logging
import os
import shutil
import subprocess
import sys
import time
import traceback
import venv
from datetime import datetime
from importlib.resources import files as resource_files
from pathlib import Path

from genesis import __version__
from genesis.context_manager import ContextManager
from genesis.util import run_agent

# Tasks that ship inside the wheel via package-data (genesis.tasks/<name>/...).
BUNDLED_TASKS = ("gpqa", "lawbench", "longcot-chess", "spaceship-titanic")


def resolve_task_dir(task: str | None, task_dir: str | None) -> tuple[str, str]:
    """Resolve --task / --task_dir to a (task_dir, shared_dir) pair of real paths.

    - --task <name>  → bundled genesis.tasks/<name>/, shared_dir = bundled genesis.tasks/_shared/
    - --task_dir P   → P, shared_dir = P/../_shared/ if present else bundled _shared/
    """
    bundled_root = Path(str(resource_files("genesis.tasks")))
    bundled_shared = bundled_root / "_shared"

    if task:
        resolved = bundled_root / task
        if not resolved.is_dir():
            available = ", ".join(BUNDLED_TASKS)
            raise SystemExit(f"Bundled task '{task}' not found. Available: {available}")
        return str(resolved), str(bundled_shared)

    if task_dir:
        resolved = Path(task_dir).resolve()
        if not resolved.is_dir():
            raise SystemExit(f"Task directory does not exist: {task_dir}")
        external_shared = resolved.parent / "_shared"
        shared = external_shared if external_shared.is_dir() else bundled_shared
        return str(resolved), str(shared)

    raise SystemExit("Either --task or --task_dir must be provided")


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)


# ========================
# HELPER FUNCTIONS
# ========================


def load_agent_execution(gen_directory):
    """
    Load execution logs with automatic format detection.

    Supports two formats:
    1. Single-file: gen_X/agent_execution.json (backwards compatible)
    2. Multi-trajectory: gen_X/agent_execution/execution_q0.json, execution_q1.json, ...

    Args:
        gen_directory: Path to the generation directory

    Returns:
        tuple: (execution_data, is_multi_trajectory)
            - execution_data: dict or list containing execution log(s)
            - is_multi_trajectory: bool indicating if multi-trajectory format
    """
    execution_folder = os.path.join(gen_directory, "agent_execution")
    execution_file = os.path.join(gen_directory, "agent_execution.json")

    # Check for multi-trajectory folder first (new format)
    if os.path.isdir(execution_folder):
        logger.info("  → Detected multi-trajectory format (folder)")

        files = sorted(glob.glob(os.path.join(execution_folder, "execution_q*.json")))

        if not files:
            logger.warning("  ✗ agent_execution/ folder exists but is empty")
            return {"error": "Empty execution folder", "type": "multi-trajectory"}, True

        # Load all trajectory files
        trajectories = []
        for f in files:
            try:
                with open(f, encoding="utf-8") as fp:
                    trajectories.append(json.load(fp))
            except json.JSONDecodeError as e:
                logger.warning(f"  ✗ Failed to parse {os.path.basename(f)}: {e}")
                trajectories.append({"error": str(e), "file": os.path.basename(f)})
            except Exception as e:
                logger.warning(f"  ✗ Error reading {os.path.basename(f)}: {e}")
                trajectories.append({"error": str(e), "file": os.path.basename(f)})

        logger.info(f"  ✓ Loaded {len(trajectories)} trajectory files")

        return {"trajectories": trajectories, "count": len(trajectories), "type": "multi-trajectory"}, True

    # Fall back to single file (old format, backwards compatible)
    elif os.path.exists(execution_file):
        logger.info("  → Detected single-file format")

        try:
            with open(execution_file, encoding="utf-8") as f:
                data = json.load(f)
            logger.info("  ✓ Successfully loaded agent execution log")
            return data, False

        except json.JSONDecodeError as e:
            logger.warning(f"  ✗ Failed to parse agent_execution.json: {e}")
            logger.warning("  → The target agent may have crashed or failed to complete")

            # Return partial data for debugging
            try:
                with open(execution_file, encoding="utf-8") as f:
                    raw = f.read()
                return {
                    "error": "Parse error",
                    "raw_preview": raw[:1000],
                    "parse_error": str(e),
                    "file_size": len(raw),
                }, False
            except Exception as read_error:
                return {"error": "Could not read file", "read_error": str(read_error)}, False

        except FileNotFoundError:
            logger.error("  ✗ agent_execution.json not found")
            return {"error": "Execution log file not found"}, False

    # Neither exists
    else:
        logger.error("  ✗ No execution log found (neither file nor folder)")
        return {"error": "Execution log not found"}, False


def run_evaluation(gen_directory, task_dir, venv_dir):
    """
    Run evaluate.py if it exists in the task's public data directory.

    Args:
        gen_directory: Path to the generation directory containing submission files
        task_dir: Path to the task directory
        venv_dir: Path to the virtual environment

    Returns:
        dict: Evaluation results or error information
    """
    # Look for evaluate.py in data/public/ first, then fall back to task_dir
    evaluate_script = os.path.join(task_dir, "data/public/evaluate.py")
    if not os.path.exists(evaluate_script):
        evaluate_script = os.path.join(task_dir, "evaluate.py")

    # Check if evaluate.py exists
    if not os.path.exists(evaluate_script):
        logger.info(f"  → No evaluate.py found in {task_dir}, skipping evaluation")
        return {"status": "skipped", "reason": "evaluate.py not found"}

    logger.info(f"Running evaluation script: {evaluate_script}")

    # Create evaluation log file
    eval_log_file = os.path.join(gen_directory, "evaluation.log")
    logger.info(f"  → Evaluation log: {eval_log_file}")

    # Run evaluate.py as subprocess with --gen-dir
    try:
        python_exec = sys.executable  # Use system Python (has project dependencies)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        command = f"PYTHONPATH={project_root} {python_exec} {evaluate_script} --gen-dir {gen_directory} 2>&1 | tee {eval_log_file}"

        result = subprocess.run(command, shell=True, text=True, executable="/bin/bash")

        # Read evaluation log
        with open(eval_log_file) as f:
            eval_output = f.read()

        if result.returncode != 0:
            logger.error(f"  ✗ Evaluation failed with exit code {result.returncode}")
            return {
                "status": "error",
                "reason": f"evaluate.py exited with code {result.returncode}",
                "log_path": eval_log_file,
                "output": eval_output,
            }

        # Check if results.json was created
        results_json_path = os.path.join(gen_directory, "results.json")
        if os.path.exists(results_json_path):
            logger.info("  ✓ Evaluation completed successfully")
            logger.info(f"  ✓ Results saved to: {results_json_path}")

            # Load and log results
            try:
                with open(results_json_path) as f:
                    results = json.load(f)
                logger.info(f"    Results: {json.dumps(results, indent=2)}")
            except Exception:
                pass

            return {
                "status": "success",
                "log_path": eval_log_file,
                "results_path": results_json_path,
                "output": eval_output,
            }
        else:
            logger.warning("  ⚠ Evaluation completed but results.json not found")
            return {
                "status": "warning",
                "reason": "results.json not created by evaluate.py",
                "log_path": eval_log_file,
                "output": eval_output,
            }

    except Exception as e:
        logger.error(f"  ✗ Unexpected error during evaluation: {e}")
        logger.error(traceback.format_exc())
        return {"status": "error", "reason": str(e), "traceback": traceback.format_exc()}


def evolutionary_discovery_engine(
    current_agent_code: str,
    task_text: str,
    pipeline_evaluator: callable = None,
    population_size: int = 8,
    generations: int = 2,
    diversity_weight: float = 0.3,
) -> dict:
    """
    AlphaEvolve / FunSearch-style Evolutionary Discovery Engine (skeleton).

    Generates a population of agent variants, evaluates them using the GENESIS pipeline
    as strict evaluator (performance + robustness + cost proxy), selects with diversity + lineage.

    This is the core integration from GENESIS_DeepMind_AlphaEvolve_FunSearch_Theft_AR.md (Task 6).
    Currently a high-quality skeleton: LLM can be used later for mutation/crossover.
    Ties directly to Bridge task (uses run_minimal_pipeline as substrate).

    Args:
        current_agent_code: Base target_agent.py code to evolve from.
        task_text: The task description.
        pipeline_evaluator: Optional callable that runs the pipeline for fitness.
        population_size: Number of variants per generation.
        generations: Evolutionary generations.
        diversity_weight: Weight for diversity in selection (vs pure performance).

    Returns:
        dict with best_variant, population, lineage, metrics.
    """
    logger.info(f"  🧬 Starting Evolutionary Discovery Engine (population={population_size}, gens={generations})")

    if pipeline_evaluator is None:
        # Default: use the imported minimal_run as evaluator (real harness)
        try:
            from virtual_genesis.runtime.pipeline.minimal_run import run_minimal_pipeline

            def default_evaluator(code: str, task: str) -> dict:
                # In real use, this would exec the code or run the agent and call pipeline
                # For skeleton: simulate fitness using pipeline if available, else mock
                try:
                    # Placeholder: in full impl, write temp agent, run it, then call pipeline on traces
                    # For now, use a simple proxy (in production replace with full eval + pipeline)
                    fitness = 0.85 + (hash(code) % 100) / 1000.0  # mock for skeleton
                    cost = len(code) / 10000.0
                    robustness = 0.9
                    return {
                        "fitness": fitness,
                        "cost": cost,
                        "robustness": robustness,
                        "diversity_score": 0.5,
                        "details": "skeleton_eval (replace with real pipeline + agent exec)",
                    }
                except Exception as e:
                    return {"fitness": 0.1, "error": str(e)}

            pipeline_evaluator = default_evaluator
        except ImportError:
            pipeline_evaluator = lambda c, t: {"fitness": 0.5, "note": "pipeline not available in skeleton"}

    population = []
    lineage = []  # Track parent -> child for evolution

    # Seed population: base + simple mutations (in full: LLM generate variants)
    base = current_agent_code
    for i in range(population_size):
        if i == 0:
            variant = base
            parent = "seed"
        else:
            # Simple mutation skeleton (replace with LLM mutation/crossover from theft)
            mutation = f"# Evo variant {i}: added robustness comment + minor edit\n"
            variant = mutation + base[:500] + "\n# [evolved section]\n" + base[500:1000] + base[1000:]
            parent = "seed" if i < 3 else f"variant_{i-1}"

        eval_result = pipeline_evaluator(variant, task_text)
        fitness = eval_result.get("fitness", 0.5)
        cost = eval_result.get("cost", 1.0)
        robustness = eval_result.get("robustness", 0.8)

        # Multi-objective score (performance + robustness - cost + diversity bonus later)
        score = fitness * 0.6 + robustness * 0.3 - cost * 0.1

        population.append(
            {
                "id": f"variant_{i}",
                "code": variant[:2000] + "..." if len(variant) > 2000 else variant,
                "fitness": fitness,
                "cost": cost,
                "robustness": robustness,
                "score": score,
                "parent": parent,
                "eval_details": eval_result,
            }
        )
        lineage.append({"child": f"variant_{i}", "parent": parent, "score": score})

    # Evolve for generations (selection + mutation skeleton)
    for evo_gen in range(generations):
        logger.info(f"    Evo gen {evo_gen+1}/{generations}...")
        # Sort by score
        population.sort(key=lambda x: x["score"], reverse=True)
        # Keep top half + diversity injection (simple for skeleton)
        elites = population[: population_size // 2]
        # Diversity: pick some lower ones if diversity_weight high
        diverse = sorted(population, key=lambda x: x.get("diversity_score", 0), reverse=True)[: population_size // 4]
        population = elites + diverse
        # Pad with new mutations (skeleton)
        while len(population) < population_size:
            idx = len(population)
            mutation = f"# Evo-mutated in gen {evo_gen+1}\n"
            new_var = mutation + population[0]["code"][:800]
            eval_result = pipeline_evaluator(new_var, task_text)
            new_score = eval_result.get("fitness", 0.5) * 0.7 + 0.2
            population.append(
                {
                    "id": f"variant_{idx}_g{evo_gen+1}",
                    "code": new_var[:1500],
                    "fitness": eval_result.get("fitness", 0.5),
                    "score": new_score,
                    "parent": population[0]["id"],
                    "eval_details": eval_result,
                }
            )

        # Re-score with diversity bonus (simplified)
        for p in population:
            p["final_score"] = p["score"] + (diversity_weight * p.get("diversity_score", 0.4))

    # Final selection
    population.sort(key=lambda x: x.get("final_score", x["score"]), reverse=True)
    best = population[0]

    logger.info(f"  ✓ Evolutionary Discovery complete. Best fitness: {best['fitness']:.3f}, score: {best.get('final_score', best['score']):.3f}")
    logger.info(f"    Selected variant: {best['id']} (parent lineage tracked)")

    return {
        "best_variant": best,
        "population": population,
        "lineage": lineage,
        "metrics": {
            "avg_fitness": sum(p["fitness"] for p in population) / len(population),
            "best_fitness": best["fitness"],
            "diversity": len(set(p["parent"] for p in population)),
        },
        "note": "Skeleton implementation from AlphaEvolve theft. Full version will use LLM for true mutation/crossover + real pipeline calls + GRASP gating.",
    }



def _print_welcome():
    banner = rf"""
     _______. __       ___
    /       ||  |     /   \
   |   (----`|  |    /  ^  \
    \   \    |  |   /  /_\  \
.----)   |   |  |  /  _____  \
|_______/    |__| /__/     \__\

    Self-Improving AI framework

    • Version : v{__version__}
    • Docs    : https://github.com/hexo-ai/sia
    • Help    : genesis --help
"""
    print(banner)


def main():
    _print_welcome()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the orchestrator for agent evolution")
    parser.add_argument("--max_gen", type=int, default=3, help="Maximum number of generations to run (default: 3)")
    parser.add_argument("--run_id", type=int, default=1, help="Run ID for this experiment (default: 1)")
    parser.add_argument(
        "--use_evolutionary_discovery",
        action="store_true",
        help="Enable AlphaEvolve-style evolutionary search over agent variants (population + strict evaluator + diversity + lineage). Ties to GENESIS_DeepMind_AlphaEvolve_FunSearch_Theft_AR.md Task 6.",
    )
    task_group = parser.add_mutually_exclusive_group(required=True)
    task_group.add_argument(
        "--task",
        type=str,
        choices=BUNDLED_TASKS,
        help=f"Name of a bundled task shipped with genesis-agent ({', '.join(BUNDLED_TASKS)})",
    )
    task_group.add_argument(
        "--task_dir",
        type=str,
        help="Path to an external task directory (e.g., ./tasks/my-task)",
    )
    parser.add_argument(
        "--meta_model",
        type=str,
        default=None,
        help="Model to use for meta-agent (default: haiku for claude backend, gemini/gemini-3.1-pro-preview for openhands backend)",
    )
    parser.add_argument(
        "--task_model",
        type=str,
        default="claude-haiku-4-5-20251001",
        help="Model to use for target agent (default: claude-haiku-4-5-20251001)",
    )
    parser.add_argument(
        "--backend",
        type=str,
        default="claude",
        choices=["claude", "openhands", "openai"],
        help="Agent backend to use: claude (Claude Code SDK), openhands (OpenHands SDK), or openai (OpenAI-compatible, with compression fix) (default: claude)",
    )
    args = parser.parse_args()

    max_gen = args.max_gen
    task_dir, shared_dir = resolve_task_dir(args.task, args.task_dir)
    run_id = args.run_id
    backend = args.backend

    # Set default meta_model based on backend if not explicitly provided
    if args.meta_model is None:
        if backend == "openhands":
            meta_model = "gemini/gemini-3.1-pro-preview"
            logger.info("Using default OpenHands model: gemini/gemini-3.1-pro-preview")
        elif backend == "openai":
            meta_model = "openai/mimo-v2.5-pro"
            logger.info("Using default OpenAI-compatible model: openai/mimo-v2.5-pro")
        else:
            meta_model = "haiku"
            logger.info("Using default Claude model: haiku")
    else:
        meta_model = args.meta_model

    task_model = args.task_model

    logger.info("Configuration:")
    logger.info(f"  - Maximum generations: {max_gen}")
    logger.info(f"  - Task directory: {task_dir}")
    logger.info(f"  - Run ID: {run_id}")
    logger.info(f"  - Agent backend: {backend}")
    logger.info(f"  - Meta-agent model: {meta_model}")
    logger.info(f"  - Task-agent model: {task_model}")
    use_evo = getattr(args, "use_evolutionary_discovery", False)
    logger.info(f"  - Evolutionary Discovery (AlphaEvolve-style): {'ENABLED' if use_evo else 'disabled'}")

    # ========================
    # SECTION 1: Load Files from Task Directory
    # ========================

    logger.info("Loading files from task directory...")

    SAMPLE_TASK_DESCRIPTIONS = Path(task_dir, "reference/SAMPLE_TASK_DESCRIPTIONS.md").read_text()
    logger.info("  ✓ Sample task descriptions loaded")

    REFERENCE_TARGET_AGENT_PY = Path(task_dir, "reference/reference_target_agent.py").read_text()
    logger.info("  ✓ Reference target agent loaded")

    with open(os.path.join(shared_dir, "sample_agent_execution.json")) as f:
        SAMPLE_AGENT_EXECUTION = json.load(f)
    logger.info("  ✓ Sample agent execution loaded")

    TASK_MD = Path(task_dir, "data/public/task.md").read_text()
    logger.info("  ✓ Task specification loaded")

    # ========================
    # SECTION 2: Setup Run Directories
    # ========================

    gen_num = 1
    RUN_DIRECTORY = f"./runs/run_{run_id}"
    META_AGENT_WORKING_DIRECTORY = os.path.abspath(f"{RUN_DIRECTORY}/gen_{gen_num}")
    # Create run directory and meta_agent working directory
    if os.path.exists(RUN_DIRECTORY):
        logger.error(f"Run directory already exists: {RUN_DIRECTORY}")
        logger.error("Please use a different run_id or remove the existing directory")
        sys.exit(1)

    logger.info(f"Creating run directory: {RUN_DIRECTORY}")
    os.makedirs(RUN_DIRECTORY, exist_ok=False)

    logger.info(f"Creating meta_agent working directory: {META_AGENT_WORKING_DIRECTORY}")
    os.makedirs(META_AGENT_WORKING_DIRECTORY, exist_ok=False)

    # Create virtual environment
    venv_dir = os.path.join(RUN_DIRECTORY, "venv")
    logger.info(f"Creating virtual environment at: {venv_dir}")

    packages = [
        "anthropic",
        "openai",
        "python-dotenv",
        "google-genai",
        "tqdm",
        "pydantic",
        "scikit-learn",
        "pandas",
        "numpy",
    ]

    if shutil.which("uv"):
        subprocess.run(["uv", "venv", venv_dir], check=True)
        subprocess.run(
            ["uv", "pip", "install", "--python", os.path.join(venv_dir, "bin", "python"), *packages], check=True
        )
    else:
        venv.create(venv_dir, with_pip=True)
        subprocess.run([os.path.join(venv_dir, "bin", "pip"), "install", *packages], check=True)

    # Initialize Context Manager
    logger.info("Initializing context manager...")
    context_mgr = ContextManager(
        RUN_DIRECTORY,
        {
            "task_dir": task_dir,
            "meta_model": meta_model,
            "task_model": task_model,
            "backend": backend,
            "max_gen": max_gen,
        },
    )
    context_mgr.initialize()
    logger.info("  ✓ Context manager initialized")

    # ========================
    # SECTION 2.5: Initialize Research Memory (Phase 4)
    # ========================
    logger.info("Loading research memory...")
    research_memory = None
    research_insights = ""
    try:
        from genesis.research_memory import ResearchMemoryStore
        research_memory = ResearchMemoryStore()
        # Get insights from past runs
        if TASK_MD:
            research_insights = research_memory.get_insights_for_task(TASK_MD)
        stats = research_memory.get_stats()
        logger.info(f"  ✓ Research memory: {stats['total_experiments']} entries, {stats['success_rate']:.0%} success rate")
    except Exception as e:
        logger.info(f"  ⚠ Research memory unavailable: {e}")

    # ========================
    # SECTION 3: Define Prompts
    # ========================

    META_AGENT_PROMPT = f"""You are a meta-agent. Write target_agent.py NOW. Do NOT explore.

TASK: Create a target_agent.py that uses Virtual-GENESIS's cognitive pipeline + LLM.

IMPORTS (copy exactly):
```python
from virtual_genesis.runtime.pipeline.minimal_run import run_minimal_pipeline
from virtual_genesis.runtime.memory_os.store import InMemoryMemoryStore
from virtual_genesis.runtime.concept_engine.registry import InMemoryConceptRegistry
from virtual_genesis.runtime.theory_runtime.registry import InMemoryTheoryRegistry
from virtual_genesis.runtime.economy_control.ledger import InMemoryLedgerStore
from virtual_genesis.core.objects.memory import MemoryUnit
```

Pipeline call:
```python
result = run_minimal_pipeline(task_text, store=store, concept_registry=concept_registry, theory_registry=theory_registry, ledger_store=ledger_store)
# result has: task, memory_pack, concept_items, tier_decision, theory_prediction, verification
```

LLM call:
```python
import openai, httpx
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL","https://api.pioneer.ai/v1"))
resp = client.chat.completions.create(model="deepseek-ai/DeepSeek-V4-Flash", messages=[...])
```

Memory storage:
```python
memory = MemoryUnit.create(summary=summary, memory_type="episodic" if success else "negative")
store.store_memory(memory)
```

Write ONE file to {META_AGENT_WORKING_DIRECTORY}/target_agent.py using write_file.
Verify: bash("python3 -c 'compile(open(\"target_agent.py\").read(),\"target_agent.py\",\"exec\"); print(\"OK\")'")
Do NOT read files. JUST WRITE THE CODE.
"""

    FEEDBACK_AGENT_PROMPT = """Fix target_agent.py based on execution report. JUST WRITE CODE, NO EXPLORATION.

EXECUTION REPORT (gen {CURRENT_GEN}):
{EXECUTION_STATUS}
{EXECUTION_SECTION}
{SPIN_SECTION}

CURRENT CODE:
```python
{AGENT_PY}
```

Write IMPROVED code to: {IMPROVEMENT_DIR}/target_agent.py using write_file.
Verify syntax: bash("python3 -c 'compile(open(\"target_agent.py\").read(),\"target_agent.py\",\"exec\"); print(\"OK\")'")
STOP after writing. NO FILE READING.
"""

    # ========================
    # SECTION 4: Run Target Agent Creation (Meta-Agent)
    # ========================

    # Save the meta-agent prompt for debugging/transparency
    meta_agent_prompt_path = os.path.join(META_AGENT_WORKING_DIRECTORY, "meta_agent_prompt.txt")
    with open(meta_agent_prompt_path, "w", encoding="utf-8") as f:
        f.write(META_AGENT_PROMPT)
    logger.info(f"  ✓ Saved meta-agent prompt to: {meta_agent_prompt_path}")

    asyncio.run(
        run_agent(
            model_name=meta_model,
            max_turns="20",
            prompt=META_AGENT_PROMPT,
            agent_working_directory=META_AGENT_WORKING_DIRECTORY,
            backend=backend,
        )
    )

    # ========================
    # SECTION 5: Main Loop - Run Target Agent and Feedback Agent
    # ========================

    # Define the dataset directory and working directory to pass as arguments
    DATASET_DIRECTORY = os.path.join(task_dir, "data/public")
    ABS_DATASET_DIRECTORY = os.path.abspath(DATASET_DIRECTORY)
    logger.info(f"Dataset directory: {ABS_DATASET_DIRECTORY}")

    # Run the loop for max_gen generations
    # gen_1 is already created by meta-agent, so we loop from gen_1 to max_gen
    for current_gen in range(1, max_gen + 1):
        logger.info("=" * 80)
        logger.info(f"Starting Generation {current_gen} of {max_gen}")
        logger.info("=" * 80)

        # ========================
        # SECTION 5a: Run Target Agent
        # ========================

        current_gen_directory = os.path.abspath(f"{RUN_DIRECTORY}/gen_{current_gen}")
        target_agent_path = os.path.join(current_gen_directory, "target_agent.py")

        logger.info(f"Running target agent: {target_agent_path}")

        # Track execution results for feedback agent
        target_agent_success = True
        target_agent_stdout = ""
        target_agent_stderr = ""
        target_agent_error_msg = ""

        # Create log file paths
        stdout_log_file = os.path.join(current_gen_directory, "target_agent_stdout.log")
        stderr_log_file = os.path.join(current_gen_directory, "target_agent_stderr.log")

        logger.info(f"  → Stdout log: {stdout_log_file}")
        logger.info(f"  → Stderr log: {stderr_log_file}")
        logger.info("=" * 60)

        # Start timing for this generation
        generation_start_time = time.time()

        # Run target agent with real-time output using shell redirection
        try:
            # Build command with tee for real-time display and logging
            # Use PIPEFAIL to catch failures in the python command, not just tee
            python_exec = sys.executable  # Use system python (has virtual_genesis accessible)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            command = f"set -o pipefail; PYTHONPATH={project_root} {python_exec} -u {target_agent_path} --dataset_dir {ABS_DATASET_DIRECTORY} --working_dir {current_gen_directory} 2>&1 | tee {stdout_log_file}"

            # Run with shell=True and bash to enable pipefail
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                executable="/bin/bash",  # Use bash to support pipefail
            )

            return_code = result.returncode

            # Read captured output from file for feedback agent
            with open(stdout_log_file) as f:
                target_agent_stdout = f.read()
            # Since we're using 2>&1, stderr is merged into stdout
            target_agent_stderr = ""

            logger.info("=" * 60)

            # Check if execution was successful
            if return_code != 0:
                target_agent_success = False
                target_agent_error_msg = f"Target agent failed with exit code {return_code}"
                logger.error(f"  ✗ Target agent execution failed with exit code {return_code}")
                logger.warning("  → Continuing with feedback agent despite target agent failure")
            else:
                target_agent_success = True
                logger.info(f"  ✓ Generation {current_gen} target agent execution completed successfully")

        except FileNotFoundError:
            logger.error(f"  ✗ Target agent file not found: {target_agent_path}")
            logger.error("  → Cannot continue. Exiting.")
            sys.exit(1)
        except Exception as e:
            target_agent_success = False
            target_agent_error_msg = f"Unexpected error during target agent execution: {e!s}"
            logger.error(f"  ✗ {target_agent_error_msg}")
            logger.warning("  → Continuing with feedback agent despite target agent failure")

            # Try to read any partial logs
            try:
                with open(stdout_log_file) as f:
                    target_agent_stdout = f.read()
            except OSError:
                pass  # If log files don't exist, keep empty strings

        # Calculate execution duration
        generation_duration = time.time() - generation_start_time

        # ========================
        # SECTION 5a.1: Run Evaluation (if evaluate.py exists)
        # ========================

        logger.info("=" * 60)
        logger.info("Running evaluation (if available)...")
        run_evaluation(current_gen_directory, task_dir, venv_dir)
        logger.info("=" * 60)

        # ========================
        # SECTION 5a.2: Constitutional Self-Play Evaluation (Phase 2)
        # ========================

        logger.info("=" * 60)
        logger.info("Running constitutional evaluation...")
        try:
            from genesis.constitutional_evaluator import evaluate_constitutional

            # Read the agent code
            if os.path.exists(target_agent_path):
                with open(target_agent_path, encoding="utf-8") as f:
                    agent_code = f.read()

                report = evaluate_constitutional(
                    agent_code=agent_code,
                    gen_dir=current_gen_directory,
                    llm_evaluation=False,
                )

                # Save constitutional report
                constitutional_path = os.path.join(current_gen_directory, "constitutional_report.json")
                with open(constitutional_path, "w", encoding="utf-8") as f:
                    json.dump(report.to_dict(), f, indent=2)

                if report.passed:
                    logger.info(f"  ✅ Constitutional check PASSED (score: {report.total_score}/{report.max_allowed_score})")
                else:
                    logger.warning(f"  ❌ Constitutional check FAILED (score: {report.total_score}/{report.max_allowed_score})")
                    for v in report.violations:
                        logger.warning(f"     ⚠ {v.rule_name}: {v.description}")
            else:
                logger.warning("  ⚠ No target_agent.py found — skipping constitutional check")
        except Exception as e:
            logger.warning(f"  ⚠ Constitutional evaluation failed: {e}")
        logger.info("=" * 60)

        # Check if improvement.md exists in current gen directory (created by previous feedback agent)
        improvement_md_path = os.path.join(current_gen_directory, "improvement.md")

        # Add generation to context (do this before feedback agent runs)
        context_mgr.add_generation(
            gen_num=current_gen,
            gen_data={
                "success": target_agent_success,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "duration": generation_duration,
                "agent_path": target_agent_path,
                "gen_dir": current_gen_directory,
                "improvement_path": improvement_md_path if os.path.exists(improvement_md_path) else None,
                "execution_type": "Multi-trajectory"
                if (os.path.isdir(os.path.join(current_gen_directory, "agent_execution")))
                else "Single",
            },
        )

        # ========================
        # SECTION 5a.3: AlphaEvolve-style Evolutionary Discovery (if enabled)
        # ========================
        if use_evo:
            logger.info("  🧬 Running evolutionary discovery on this generation's agent (AlphaEvolve skeleton)...")
            try:
                with open(target_agent_path, encoding="utf-8") as f:
                    agent_code = f.read()
                evo_result = evolutionary_discovery_engine(
                    current_agent_code=agent_code,
                    task_text=TASK_MD,  # use the loaded task spec (available from SECTION 1)
                    population_size=6,  # smaller for skeleton
                    generations=1,
                )
                # Save the evo results for the run
                evo_path = os.path.join(current_gen_directory, "evolutionary_discovery.json")
                with open(evo_path, "w", encoding="utf-8") as f:
                    json.dump(evo_result, f, indent=2, default=str)
                logger.info(f"  ✓ Evolutionary results saved to {evo_path}")
                logger.info(f"    Best evo variant fitness: {evo_result['best_variant']['fitness']:.3f}")
                # Apply the best variant: write it as evolved_target_agent.py for use in feedback or next steps
                try:
                    best_code = evo_result['best_variant'].get('code', agent_code)
                    evolved_path = os.path.join(current_gen_directory, "evolved_target_agent.py")
                    with open(evolved_path, "w", encoding="utf-8") as f:
                        f.write(best_code)
                    logger.info(f"  ✓ Best evolved variant written to {evolved_path} (ready for feedback or next gen)")
                    # Record in research memory if available (ties to theft integration)
                    if research_memory:
                        research_memory.record_run_completion(
                            run_id=f"evo_{current_gen}",
                            total_generations=1,
                            best_score=evo_result['best_variant']['fitness'],
                            improvements=[f"Evo gen {current_gen}: fitness {evo_result['best_variant']['fitness']:.3f}"],
                        )
                except Exception as apply_e:
                    logger.warning(f"  ⚠ Could not apply best evo variant: {apply_e}")
            except Exception as e:
                logger.warning(f"  ⚠ Evolutionary discovery failed: {e}")

        # ========================
        # SECTION 5b: Run Feedback Agent (if not the last generation)
        # ========================

        if current_gen < max_gen:
            logger.info(f"Running feedback agent for generation {current_gen}")

            # Load artifacts produced by the target agent so the feedback prompt is fully populated.
            AGENT_PY = Path(current_gen_directory, "target_agent.py").read_text(encoding="utf-8")
            TASK = Path(DATASET_DIRECTORY, "task.md").read_text(encoding="utf-8")

            # Load agent execution log (supports both single-file and multi-trajectory formats)
            logger.info("Loading agent execution log...")
            AGENT_EXECUTION, is_multi_trajectory = load_agent_execution(current_gen_directory)

            # Build execution section for the feedback prompt
            if is_multi_trajectory:
                # Multi-trajectory format
                trajectory_count = AGENT_EXECUTION.get("count", 0)
                trajectories = AGENT_EXECUTION.get("trajectories", [])

                # Calculate success/failure counts
                # Successful trajectory = list of messages
                # Failed trajectory = dict with "error" key
                successful = sum(1 for t in trajectories if isinstance(t, list))
                failed = sum(1 for t in trajectories if isinstance(t, dict) and t.get("error"))
                # Note: failed might not equal trajectory_count - successful if there are unexpected formats

                # Show first 3 trajectories as examples
                sample_trajectories_text = ""
                for idx, traj in enumerate(trajectories[:3]):
                    traj_json = json.dumps(traj, indent=2)
                    # Truncate if too long
                    if len(traj_json) > 1000:
                        traj_json = traj_json[:1000] + "\n  ... (truncated)"
                    sample_trajectories_text += f"\n### Trajectory {idx}\n```json\n{traj_json}\n```\n"

                execution_section = f"""
**MULTI-TRAJECTORY EXECUTION**:

The agent executed {trajectory_count} separate trajectories (e.g., different questions/samples).

**Summary**:
- Total trajectories: {trajectory_count}
- Successful: {successful}
- Failed: {failed}
- Execution folder: {os.path.join(current_gen_directory, "agent_execution")}

**Sample Trajectories** (first 3 shown, you can read others from the folder):
{sample_trajectories_text}

**To analyze all trajectories**:
- Read files from: {os.path.join(current_gen_directory, "agent_execution")}
- Files named: execution_q0.json, execution_q1.json, ..., execution_q{trajectory_count - 1}.json

**Analysis guidance**:
- Look for common failure patterns across trajectories
- Check if trajectories are properly isolated
- Ensure consistent behavior across all samples
"""
            else:
                # Single-trajectory format (backwards compatible)
                execution_section = f"""
Here is the target agent execution trajectory:
```json
{json.dumps(AGENT_EXECUTION, indent=2)}
```

NOTE: If you see an "error" field in the above JSON, it means the execution log was malformed or missing. Focus on making the agent more robust.
"""

            # Load evaluation results if available
            eval_results_section = ""
            results_json_path = os.path.join(current_gen_directory, "results.json")
            if os.path.exists(results_json_path):
                try:
                    with open(results_json_path, encoding="utf-8") as f:
                        eval_data = json.load(f)
                    eval_results_section = f"""

**EVALUATION RESULTS**:
```json
{json.dumps(eval_data, indent=2)}
```
"""
                except Exception as e:
                    eval_results_section = f"\n**EVALUATION RESULTS**: Error loading results.json: {e}\n"
            else:
                eval_results_section = (
                    "\n**EVALUATION RESULTS**: No results.json found (evaluation may not have run or may have failed)\n"
                )

            # Load constitutional report if available
            constitutional_section = ""
            constitutional_path = os.path.join(current_gen_directory, "constitutional_report.json")
            if os.path.exists(constitutional_path):
                try:
                    with open(constitutional_path, encoding="utf-8") as f:
                        const_data = json.load(f)
                    passed_str = "✅ PASSED" if const_data.get("passed") else "❌ FAILED"
                    const_lines = [f"Constitutional check: {passed_str} (Score: {const_data.get('total_score', '?')}/{const_data.get('max_allowed_score','?')})"]
                    const_lines.append(f"Rule results:")
                    for rule_id, ok in const_data.get("rule_results", {}).items():
                        icon = "✅" if ok else "❌"
                        const_lines.append(f"  {icon} {rule_id}")
                    if const_data.get("violations"):
                        const_lines.append(f"Violations to fix:")
                        for v in const_data["violations"]:
                            const_lines.append(f"  ❌ {v['rule_name']}: {v['description']}")
                    constitutional_section = "\n".join(const_lines)
                except Exception as e:
                    constitutional_section = f"(Error reading constitutional report: {e})"

            # Prepare execution status for feedback agent
            if target_agent_success:
                # Get last 10 lines of stdout for quick preview
                stdout_lines = target_agent_stdout.split("\n")
                last_10_lines = "\n".join(stdout_lines[-10:]) if len(stdout_lines) > 10 else target_agent_stdout

                execution_status = f"""SUCCESS: Target agent completed execution successfully.
{eval_results_section}

**CONSTITUTIONAL EVALUATION**:
The following constitutional rules were checked. VIOLATIONS MUST BE FIXED in the next generation:

{constitutional_section}

**Last 10 lines of output**:
```
{last_10_lines}
```

Full logs available at: {stdout_log_file}
"""
            else:
                # Get last 10 lines of stdout for quick preview
                stdout_lines = target_agent_stdout.split("\n")
                last_10_lines = "\n".join(stdout_lines[-10:]) if len(stdout_lines) > 10 else target_agent_stdout

                execution_status = f"""FAILED: {target_agent_error_msg}
{eval_results_section}

**CONSTITUTIONAL EVALUATION**:
The following constitutional rules were checked. VIOLATIONS MUST BE FIXED:

{constitutional_section}

**Last 10 lines of output**:
```
{last_10_lines}
```

Full logs available at: {stdout_log_file}

STDERR:
{target_agent_stderr}
"""

            # Prepare next generation directory
            next_gen = current_gen + 1
            next_gen_directory = os.path.abspath(f"{RUN_DIRECTORY}/gen_{next_gen}")

            # Build previous generations list
            previous_gens_list = list(range(1, current_gen)) if current_gen > 1 else []
            previous_gens_text = ", ".join(map(str, previous_gens_list)) if previous_gens_list else "None"

            # ========================
            # SPIN Semantic Gap Analysis (Phase 3)
            # ========================
            spin_section = ""
            try:
                from genesis.spin_feedback import compute_semantic_gap, generate_spin_feedback

                # Compare the generated agent against the reference agent for semantic gap
                if os.path.exists(target_agent_path):
                    # Read reference agent for comparison
                    reference_path = os.path.join(task_dir, "reference", "reference_target_agent.py")
                    if os.path.exists(reference_path):
                        with open(reference_path, encoding="utf-8") as f:
                            reference_code = f.read()
                        # Use code as "strong" output (reference), current as "weak" output
                        gap = compute_semantic_gap(
                            task_text=TASK[:500] if TASK else "No task",
                            strong_output=reference_code[:3000],
                            weak_output=AGENT_PY[:3000],
                        )
                        spin_section = f"""**SPIN SEMANTIC GAP ANALYSIS**:
Semantic distance from reference: {gap.cosine_distance:.3f} ({gap.gap_category})
Improvement priority: {gap.improvement_priority:.2f}
{'- Large gap → significant room for improvement' if gap.gap_category == 'large' else '- Moderate gap → refine existing patterns' if gap.gap_category == 'medium' else '- Small gap → agent is close to optimal'}
"""
                        logger.info(f"  SPIN gap: {gap.cosine_distance:.3f} ({gap.gap_category})")
            except Exception as e:
                logger.debug(f"  SPIN analysis skipped: {e}")

            # Call feedback agent with full context
            feedback_agent_prompt_prepared = FEEDBACK_AGENT_PROMPT.format(
                CURRENT_GEN=current_gen,
                AGENT_PY=AGENT_PY,
                TASK=TASK,
                EXECUTION_STATUS=execution_status,
                EXECUTION_SECTION=execution_section,
                SPIN_SECTION=spin_section,
                IMPROVEMENT_DIR=next_gen_directory,
            )

            os.makedirs(next_gen_directory, exist_ok=True)

            # Save the feedback agent prompt for debugging/transparency
            feedback_prompt_path = os.path.join(next_gen_directory, "feedback_agent_prompt.txt")
            with open(feedback_prompt_path, "w", encoding="utf-8") as f:
                f.write(feedback_agent_prompt_prepared)
            logger.info(f"  ✓ Saved feedback agent prompt to: {feedback_prompt_path}")
            asyncio.run(
                run_agent(
                    model_name=meta_model,
                    max_turns="20",  # Feedback agent needs more turns for DeepSeek reasoning
                    prompt=feedback_agent_prompt_prepared,
                    agent_working_directory=next_gen_directory,
                    backend=backend,
                )
            )

            logger.info(f"Feedback agent completed. Created improved agent for generation {next_gen}")
        else:
            logger.info(f"Generation {current_gen} is the final generation. Skipping feedback agent.")

    # Finalize context with summary statistics
    logger.info("Finalizing context.md with summary statistics...")
    context_mgr.finalize()

    logger.info("=" * 80)
    logger.info(f"Orchestrator completed all {max_gen} generations successfully!")
    logger.info(f"Results saved in: {RUN_DIRECTORY}")
    logger.info(f"Context summary: {os.path.join(RUN_DIRECTORY, 'context.md')}")
    logger.info("=" * 80)

    # ========================
    # SECTION 7: Record in Research Memory (Phase 4)
    # ========================
    if research_memory:
        try:
            # Calculate best score from all generations
            best_score = 0.0
            improvements = []
            for gen in range(1, max_gen + 1):
                const_path = os.path.join(RUN_DIRECTORY, f"gen_{gen}", "constitutional_report.json")
                eval_path = os.path.join(RUN_DIRECTORY, f"gen_{gen}", "evaluation_results.json")
                
                if os.path.exists(eval_path):
                    with open(eval_path) as f:
                        edata = json.load(f)
                    score = edata.get("overall_score", 0)
                    if score > best_score:
                        best_score = score
                    improvements.append(f"Gen {gen}: score {score:.1%}")
            
            research_memory.record_run_completion(
                run_id=os.path.basename(RUN_DIRECTORY),
                total_generations=max_gen,
                best_score=best_score,
                improvements=improvements,
            )
            logger.info("  ✓ Run recorded in research memory")
        except Exception as e:
            logger.debug(f"  ⚠ Research memory record failed: {e}")


if __name__ == "__main__":
    main()
