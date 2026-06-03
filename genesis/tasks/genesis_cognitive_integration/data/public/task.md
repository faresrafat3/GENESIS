# 🧠 TASK: Virtual-GENESIS Cognitive-LLM Integration (Phase 1 — Bridging the Gap)

## 📌 Mission Overview

You are tasked with the **most critical architectural transformation** in Virtual-GENESIS's history: **bridging the gap between the deterministic cognitive pipeline and real LLM reasoning**.

Currently, Virtual-GENESIS's `run_reasoning()` function uses **string templates** to generate responses. This means the "98.6% success rate" is actually "98.6% keyword matching" — not genuine intelligence. Your mission is to create a **new target_agent.py** that uses Virtual-GENESIS's cognitive pipeline as a **reasoning substrate** for an actual LLM, replacing template-based reasoning with LLM-backed reasoning guided by the cognitive architecture.

---

## 🏛️ Current Architecture (What Exists)

### Virtual-GENESIS Pipeline (`virtual_genesis/runtime/pipeline/minimal_run.py`)
The pipeline has these stages:
1. **Task Ingress** — classifies task family (comparison, synthesis, procedure, analysis, extraction, planning)
2. **Memory Retrieval** — retrieves relevant past experiences
3. **Concept Engine** — activates relevant concepts
4. **Economy Control** — chooses reasoning tier (tier_0/tier_1/tier_2)
5. **Reasoning** — ⚠️ CURRENTLY: string templates (THIS IS WHAT YOU FIX)
6. **Verification** — checks output quality
7. **Escalation** — escalates if quality is insufficient

### The Problem
`reasoning_runtime/service.py` has functions like `_render_comparison()`, `_render_synthesis()`, etc. that generate responses by assembling pre-written text fragments. This is NOT reasoning — it's template filling.

---

## 🎯 Your Mission

Create a **target_agent.py** that:

### 1. Uses Virtual-GENESIS's Pipeline as Cognitive Substrate
```python
from virtual_genesis.runtime.pipeline.minimal_run import run_minimal_pipeline
```
The pipeline returns:
- `task` — classified task with family, difficulty, criticality
- `memory_pack` — retrieved memories and lessons
- `concept_items` — activated concepts
- `tier_decision` — chosen reasoning tier
- `theory_prediction` — predicted difficulty/failure
- `verification` — output quality checks

### 2. Injects Cognitive Hints into LLM Prompt
Instead of using template reasoning, build an LLM prompt that includes:
- **Task classification**: "This is a {family} task with {difficulty} difficulty"
- **Memory hints**: "Past experiences suggest: {memory_pack}"
- **Concept guidance**: "Relevant concepts: {concept_items}"
- **Theory predictions**: "Theory predicts: {theory_prediction}"
- **Tier guidance**: "Use {tier} level reasoning (tier_0=quick, tier_1=standard, tier_2=deep)"

### 3. Replaces Template Reasoning with LLM Call
```python
# OLD (template-based):
reasoning = run_reasoning(task_text, family, memory_pack, tier, frames)

# NEW (LLM-backed with cognitive hints):
cognitive_context = build_cognitive_context(task, memory_pack, concepts, theory_prediction, tier)
llm_response = call_llm(task_text, cognitive_context)
```

### 4. Stores Results as Memories
After each task:
- Success → store as episodic memory with metadata
- Failure → store as negative memory with failure analysis
- Concepts form from patterns across multiple tasks

### 5. Uses Verification for Quality Control
Use Virtual-GENESIS's verification system to check LLM output quality:
- If verification fails → escalate to higher tier or retry with different framing
- If verification passes → store as successful experience

---

## 🔧 Technical Requirements

### File Structure
Create these files in your working directory:
1. **`target_agent.py`** — Main agent that integrates Virtual-GENESIS pipeline with LLM
2. **`cognitive_prompt_builder.py`** — Builds LLM prompts with cognitive hints (optional, can be in target_agent.py)

### Dependencies
Use these imports (they exist in the codebase):
```python
from virtual_genesis.runtime.pipeline.minimal_run import run_minimal_pipeline
from virtual_genesis.runtime.concept_engine.registry import InMemoryConceptRegistry
from virtual_genesis.runtime.memory_os.store import InMemoryMemoryStore
from virtual_genesis.runtime.economy_control.ledger import InMemoryLedgerStore
from virtual_genesis.runtime.theory_runtime.registry import InMemoryTheoryRegistry
```

### LLM Integration
Use the OpenAI-compatible API (already configured in the reference agent):
```python
import openai
client = openai.AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)
```

### Execution Flow
```
For each task in dataset:
  1. Run Virtual-GENESIS pipeline: result = run_minimal_pipeline(task_text, store, concepts, theories, ...)
  2. Extract cognitive hints from result
  3. Build LLM prompt with cognitive hints
  4. Call LLM: response = call_llm(prompt)
  5. Verify response using Virtual-GENESIS's verification
  6. Store result as memory (success or failure)
  7. Log trajectory
```

---

## 📊 Expected Outcomes

### Before (Current State)
- 98.6% success = keyword matching
- Reasoning = string templates
- No genuine intelligence

### After (Your Target)
- LLM reasoning guided by cognitive architecture
- Concepts, memories, and theories INFORM the LLM
- Failed tasks generate negative memories
- Concepts form from failure patterns
- **Genuine intelligence, not keyword matching**

---

## 🧪 Evaluation Criteria

1. **Test Success Rate**: 424/424 tests must pass (zero regressions)
2. **Cognitive Integration**: The target_agent.py MUST use `run_minimal_pipeline()`
3. **LLM Reasoning**: The target_agent.py MUST call an LLM (not templates)
4. **Memory Formation**: Failed tasks MUST be stored as negative memories
5. **Concept Formation**: Patterns across tasks MUST generate concepts

---

## 🚫 What NOT to Do

1. **DO NOT** modify Virtual-GENESIS's core modules (Layer A is locked)
2. **DO NOT** use template-based reasoning (that defeats the purpose)
3. **DO NOT** skip the cognitive pipeline (that defeats the purpose)
4. **DO NOT** hardcode dataset paths (use --dataset_dir argument)
5. **DO NOT** break existing tests

---

## 🔑 Key Insight

The breakthrough is NOT replacing Virtual-GENESIS with an LLM. The breakthrough is **using Virtual-GENESIS's cognitive architecture to GUIDE the LLM**. The LLM does the reasoning; Virtual-GENESIS provides the cognitive infrastructure (concepts, memories, theories, verification).

This is the difference between:
- ❌ "98.6% keyword matching" (current)
- ✅ "LLM reasoning guided by cognitive architecture" (your target)

---

## 📚 Reference Files

- **Pipeline**: `virtual_genesis/runtime/pipeline/minimal_run.py`
- **Reasoning**: `virtual_genesis/runtime/reasoning_runtime/service.py` (template-based — to be replaced)
- **Memory**: `virtual_genesis/runtime/memory_os/store.py`
- **Concepts**: `virtual_genesis/runtime/concept_engine/registry.py`
- **Verification**: `virtual_genesis/runtime/verification_runtime/service.py`
- **Reference Agent**: `sia/tasks/virtual_genesis_optimization/reference/reference_target_agent.py`

---

## 🏁 Success Criteria

1. ✅ `target_agent.py` uses `run_minimal_pipeline()`
2. ✅ `target_agent.py` calls an LLM with cognitive hints
3. ✅ Failed tasks generate negative memories
4. ✅ 424/424 tests pass
5. ✅ The agent genuinely reasons (not keyword matching)

---

*This is the most important task in SIA's history. You are bridging the gap between deterministic cognitive architecture and genuine LLM intelligence. Good luck.*
