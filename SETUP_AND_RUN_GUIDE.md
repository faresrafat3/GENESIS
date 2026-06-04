# GENESIS Full Setup & Real Benchmark Run Guide (OpenRouter + Evolutionary Discovery)

This guide prepares the entire project from the repo for **real paper/project-level experimentation**.

We will:
- Clone and install GENESIS.
- Configure for OpenRouter with `openai/gpt-oss-120b:free` (as requested).
- Enable the AlphaEvolve-style Evolutionary Discovery Engine (`--use_evolutionary_discovery`).
- Run on serious benchmarks (SWE-bench as primary, gpqa, spaceship-titanic).
- Measure impact of the "legitimate thefts" (especially AlphaEvolve + prior ones like GRASP, ExpGraph, Aletheia).

**Goal**: Run the self-improving orchestrator on high-quality agentic benchmarks using the free OpenRouter model, see how the evolutionary search improves performance over the baseline (98.6% keyword matching → genuine reasoning).

## Prerequisites
- Python >= 3.10
- Git
- OpenRouter API key (get free tier at https://openrouter.ai/keys). The model `openai/gpt-oss-120b:free` is used for **all** LLM calls (meta-agent and target agents).
- (Optional for SWE-bench) Access to SWE-bench data (https://github.com/princeton-nlp/SWE-bench)

## Step 1: Clone the Repo
```bash
git clone https://github.com/faresrafat3/GENESIS.git
cd GENESIS
```

## Step 2: Install the Project
```bash
# Install in editable mode with dev dependencies
pip install -e .[dev]

# Verify installation
python -c "import genesis; print('GENESIS imported successfully')"
python -m genesis.orchestrator --help
```

**Note**: The project uses a mix of `genesis/` (CLI/orchestrator) and `virtual_genesis/` (core runtime). The editable install handles this.

## Step 3: Configure OpenRouter + Your Model
Set these environment variables (use the free tier model everywhere):

```bash
export OPENAI_API_KEY="sk-or-YOUR_OPENROUTER_KEY_HERE"
export OPENAI_BASE_URL="https://openrouter.ai/api/v1"

# Verify
python -c "
import os
print('API Key set:', bool(os.getenv('OPENAI_API_KEY')))
print('Base URL:', os.getenv('OPENAI_BASE_URL'))
"
```

In all runs, we force:
- `--backend openai`
- `--meta_model openai/gpt-oss-120b:free`
- `--task_model openai/gpt-oss-120b:free`

The orchestrator and benchmark script default to this when using the openai backend.

## Step 4: Verify Core Components (Quick Test)
```bash
# Run unit tests (especially the evolutionary discovery tests we added)
python -m pytest tests/test_evolutionary_discovery.py -q

# Quick dry-run of orchestrator (no real API calls if you skip LLM parts)
python -m genesis.orchestrator --help
```

## Step 5: Run on Benchmarks

We use the prepared `run_openrouter_benchmark.py` script (or direct orchestrator calls).

### Recommended Serious Benchmarks (Paper-Level)
- **SWE-bench** (primary for real agentic coding): Real GitHub issues → patches that fix bugs and pass tests. Perfect to show self-improving evolutionary agents.
- **gpqa**: Hard graduate-level science reasoning (tests genuine vs keyword matching).
- **spaceship-titanic**: Fast tabular baseline for quick validation.

### Easy One-Command Runs (Internal/Quick Validation)
```bash
# Spaceship-titanic (fast, with evolutionary discovery)
python run_openrouter_benchmark.py \
  --task spaceship-titanic \
  --max_gen 2 \
  --run_id 1 \
  --use_evolutionary_discovery

# gpqa (hard reasoning)
python run_openrouter_benchmark.py \
  --task gpqa \
  --max_gen 2 \
  --run_id 2 \
  --use_evolutionary_discovery
```

The script automatically:
- Uses your OpenRouter key + gpt-oss-120b:free.
- Enables the AlphaEvolve engine when the flag is passed.
- Outputs to `runs/run_<id>/` with `evolutionary_discovery.json`, `evolved_target_agent.py`, results, etc.

### Serious Benchmark: SWE-bench (Real Project/Paper Mode)
SWE-bench requires setting up task data (repos + issues).

1. Follow SWE-bench setup: https://github.com/princeton-nlp/SWE-bench (download dataset, prepare instances).

2. Use the benchmark script for instructions:
```bash
python run_openrouter_benchmark.py --task swe_bench --max_gen 2 --use_evolutionary_discovery
```
It will print exact commands and setup notes.

3. Or run directly with a prepared SWE-bench task directory:
```bash
python -m genesis.orchestrator \
  --task_dir /path/to/your/swe_bench_task_instance \
  --max_gen 2 \
  --backend openai \
  --meta_model "openai/gpt-oss-120b:free" \
  --task_model "openai/gpt-oss-120b:free" \
  --use_evolutionary_discovery
```

The evolutionary engine will generate/evolve better `target_agent.py` that uses the full GENESIS cognitive pipeline (concepts, theories, memory, verification) to reason about the code issue.

After generation, evaluate the resulting patches with the official SWE-bench harness.

**Run with and without `--use_evolutionary_discovery`** to isolate the impact of the thefts.

## Step 6: Analyze Results & Measure Impact
After each run, inspect `runs/run_<id>/`:

- `evolutionary_discovery.json`: Population, best fitness, lineage, metrics from AlphaEvolve engine.
- `evolved_target_agent.py`: The best evolved agent code.
- `results.json`, `constitutional_report.json`: Performance, robustness.
- `context.md`: Full trace.

Key comparisons (baseline 98.6% was keyword-heavy on v3b_curriculum):
- Success rate / % resolved (for SWE-bench).
- Discovery rate / evolutionary metrics.
- Genuine reasoning signals (vs keyword matching in verification).
- Cost (tokens/generations) vs quality.
- Transfer to other tasks.

Use the existing ablation tools (`virtual_genesis/eval/runners/`) for deeper analysis.

## Step 7: Full Reproducible Experiment Plan (for Paper)
1. Run the 3 recommended benchmarks **with** and **without** evolutionary discovery.
2. Log everything (use different run_ids).
3. Collect:
   - Quantitative: success rates, evo fitness lift, patch resolution % on SWE-bench.
   - Qualitative: examples of evolved improvements.
4. Compare to original GENESIS baseline and published numbers for gpt-oss-120b-like models on SWE-bench/gpqa.
5. Document in new results/ or a paper draft section.

## Troubleshooting
- **API errors**: Check OPENAI_API_KEY and BASE_URL. OpenRouter free tier has rate limits.
- **Packaging issues**: Re-run `pip install -e .`
- **No tasks found**: Use `--task_dir` for external or ensure bundled tasks are accessible.

## Recent Prompt Robustness Fixes (from run_49, 2026-06-04)
- Added to META/FEEDBACK prompts: explicit "imports at VERY TOP", GENERAL data loading (full pd.read_csv shapes, no column hardcodes like 'Mars'), MANDATORY robust execution logging block with fallback.
- This fixed (in run_49 vs prior): Gen1 json scope error + wrong data shape (870,2); Gen2 wrote agent_execution.json successfully; evo ran clean; no file-not-found.
- Always use --use_evolutionary_discovery to test AlphaEvolve (5.84) + 5.87.
- Reminder: keep ALL changes GENERAL to protect long-term vision (no overfitting to spaceship-titanic proxy).
- Next recommended: rm -rf runs/run_49; python run_openrouter_benchmark.py --task gpqa --max_gen 2 --run_id 50 --use_evolutionary_discovery (test transfer).
- **Evo not triggering**: Confirm `--use_evolutionary_discovery` flag and that the call site in orchestrator is reached.
- For SWE-bench full harness: You will need Docker + the official SWE-bench eval code.

## Next Steps After Running
- Share results/ablation summaries.
- We can iterate: improve the real pipeline evaluator in the evo engine, add Co-Scientist tournament, integrate more with run_real_llm_eval.py, or prepare more task adapters.
- Push any new results back to the repo.

**Ready?** Set your OpenRouter key, pick a benchmark, and run:
```bash
python run_openrouter_benchmark.py --task gpqa --max_gen 2 --use_evolutionary_discovery
```

يلا بسم الله! The project is now fully prepared for real serious benchmarking on OpenRouter with the evolutionary thefts. 

If you hit any issue during setup/run, paste the error and we'll fix it immediately. 

(Files updated/pushed: SETUP_AND_RUN_GUIDE.md, run_openrouter_benchmark.py, Strategic Plan, orchestrator defaults for OpenRouter.) 

All changes are in the main branch on GitHub. Clone fresh if needed.