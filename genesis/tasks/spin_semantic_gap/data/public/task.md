# 🧠 TASK: SPIN Semantic Gap Self-Training (Phase 3)

## 📌 Mission Overview

Integrate **SPIN-OFF Semantic Gap Feedback** (from DeepSeek AI, June 2026) into the SIA self-improvement loop.

Currently, the feedback agent receives binary pass/fail signals. With SPIN, the agent receives a **continuous semantic distance metric** — how far the generated agent's reasoning is from the optimal reference — enabling more nuanced, gradient-guided improvement.

## 🎯 Core Concept: Semantic Gap

```
SPIN Cycle:
  1. Generate STRONG answer (best-of-N sampling with temperature=0.7)
  2. Generate WEAK answer (single sample with temperature=0.0)
  3. Compute cosine distance between their vector representations
  4. Use the gap as a learning signal:
     - Large gap (>0.5) → HIGH priority for improvement
     - Medium gap (0.2-0.5) → moderate refinement needed
     - Small gap (<0.2) → agent is close to optimal, move to harder tasks
```

## 🏗️ What to Build

Create a target_agent.py that:

### 1. Produces Semantic Gap Metrics
For each task execution, compute:
- `semantic_gap`: cosine distance between strong and weak outputs
- `gap_category`: "small", "medium", or "large"
- `improvement_priority`: 0.0-1.0 priority score
- `gap_trend`: whether the gap is shrinking or growing across generations

### 2. Uses the Gap for Feedback
Instead of just "PASS" or "FAIL", the agent should:
- Report the semantic gap in its execution output
- Prioritize tasks with the largest gaps
- Show gap trends across generations

### 3. Implements Best-of-N Sampling
- STRONG: 3 samples with temperature=0.7, select longest/best
- WEAK: 1 sample with temperature=0.0
- Store both outputs for gap computation

### 4. Tracks Gap Trends
- Save gap history across executions
- Report whether the gap is shrinking (improvement) or growing (regression)

## 📊 Success Criteria

- ✅ Computes semantic gap between strong and weak outputs
- ✅ Categorizes gap (small/medium/large)
- ✅ Reports improvement priority
- ✅ Tracks gap trend across generations
- ✅ Uses sys.executable (not venv python) for compatibility
- ✅ All 424 tests pass
- ✅ Constitutional score ≤ 10
- ✅ Cognitive + LLM + Memory scores = 100%

## 🔬 Reference Implementation

Key functions in `sia/spin_feedback.py`:
- `compute_semantic_gap(task, strong_output, weak_output)` → GapReport
- `generate_spin_feedback(agent_code, results, gaps)` → feedback text
- `cosine_distance(a, b)` → float (0=identical, 1=orthogonal)
- `simple_text_vectorize(text)` → np.ndarray

## 📁 Files

- `sia/spin_feedback.py` — SPIN feedback module (already built)
- `sia/constitutional_evaluator.py` — Constitutional checks
- `virtual_genesis/runtime/pipeline/minimal_run.py` — Cognitive pipeline