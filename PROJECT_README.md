# 🗺️ PROJECT_README — Master Entry Point

**Last updated:** 2026-06-07 (after Session 15 — v0.10 Theory-14 Anti-Antifragility)
**Project owner:** Fares Rafat (F.) — sole author per NeurIPS 2025 policy
**Project repo:** https://github.com/faresrafat3/GENESIS
**Current paper version:** **v0.10** (`PAPER.md`) — Theory-13 Negative Memory integrated as six internal theories (5 + 1 unifying)
**Current mode:** Theoretical Mode (v2.0 of `PAPER_PROTOCOL.md`)
**Last consistency audit:** Session 13.6 — see `AUDIT_REPORT_S13.6.md` for full findings; 3 critical issues fixed in PAPER.md, 11 documentation issues fixed in master docs

> **⚠️ READ THIS FIRST** before touching any file in this repo. This document is the single entry point that tells you:
> - What this project is
> - Where each piece of knowledge lives
> - What rules must be followed
> - Where to start reading depending on your role
> - What is "live" vs "deferred" vs "locked"

---

## 0) What this project is — two layers

### Layer A: The Original GENESIS Prototype (pre-Paper era)
- Lives in: `README.md` (root), `genesis/` code, `tasks/` benchmarks, `runs/`
- Tested two hypotheses: (1) Concept Formation > retrieval-only, (2) Cognitive Economy > stronger-model-only scaling.
- Produced prototype results on synthetic `prototype_v3b_curriculum` tasks.
- **Status:** Foundation work — not the focus of the current paper.

### Layer B: The Paper Project (current focus)
- Lives in: `PAPER.md`, `PAPER/`, `GENESIS_*_AR.md` foundational docs (122 files)
- Tests `gpt-oss-120b` on `GPQA Diamond` (and a 20-question subset for fast iteration).
- Has produced a **5-lens theoretical stack**, **4 external thefts integrated**, and an empirical anchor of **75% pure baseline / 65% GENESIS post-fix / 70% A3 no_pipeline**.
- **This is what active sessions are working on.**

When this README mentions "the paper," it always means Layer B.

---

## 1) The Single Most Important Rule

**No PAPER.md edits without Fares's explicit authorization.**

The agent (working under Fares's delegation) may:
- Read foundational docs
- Propose changes in `PAPER/notes/INTERNAL_RE_READING_SESSION_NN.md` or similar research artifacts
- Write commits with `(pending)` status awaiting authorization

The agent must **NOT** unilaterally:
- Rewrite §12.2 attribution claims
- Add new sections to PAPER.md
- Change locked empirical numbers
- Execute new runs / API calls / benchmarks

The propose → authorize → execute chain has run successfully **twice** (Session 12 → 12b corrections; Sessions 7/9/10/11 additions). See `CONTRIBUTION_LEDGER.md` for the full provenance trail.

---

## 2) Where to start reading — by role

### If you are Fares (returning after time away)
1. This file
2. `PAPER/notes/HANDOFF.md` (operational current state, 6 open paths)
3. `MASTER_TIMELINE.md` (full chronological story, Sessions 1 through 14)
4. `PAPER.md` v0.8.2 (the paper itself)

### If you are a new agent / new session
1. This file
2. `PAPER_PROTOCOL.md` (especially v2.0 Mode Pivot and §12.2 Creative Attribution Rule)
3. `PAPER/notes/HANDOFF.md`
4. `CONTRIBUTION_LEDGER.md` (so you don't misattribute)
5. `MASTER_TIMELINE.md` (so you understand the history)
6. `PAPER/notes/SESSION_LOG.md` (raw chronological log)

### If you are a researcher / reviewer (external)
1. This file
2. `PAPER.md` v0.7 (especially §12.2 Author Contributions + §14 Ethics)
3. `PAPER/ideas/ATTRIBUTION_MAP.md`
4. `GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md` (scope 5.1–5.94 of external work integrated)

### If you are a future maintainer (post-paper)
1. This file
2. `MASTER_TIMELINE.md`
3. `CONTRIBUTION_LEDGER.md`
4. `PAPER_PROTOCOL.md`

---

## 3) File map — where each piece of knowledge lives

This map is **complete** as of Session 13.6 audit. Every file/directory at the repo root is listed. If you add a new file at the root, update this map.

```
GENESIS/                                       # repo root
│
│ ─── 📚 MASTER NAVIGATION DOCS (read these first) ────────────────
│
├── PROJECT_README.md                          # ⭐ THIS FILE — master entry point for paper era
├── AGENT_OPERATING_MANUAL.md                  # ⭐ NEW S13.7 — how to work on this project safely (REQUIRED for new agents)
├── MASTER_TIMELINE.md                         # ⭐ Full chronological story Sessions 1 → 13.7
├── CONTRIBUTION_LEDGER.md                     # ⭐ Single source of truth for attribution
├── AUDIT_REPORT_S13.6.md                      # Consistency audit findings (Session 13.6)
├── CLEANUP_INVENTORY_S13.7.md                 # ⭐ NEW S13.7 — inventory of old/redundant files awaiting Fares decision
│
│ ─── 📄 PAPER ARTIFACTS ──────────────────────────────────────────
│
├── PAPER.md                                   # The paper itself (v0.7, sole author: F. per §12.1)
├── PAPER_PROTOCOL.md                          # v2.0 — Theoretical Mode rules + §12.2 Attribution Rule
│
│ ─── 📖 LAYER A (pre-paper) DOCS ─────────────────────────────────
│
├── README.md                                  # Layer A prototype docs — predates paper era
├── SETUP_AND_RUN_GUIDE.md                     # Layer A — operational setup guide for prototype
├── API_GENESIS_Design_Arabic.md               # Layer A — original system design (Arabic)
├── QUICK_RUN_20Q_GUIDE_AR.md                  # Operational guide for 20-question subset runs
├── STRATEGIC_DEVELOPMENT_PLAN_2026_06.md      # Layer A — strategic plan (pre-paper)
├── STRATEGIC_DEVELOPMENT_PLAN_2026_06_v2.md   # Layer A — strategic plan v2 (pre-paper)
│
│ ─── 🗂️ FOUNDATIONAL THEORY DOCS (122 .md files at root) ─────────
│
├── GENESIS_*_AR.md                            # 122 Arabic foundational documents (pre-paper)
│   │
│   │ Master index of external work:
│   ├── GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md   # Scope 5.1–5.94 + classical 6.1–6.13
│   │
│   │ Theft memos (external papers integrated):
│   ├── GENESIS_DeepMind_LEAP_Agentic_Theft_AR.md      # T5.92 LEAP (Session 7)
│   ├── GENESIS_External_Inverted_U_Wu2025_Theft_AR.md # T5.93 Wu et al. (Session 10)
│   ├── GENESIS_External_DTR_ChenMeng2026_Theft_AR.md  # T5.94 Chen et al. (Session 10)
│   ├── GENESIS_DeepMind_AlphaEvolve_FunSearch_Theft_AR.md  # T5.86
│   ├── GENESIS_DeepMind_CoScientist_Theft_AR.md           # T5.85
│   ├── GENESIS_DeepMind_Aletheia_Theft_AR.md              # T5.84
│   │
│   │ The 9 foundational theory docs read in Sessions 12 + 13 (priority docs):
│   ├── GENESIS_Cognitive_Economy_Theory_AR.md         # ← Theory-08 + Theory-10 originator (S12)
│   ├── GENESIS_Concept_Formation_Theory_AR.md         # ← Ladder of Abstraction §4 (S12)
│   ├── GENESIS_Tiered_Intelligence_AR.md              # ← Phil-07 originator (S12)
│   ├── GENESIS_Productive_Forgetting_Theory_AR.md     # ← Theory-10 P6 contributor (S12)
│   ├── GENESIS_Anomaly_Crisis_Paradigm_Theory_AR.md   # ← §8.6 Hidden Crisis Diagnostic + Phil-07 attractor (S12)
│   ├── GENESIS_Self_Benchmarking_Theory_AR.md         # ← 3-tier Value framework (S13)
│   ├── GENESIS_Meta_Theory_AR.md                      # ← 8-pillar unifying frame "Tiered Externalized Recursive Intelligence" (S13) — biggest single doc
│   ├── GENESIS_Contradiction_Theory_AR.md             # ← Indicators D+G dependency (S13)
│   ├── GENESIS_Agent_Identity_Theory_AR.md            # ← §14.4 resolution + Identity Drift (S13)
│   │
│   └── ... (113 more foundational docs not yet re-read; queue in HANDOFF.md)
│
│ ─── 📑 PAPER PRODUCTION DIRECTORY ───────────────────────────────
│
├── PAPER/
│   │
│   ├── ideas/                                 # Idea lifecycle (INBOX → IN_PROGRESS → INTEGRATED)
│   │   ├── ATTRIBUTION_MAP.md                 # ⭐ session-by-session attribution tracker (operational)
│   │   ├── README.md                          # Ideas Bank explanation
│   │   ├── INBOX.md                           # New ideas from Fares awaiting work (currently empty)
│   │   ├── IN_PROGRESS.md                     # Currently being worked on
│   │   ├── INTEGRATED.md                      # Ideas that have entered the paper
│   │   ├── idea_001_leap_agentic_framework_for_formal_math.md
│   │   └── idea_002_creative_attribution_rule.md
│   │
│   ├── theory/                                # 5 internal theory files + README
│   │   ├── README.md
│   │   ├── 07_pipeline_as_memory_vs_decision_injection.md
│   │   ├── 08_feedback_value_determinism_scope.md
│   │   ├── 09_anticipatory_concepts_vs_lemmas.md
│   │   ├── 10_reasoning_saturation.md         # Includes P6 lifetime-drift (added S12b)
│   │   └── 13_negative_memory.md              # ⭐ NEW S14 — Negative Memory as Epistemic Safety Net
│   │
│   ├── philosophy/                            # 1 philosophy file + README
│   │   ├── README.md
│   │   └── 07_meaning_of_general_purpose_sufficiency.md   # Includes §9 stable-attractor (added S12b)
│   │
│   ├── figures/                               # 12 figures + README (fig01-fig12)
│   │   ├── README.md
│   │   ├── fig01_pipeline_overview.md         through fig10_ablation_decision_tree.md (existing)
│   │   ├── fig11_110_point_gap.md             # Added S7-8 (LEAP integration)
│   │   └── fig12_feedback_quadrant.md         # Added S7-8 (Theory-08)
│   │
│   ├── tables/                                # 8 table files + README (NOT 17 as some docs claimed)
│   │   ├── README.md
│   │   ├── tab04_per_question_results.md
│   │   ├── tab11_run57_comparison.md
│   │   ├── tab12_question_delta_analysis.md
│   │   ├── tab13_ablation_matrix.md
│   │   ├── tab14_a3_no_pipeline_results.md
│   │   ├── tab15_a7_design.md
│   │   ├── tab16_leap_vs_genesis.md           # Added S7-8 (LEAP integration)
│   │   └── tab17_feedback_value_matrix.md     # Added S7-8 (Theory-08)
│   │   # Note: tables 1-3, 5-10 are referenced inline in PAPER.md sections without dedicated files
│   │
│   ├── data/                                  # Empirical results
│   │   ├── aggregated_results.json
│   │   ├── run57_genesis_postfix_20q.json
│   │   └── run58_a3_no_pipeline_20q.json
│   │
│   ├── references/                            # External paper references
│   │
│   └── notes/                                 # Working notes
│       ├── HANDOFF.md                         # ⭐ Operational current state for next session
│       ├── SESSION_LOG.md                     # Chronological log Sessions 1 → 13.6
│       ├── INTERNAL_RE_READING_SESSION_12.md  # 12 discoveries from re-reading batch 1+2
│       ├── INTERNAL_RE_READING_SESSION_13.md  # 11 discoveries from re-reading batch 3
│       ├── TODO_HIGH.md
│       ├── TODO_MEDIUM.md
│       └── OPEN_QUESTIONS.md
│
│ ─── 💻 CODE ─────────────────────────────────────────────────────
│
├── genesis/                                   # Core code (DO NOT execute runs without F. authorization)
│   ├── llm_helpers.py                         # 220 lines, 35 tests (Bug #6 fixed)
│   ├── orchestrator.py                        # Ablation modes wired: none / no_pipeline / narrow_feedback / no_pipeline+narrow_feedback
│   └── tasks/                                 # includes longcot-chess (NOT agent work — see §7)
│
├── tools/                                     # API key pool, providers, model registry, multi-model benchmark
│   ├── api_key_pool.py
│   ├── providers.py                           # 9 providers documented
│   ├── model_registry.py                      # 13 models
│   └── run_multi_model_benchmark.py
│
├── virtual_genesis/                           # Layer A prototype code (api, core, eval, persistence, runtime)
│   └── (organized into 5 subdirs + __init__.py)
│
├── tasks/                                     # Benchmark task definitions
│   └── gpqa_subset_20/                        # 20-question GPQA subset for fast iteration
│
├── tests/                                     # 463 tests passing
│
├── scripts/                                   # Utility scripts (Layer A operational helpers)
│
├── runs/                                      # Past run artifacts (run_53 to run_58 referenced in paper)
│
├── results/                                   # Layer A ablation/comparison results (pre-paper)
│
│ ─── 🔧 ROOT-LEVEL CONFIG & SCRIPTS ──────────────────────────────
│
├── pyproject.toml                             # Python project config
├── run_openrouter_benchmark.py                # OpenRouter benchmark entry script
├── test_pioneer.py                            # Test utility
├── push_runs.sh                               # ⚠️ File-permission diff only — NOT agent work
│
│ ─── 🔒 NEVER COMMITTED ──────────────────────────────────────────
│
└── .env                                       # API keys (LOCAL ONLY; NEVER committed)
```

### Two-layer distinction summary

The repo contains **two distinct project layers** that should not be confused:

| Layer | Era | Primary docs | Key files |
|---|---|---|---|
| **Layer A** (pre-paper prototype) | Before Session 1 of paper era | `README.md`, `SETUP_AND_RUN_GUIDE.md`, `API_GENESIS_Design_Arabic.md`, `STRATEGIC_DEVELOPMENT_PLAN_*.md` | `virtual_genesis/`, `results/`, `scripts/` |
| **Layer B** (paper era — current focus) | Sessions 1 through 13.6 | `PAPER.md`, `PROJECT_README.md`, `MASTER_TIMELINE.md`, `CONTRIBUTION_LEDGER.md`, all of `PAPER/` | `genesis/`, `tools/`, `tasks/gpqa_subset_20/`, `runs/`, `tests/` |

**All paper-era sessions document Layer B.** Layer A is preserved for context but not actively edited.

---

## 4) What's "live" vs "deferred" vs "locked" right now

### LIVE — actively under discussion
| Item | Status |
|---|---|
| `PAPER.md` v0.9 | Latest version (S14: §15 TERI Frame + §14 Ethics + §15 sharpened + Theory-13 Negative Memory — six internal theories (5 + 1 unifying)) |
| Re-reading exercise | Active; 14 of 122 docs read; 37 cumulative discoveries from S12-S14 |
| Session 14 complete | 7 commits, 3 paper version bumps (v0.7→v0.8→v0.8.1→v0.8.2) |

### DEFERRED — infrastructure ready, execution paused
| Item | Status |
|---|---|
| A7a `narrow_feedback` ablation | Code wired in `genesis/orchestrator.py`, NOT executed (Theoretical Mode) |
| A7b `no_pipeline+narrow_feedback` ablation | Same — wired, not executed |
| A7c `--max_gen 1` ablation | Same |
| Future Work Track A.1-A.5 | All theoretical; awaiting end of Theoretical Mode |
| New runs / benchmarks | All paused per Session 6 Mode Pivot |

### LOCKED — do not change without new run + Fares authorization
| Metric | Value | Source |
|---|---|---|
| gpt-oss-120b GPQA-Diamond official | 80.1% | NVIDIA model card |
| Pure baseline (n=20) | **75.00%** | run_57 |
| GENESIS pre-fix (n=198) | 30.30% | run_53 (buggy) |
| GENESIS post-fix Gen1 / Gen2 | 65.00% / 65.00% | run_57 |
| A3 no_pipeline Gen1 / Gen2 | **70.00%** / 60.00% | run_58 |
| LEAP Putnam 2025 | 0% → **100%** (+100) | T5.92 |
| LEAP vs GENESIS gap | **110 points** | computed |
| Reasoning saturation median tokens | 989 (correct) vs 6,836 (incorrect) | run_57 |
| Empty content rate | 35% (7/20) | run_57 (all in incorrect set) |
| T5.94 length-vs-accuracy correlation | r = −0.54 | Chen et al. on GPT-OSS + GPQA |
| Tests passing | 663/663 | local |
| Master Index theft scope | 5.1–5.94 | `GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md` |
| Sessions completed | 1 through 14 (7 S14 sub-phases, 13 numbered + 12b + 13.5 + 13.6 + 13.7 + 13.8 + 13.9 + 14) | this README + MASTER_TIMELINE |
| Epistemic artifacts produced | **12** (5 theories + 1 philosophy + 4 thefts + 2 ideas) | computed S14 |
| Foundational docs in repo | **122** (14 re-read since S12; 108 remaining in queue) | `ls GENESIS_*.md` |

---

## 5) The two governance rules that shape everything

### Rule 1 — Mode Pivot (Session 6, verbatim from Fares)
> *"هنعمل اسكيب لمواضيع التشغيل، احنا هنضبطها على الورقة وفلسفياً ونظرياً المشروع بالكامل بالأفكار اللي لسه هتجي."*

**Translation:** Skip operational topics. Focus on paper, philosophy, theory, and ideas yet to come.

**Practical consequence:** No new runs, no API calls, no benchmark execution. All work is reading, writing, theorizing.

### Rule 2 — Creative Attribution Rule (Session 7, Idea-002, verbatim from Fares)
> *"تمام خلي بالك اضافه السرقه الشرعيه القويه دي كفكره مني فلو عندك حاجات زي كده ابداعيه باي شكل اعملها تمام ونعم اشتغل"*

**Translation:** Every Fares contribution (even a paper link) must be attributed as `Idea-NNN` with a full file + ATTRIBUTION_MAP entry + paper citation tag. Every agent-initiated work must be labelled separately in `PAPER.md` Appendix D §D.2 + ATTRIBUTION_MAP "Agent-Initiated Synthesis" section.

**Practical consequence:** The three-layer authorship structure in `PAPER.md` §12.2. Session 12's re-reading exercise found that 3 of 5 theory/philosophy artifacts had been MIS-attributed as agent-initiated when they had Fares-originated precursors. Session 12b corrected them.

**This rule is the safety net that makes the whole project ethically defensible.** See `CONTRIBUTION_LEDGER.md` for how it operates.

---

## 6) Delegation pattern — the "القرار قرارك" chain

Fares does not micromanage. He delegates direction at decision points. The pattern is:
1. Fares states a strategic frame (e.g., Mode Pivot, Idea-001)
2. Agent proposes options
3. Fares says one of: `"القرار قرارك"` / `"القرار عندك"` / `"نعم اشتغل"` / `"تمام"` / etc.
4. Agent selects the highest-leverage option from the offered set
5. Agent executes
6. Agent documents in HANDOFF + SESSION_LOG + ATTRIBUTION_MAP
7. Next session: Fares reviews the work and either delegates again or redirects

This pattern has run **7 times** to date (Sessions 8, 9, 10, 11, 12, 12b, 13). Every utterance is preserved verbatim in `PAPER.md` §12.3 + `CONTRIBUTION_LEDGER.md`.

**Critical:** "تمام" by itself does NOT authorize new paper edits. It authorizes the agent's *previously-recommended path*. If you're an agent reading this, look at the immediately-preceding HANDOFF or session-end message to see what "تمام" applies to.

---

## 7) Excluded from agent work (do NOT touch)

These files have appeared in `git status` as modified in past sessions but are NOT agent work:
- `genesis/tasks/longcot-chess/data/public/evaluate.py` (file permission diff only)
- `genesis/tasks/longcot-chess/reference/reference_target_agent.py` (same)
- `push_runs.sh` (same)

**Never include these in `git add`.** They are excluded by every agent commit. The pattern is to use explicit `git add` of specific paths, never `git add -A` or `git add .`.

---

## 8) Security — credentials handling

- API keys for OpenRouter (11), Gemini (5 working), GitHub PAT (for gpt-5/4.1/4o/DeepSeek-R1/Phi-4): all in **local `.env` only**.
- Before every push: `git diff HEAD | grep -E "sk-or-v1-|sk-proj-|gsk_|csk-|AIzaSy|github_pat_|nvapi-|ghp_|nvapi-"` must return empty.
- The GitHub PAT for pushing (`github_pat_11BTHFWII0t...`) is used inline in `git push` commands only; never committed to any file in the repo.

---

## 9) Where to find specific answers

| Question | Document |
|---|---|
| "What is the project's theoretical name?" | PAPER.md §15 → **Tiered Externalized Recursive Intelligence** (placed S14, from `GENESIS_Meta_Theory_AR.md` §2) |
| "What is intelligence in this framework?" | PAPER.md §15.1 → "organized adaptive epistemic control under bounded resources" |
| "What are the 8 grand pillars?" | PAPER.md §15.2 |
| "How many internal theories?" | 5: Theory-07, Theory-08, Theory-09, Theory-10, Theory-13 (Negative Memory, added v0.9) |
| "What did Fares say in Session N?" | `PAPER/notes/SESSION_LOG.md` + `PAPER.md` §12.3 |
| "Why is Theory-10 attributed the way it is?" | `CONTRIBUTION_LEDGER.md` + `PAPER.md` §12.2 Layer 1+2 + `PAPER/notes/INTERNAL_RE_READING_SESSION_12.md` |
| "What are the pending decisions?" | `PAPER/notes/HANDOFF.md` "Next" section |
| "What was decided in Session N?" | `MASTER_TIMELINE.md` Session N entry |
| "Why is §14.4 a partially open question?" | `PAPER.md` §14.4 + `PAPER/notes/INTERNAL_RE_READING_SESSION_13.md` GEM 22 (proposes resolution via Agent Identity Theory §12) |

---

## 10) Final note for whoever picks this up next

This project's distinguishing feature is **transparency about its own production process**. Most papers hide their methodology of being written. This one documents it — sometimes more thoroughly than it documents its scientific content.

That is intentional. The Creative Attribution Rule (Idea-002) makes it a research integrity question. The Author Contributions section (§12.2) makes it a venue-compliance question. The Internal Re-Reading exercise (option F, Sessions 12+13) is what catches the cases where the documentation has gone wrong.

If you're new and confused: read `MASTER_TIMELINE.md` first. The story makes sense when you see it in order.

If you're Fares: welcome back. `PAPER/notes/HANDOFF.md` has the next 5 paths.

If you're an agent: read this file, then `PAPER_PROTOCOL.md`, then `CONTRIBUTION_LEDGER.md`, then `PAPER/notes/HANDOFF.md`. Do nothing to the paper until you've read all four.
