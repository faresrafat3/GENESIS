# §12 Appendices

## Appendix A: Full Prompts

### A.1 SCIENTIFIC_MCQ_SYSTEM_PROMPT (post-fix)
```
You are an expert scientist (physics, chemistry, biology) taking a graduate-level
multiple-choice exam (GPQA Diamond level). Each question has exactly 4 options labeled A, B, C, D
and exactly one is correct.

RESPONSE PROTOCOL — follow strictly:
1. Reason carefully and step by step about the underlying science.
2. Eliminate clearly wrong options when possible.
3. You MUST end your reply with a final line in EXACTLY this format (no other text after it):

ANSWER: X

where X is one single letter A, B, C, or D. The line must literally start with the word ANSWER
followed by a colon and a space, then the letter. Do NOT add explanations after the ANSWER line.
If you are unsure, still output your best guess in the ANSWER line — never refuse, never output
"unknown" or "I don't know".
```

### A.2 FORCE_LETTER_PROMPT (retry)
```
STOP THINKING. Just output one line with your best guess in this exact format:

ANSWER: X

where X is one of A, B, C, or D. Output ONLY that single line — no reasoning,
no explanation, no markdown, nothing else. Just the literal string 'ANSWER: '
followed by one capital letter.
```

### A.3 META_AGENT_PROMPT (excerpt of Q&A guidance)
See `genesis/orchestrator.py` for full prompt. Post-fix version references `genesis/llm_helpers.py`.

## Appendix B: extract_letter Regex Patterns (16 total)

```python
# Priority 1: Explicit ANSWER lines
r"ANSWER\s*[:\-=]+\s*\*?\*?\s*([ABCD])\s*\*?\*?"
r"\bANSWER\s+IS\s*[:\-=]?\s*\*?\*?\s*([ABCD])\b"
r"FINAL\s+ANSWER\s*[:\-=]+\s*\*?\*?\s*([ABCD])"
r"THE\s+ANSWER\s+IS\s*[:\-=]?\s*\*?\*?\s*([ABCD])"
r"CORRECT\s+(?:ANSWER|OPTION)\s+IS\s*[:\-=]?\s*\*?\*?\s*([ABCD])"
r"OPTION\s*[:\-=]?\s*\*?\*?\s*([ABCD])\s*\*?\*?\s*(?:IS|$)"

# Priority 2: Markdown/LaTeX wrappers in tail
r"\*\*\s*([ABCD])\s*\*\*"
r"\\boxed\{\s*([ABCD])\s*\}"
r"\\textbf\{\s*([ABCD])\s*\}"
r"\(\s*([ABCD])\s*\)\s*$"
r"\s([ABCD])\s*\.\s*$"
r"^\s*([ABCD])\s*$"

# Priority 3: Last line as letter
r"^(?:answer\s*[:\-]?\s*)?\*?\*?\s*([ABCD])\s*\*?\*?\s*\.?\s*$"

# Priority 4: Last A-D in tail-200 chars
r"\b([ABCD])\b"
```

## Appendix C: Model IDs and Sources

### Table C.1: Model Details

| Shortcut | OpenRouter ID | Native Provider | Notes |
|---|---|---|---|
| gpt-oss-120b | openai/gpt-oss-120b:free | OpenAI (open weights) | 131K ctx, reasoning |
| nemotron-nano | nvidia/nemotron-3-nano-30b-a3b:free | NVIDIA | 1M ctx, MoE |
| nemotron-super | nvidia/nemotron-3-super-120b-a12b:free | NVIDIA | 1M ctx, MoE |
| nemotron-ultra | nvidia/nemotron-3-ultra-550b-a55b:free | NVIDIA | 1M ctx, MoE, agent-tuned |
| gemma-4-31b | google/gemma-4-31b-it:free | Google | 262K ctx, multimodal |
| glm-4.5-air | z-ai/glm-4.5-air:free | Zhipu | 131K ctx, tool-focused |
| lfm-2.5-thinking | liquid/lfm-2.5-1.2b-thinking:free | Liquid | 32K ctx, tiny |

## Appendix D: Full Baseline Data (gpt-oss-120b, 20q)

See `results/run_gpt-oss-120b_20q/gpt-oss-120b-free.json` for raw data.

Structure per question:
```json
{
  "question_id": 1,
  "domain": "Physics",
  "subdomain": "Physics (general)",
  "correct_answer_letter": "A",
  "predicted_letter": "A",
  "round1_pred": "A",
  "used_followup": false,
  "is_correct": true,
  "response_chars": 840,
  "round1_meta": {
    "finish_reason": "stop",
    "content_chars": 840,
    "reasoning_chars": 3521,
    "usage": {
      "prompt_tokens": 152,
      "completion_tokens": 1075,
      "total_tokens": 1227,
      "reasoning_tokens": 923
    }
  },
  "response_excerpt": "...",
  "followup_excerpt": null
}
```

## Appendix E: Full Test Suite

All tests in `tests/`. Run: `python -m pytest tests/ -v`

### Categories
- `test_llm_helpers.py` — 35 tests (16 extract_letter, 5 field readers, 5 options, 4 IDs, 5 build_mcq)
- Previous existing: 428 tests across various modules

**Total: 463 passing**

## Appendix F: Cross-Reference to Stolen Papers

See `paper/sources/README.md` and `GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md` for the full theft list (100+ entries).

### Papers directly informing this work:
1. **AlphaEvolve / FunSearch** — evolutionary_discovery_engine skeleton
2. **Aletheia** — feedback_agent as verify-revise loop
3. **Co-Scientist** — 3-agent structure (deferred debate)
4. **GPQA** — primary benchmark
5. **gpt-oss card** — primary model, reasoning effort baseline

### Papers we build on:
6. Wei et al. 2022 — Chain-of-Thought Prompting
7. Chowdhery et al. 2022 — Scaling
8. Rein et al. 2023 — GPQA

## Appendix G: Reproducibility Package

### G.1 Environment
```
Python 3.13
Required packages (from pyproject.toml):
  openai>=1.99, pandas, numpy, scikit-learn, python-dotenv,
  pydantic, tqdm, google-genai, anthropic
Test framework: pytest 9.0+
```

### G.2 Setup Instructions
```bash
git clone https://github.com/faresrafat3/GENESIS
cd GENESIS
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env
# Fill in your OPENROUTER_API_KEY_* (see .env.example for format)
python tools/api_key_pool.py --test_call
```

### G.3 Running Experiments
```bash
# Pure baseline (reproduces §5)
python tools/run_multi_model_benchmark.py \
    --models gpt-oss-120b-free \
    --limit 20 \
    --reasoning high \
    --max_tokens 16384 \
    --output_dir results/replicate_baseline

# GENESIS post-fix (reproduces §7 once T1 runs)
python run_openrouter_benchmark.py \
    --task gpqa --max_gen 2 --run_id 100 \
    --use_evolutionary_discovery \
    --meta_model openai/gpt-oss-120b:free \
    --task_model openai/gpt-oss-120b:free
```

### G.4 Analysis Scripts
- `tools/diagnose_run_53.py` — audit any run for 5 bugs
- Custom analysis: see notebooks or aggregation scripts in `paper/data/`

## Appendix H: Commit History (Chronological)

| Commit | Description | Impact on Paper |
|---|---|---|
| Initial | Base GENESIS repo | Setup |
| `33ada0a` | tools/diagnose_run_53.py + bug discovery | §6 evidence |
| `91cd9ea` | 6 critical fixes + smoke v2 | §5, §6 |
| `a609c90` | Pure baseline 75% measurement | §5 primary data |
| `6240094` | Multi-provider registry (9 providers) | §4.3.2 |
| `3a16a87` | Port fixes to orchestrator (THE FIX) | §6 fix implementations |
| `3cbe48b` | Research report (pre-paper) | Foundation |
| (this) | Paper skeleton + drafts | §0-12 |

## Appendix I: Notes for Future Agents

See `AGENT_CHARTER.md` for full workflow guidance. Key points:
- Read charter first
- Update this document + `paper/README.md` when adding experiments
- Cross-reference stolen papers when possible
- Include raw data files in `paper/data/`
- Generate figures as SVG in `paper/figures/`

---

**Section status:** 🟡 Skeleton, expand as experiments complete.
