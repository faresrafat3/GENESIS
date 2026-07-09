# §4 Experimental Setup

## 4.1 Models Tested

### Table 4.1: Models Under Test (as of 2026-06-05)

| Model ID | Provider (Access) | Params | Context | Reasoning Support | Official GPQA Diamond | Status |
|---|---|---|---|---|---|---|
| `openai/gpt-oss-120b:free` | OpenRouter | 120B (5B active) | 131K | Yes (low/med/high) | 80.1% | ✅ Tested |
| `nvidia/nemotron-3-nano-30b-a3b:free` | OpenRouter | 30B (3B active) | 1M | Yes | N/A published | ✅ Tested |
| `liquid/lfm-2.5-1.2b-thinking:free` | OpenRouter | 1.2B | 32K | Yes | 37.9% | ✅ Tested |
| `google/gemma-4-31b-it:free` | OpenRouter | 31B | 262K | Yes | **84.3%** (highest!) | ❌ Rate limited (T4) |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter | 550B (55B active) | 1M | Yes | N/A published | ❌ Rate limited (T4) |
| `nvidia/nemotron-3-super-120b-a12b:free` | OpenRouter | 120B (12B active) | 1M | Yes | 79.2% | ❌ Rate limited (T4) |
| `openai/gpt-5` | GitHub Models | ? | ? | Yes | N/A published | 🆕 Available (untested) |
| `openai/gpt-4.1` | GitHub Models | ? | ? | Yes | N/A published | 🆕 Available (untested) |
| `deepseek-ai/deepseek-r1` | Various | 671B (37B active) | 128K | Yes | 71.5% | ⏳ Deferred |

**Note on `gpt-oss-120b`:** Primary model for all comparisons because:
- Highest tested accuracy in our setup (75%)
- Well-documented reasoning behavior
- Free tier available (no cost barrier)
- Reference model in gpt-oss card

## 4.2 Benchmark: GPQA Diamond

### Description
- **Source:** Rein et al. 2023 (arXiv:2311.12022)
- **Task:** 4-option multiple-choice science questions
- **Difficulty:** PhD-level ("Google-proof": untrained non-experts get ~34% with time+search)
- **Domains:** Physics, Chemistry, Biology

### Table 4.2: GPQA Diamond Domain Distribution

| Domain | # Questions | % of Total |
|---|---|---|
| Physics | 86 | 43.4% |
| Chemistry | 93 | 47.0% |
| Biology | 19 | 9.6% |
| **Total** | **198** | 100% |

**Our 20-question subset** (used for rapid iteration):
| Domain | # | % of subset | vs full |
|---|---|---|---|
| Physics | 11 | 55% | ⚠️ over-represented |
| Chemistry | 6 | 30% | under-represented |
| Biology | 3 | 15% | slightly over |

**Implication:** Our 20q results are Physics-biased. Full 198q runs will likely show **lower headline accuracy** because Chemistry is systematically harder (§5.6).

### Question Format
```json
{
  "id": 1,
  "domain": "Physics",
  "subdomain": "Physics (general)",
  "Question": "Two quantum states with energies E1 and E2...",
  "options": {
    "A": "10^-4 eV",
    "B": "10^-9 eV",
    "C": "10^-11 eV",
    "D": "10^-8 eV"
  },
  "correct_answer": "10^-4 eV",
  "correct_answer_letter": "A",
  "Explanation": "According to the uncertainty principle..."
}
```

**Critical schema detail:** `"Question"` uses **capital Q**. Missing this caused Bug B1 (§6.2).

## 4.3 Infrastructure

### 4.3.1 API Key Pool
- **11 OpenRouter accounts** (rotated automatically via `tools/api_key_pool.py`)
- Round-robin with cooldown detection
- Daily-exhaust vs rate-limit distinction
- Persistent stats in `logs/api_key_pool_stats.json`

### 4.3.2 Multi-Provider Registry (documented, not yet unified)
9 free-tier providers documented in `tools/providers.py`:
- Google Gemini (1500 req/day Flash)
- Groq (1000/day/model)
- Cerebras (1M tokens/day)
- NVIDIA NIM
- GitHub Models (only free GPT-5!)
- OpenRouter (current active)
- Cloudflare Workers AI
- Mistral, DeepSeek

**Status:** Registry documented (§4 appendix). Multi-provider pool implementation **deferred** per user request.

### 4.3.3 Response Processing Pipeline
```
Raw API response
        │
        ▼
extract_response_text()  ← merges content + reasoning
        │
        ▼
extract_letter()  ← 16 regex patterns
        │
        ▼
[Valid letter?]
    │       │
   yes      no
    │       │
    │       ▼
    │   ask_for_letter_followup()  ← retry with STOP THINKING prompt
    │       │
    │       ▼
    │   extract_letter() again
    │       │
    ▼       ▼
   Score against ground truth
```

### 4.3.4 Evaluation Script
- Uses evaluate.py in `genesis/tasks/gpqa/data/public/`
- Prefers `answers.json` / `submission.json` over execution logs
- Outputs `evaluation_results.json` with per-question breakdown

## 4.4 Reasoning Effort Settings

### Table 4.3: Reasoning Effort Impact (from gpt-oss card)

| Effort | Official GPQA Diamond | Notes |
|---|---|---|
| `low` | 67.1% | Fast, ~200 reasoning tokens |
| `medium` | 73.1% | Balanced |
| `high` | **80.1%** | Deep, up to 8K reasoning tokens |

**Our default:** `high` (matches ceiling)

**Why not `medium`?** We tested `high` primarily to establish upper bound. Future work could test cost-quality trade-offs (§11).

## 4.5 Sample Size and Statistical Considerations

### Current: 20-question subset
- **Confidence interval (95%):** ±10% absolute (using normal approximation)
- **Sufficient for:** rejecting null "GENESIS = pure baseline" if effect size >20 pts
- **Insufficient for:** claiming small differences (<10 pts)

### Planned: 198-question full run
- **Confidence interval (95%):** ±3.5% absolute
- **Sufficient for:** detecting effect sizes >7 pts
- **Time cost:** ~5-8 hours per model per setup

### Rationale for 20q first
- Free tier bandwidth constraint (50 req/day per key per model)
- Iteration speed (30-40 min vs 5-8 hours)
- Sufficient for hypothesis rejection

## 4.6 Reproducibility

### Environment
```bash
git clone https://github.com/faresrafat3/GENESIS
cd GENESIS
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env
# Fill in your OPENROUTER_API_KEY_* etc.
python tools/api_key_pool.py --test_call  # verify keys
```

### Running Pure Baseline
```bash
python tools/run_multi_model_benchmark.py \
    --models gpt-oss-120b-free \
    --limit 20 \
    --reasoning high \
    --max_tokens 16384 \
    --output_dir results/replicate_baseline
```

### Running GENESIS (post-fix)
```bash
python run_openrouter_benchmark.py \
    --task gpqa --max_gen 2 --run_id 54 \
    --use_evolutionary_discovery \
    --meta_model openai/gpt-oss-120b:free \
    --task_model openai/gpt-oss-120b:free
```

### Data & Code
- Code: `github.com/faresrafat3/GENESIS`
- Raw results: `results/` directory (committed)
- Analysis scripts: `tools/` directory
- Paper source: `paper/` directory

## 4.7 Metrics Definitions

### Primary
- **Accuracy** = correct / total (invalid counts as incorrect)
- **Invalid rate** = invalid / total

### Secondary
- **Recovery rate** = recovered / invalid (from follow-up calls)
- **Empty content rate** = # with `content=""` / total
- **Mean reasoning tokens** (per correctness class)

### Cost/Time
- **Elapsed seconds** (wall clock)
- **Requests per second** (throughput)
- **Requests per correct answer** (efficiency)

### Statistical
- **95% confidence intervals** via Wilson score for proportions
- **Chi-squared tests** for distribution comparisons (used for B1 diagnosis)

## 4.8 Ethical Considerations

- No human subjects
- All models used within their terms of service
- Data (GPQA) is publicly available
- API keys stored locally only (never committed)
- Free tier usage documented and within provider limits

---

**Section status:** 🟡 Solid skeleton. Will expand with pipeline sequence diagram after T1.
