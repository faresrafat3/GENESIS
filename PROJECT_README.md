# 🗺️ PROJECT_README — Master Entry Point

**Last updated:** 2026-06-06 (after Session 13)
**Project owner:** Fares Rafat (F.)
**Project repo:** https://github.com/faresrafat3/GENESIS
**Current paper version:** **v0.7** (`PAPER.md`)
**Current mode:** Theoretical Mode (v2.0 of `PAPER_PROTOCOL.md`)

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
2. `PAPER/notes/HANDOFF.md` (operational current state, 5 open paths)
3. `MASTER_TIMELINE.md` (full chronological story, Sessions 1-13)
4. `PAPER.md` v0.7 (the paper itself)

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

```
GENESIS/
│
├── README.md                                  # Layer A (pre-paper prototype) — DO NOT confuse with paper era
├── PROJECT_README.md                          # ⭐ THIS FILE — master entry point for paper era
├── MASTER_TIMELINE.md                         # ⭐ Full chronological story of all 13 sessions
├── CONTRIBUTION_LEDGER.md                     # ⭐ Single source of truth for attribution
│
├── PAPER.md                                   # The paper itself (v0.7)
├── PAPER_PROTOCOL.md                          # v2.0 — Theoretical Mode rules + §12.2 Attribution Rule
│
├── PAPER/
│   ├── ideas/                                 # Idea lifecycle (INBOX → IN_PROGRESS → INTEGRATED)
│   │   ├── ATTRIBUTION_MAP.md                 # ⭐ central traceability of all contributions
│   │   ├── README.md                          # Ideas Bank explanation
│   │   ├── INBOX.md                           # New ideas from Fares awaiting work
│   │   ├── IN_PROGRESS.md                     # Currently being worked on
│   │   ├── INTEGRATED.md                      # Ideas that have entered the paper
│   │   ├── idea_001_*.md                      # LEAP integration (Session 6)
│   │   └── idea_002_*.md                      # Creative Attribution Rule (Session 7)
│   │
│   ├── theory/                                # Internal theories
│   │   ├── README.md
│   │   ├── 07_pipeline_as_memory_vs_decision_injection.md
│   │   ├── 08_feedback_value_determinism_scope.md
│   │   ├── 09_anticipatory_concepts_vs_lemmas.md
│   │   └── 10_reasoning_saturation.md         # Includes P6 lifetime-drift (added S12b)
│   │
│   ├── philosophy/
│   │   ├── README.md
│   │   └── 07_meaning_of_general_purpose_sufficiency.md   # Includes §9 stable-attractor (added S12b)
│   │
│   ├── figures/                               # Figures 1-12 (fig01-fig12)
│   ├── tables/                                # Tables 1-17 (tab01-tab17)
│   ├── data/                                  # Empirical results (aggregated_results.json + per-run)
│   ├── references/                            # External paper references
│   │
│   └── notes/                                 # Working notes
│       ├── HANDOFF.md                         # ⭐ Operational current state for next session
│       ├── SESSION_LOG.md                     # Chronological log of all sessions
│       ├── INTERNAL_RE_READING_SESSION_12.md  # 12 discoveries from re-reading batch 1+2
│       ├── INTERNAL_RE_READING_SESSION_13.md  # 11 discoveries from re-reading batch 3
│       ├── TODO_HIGH.md / TODO_MEDIUM.md
│       └── OPEN_QUESTIONS.md
│
├── GENESIS_*_AR.md                            # 122 foundational documents (Arabic, pre-paper)
│   ├── GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md     # Scope 5.1-5.94 of external work
│   ├── GENESIS_DeepMind_LEAP_Agentic_Theft_AR.md        # T5.92 (LEAP integration, S7)
│   ├── GENESIS_External_Inverted_U_Wu2025_Theft_AR.md   # T5.93 (S10)
│   ├── GENESIS_External_DTR_ChenMeng2026_Theft_AR.md    # T5.94 (S10)
│   └── ... (118 more foundational theory/spec/memo docs)
│
├── genesis/                                   # Code (DO NOT execute runs without Fares authorization)
│   ├── llm_helpers.py                         # 220 lines, 35 tests
│   ├── orchestrator.py                        # Has ablation modes wired (none/no_pipeline/narrow_feedback/...)
│   └── tasks/
│
├── tools/                                     # API key pool, providers, model registry, multi-model benchmark
├── tasks/gpqa_subset_20/                      # 20-question GPQA subset for fast iteration
├── runs/                                      # Past run artifacts (run_53 to run_58 are referenced)
├── tests/                                     # 463 tests passing
│
└── .env                                       # API keys (NEVER committed; LOCAL ONLY)
```

---

## 4) What's "live" vs "deferred" vs "locked" right now

### LIVE — actively under discussion
| Item | Status |
|---|---|
| `PAPER.md` v0.7 | Latest version (Sessions 12b applied 3 attribution corrections + §8.5.7 Ladder + §8.6 Hidden Crisis Diagnostic) |
| Session 13 discoveries (11 items) | Awaiting Fares decision: Path 1b / Path 1c / Path 2 / Path 3 / Path 4 |
| Internal re-reading exercise (Option F) | Active; 9 of 122 docs read; 23 cumulative discoveries |

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
| Tests passing | 463/463 | local |
| Master Index theft scope | 5.1–5.94 | `GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md` |
| Sessions completed | 1 through 13 | this README + MASTER_TIMELINE |
| Epistemic artifacts produced | **11** (4 theories + 1 philosophy + 4 thefts + 2 ideas) | computed S13 |
| Foundational docs in repo | **122** (9 re-read since S12; 113 remaining in queue) | `ls GENESIS_*.md` |

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
| "What is the project's theoretical name?" | `GENESIS_Meta_Theory_AR.md` §2 → **Tiered Externalized Recursive Intelligence** (NOT yet in paper as of v0.7; pending Path 1c) |
| "What is intelligence in this framework?" | `GENESIS_Meta_Theory_AR.md` §3 → "organized adaptive epistemic control under bounded resources" |
| "What are the 8 grand pillars?" | `GENESIS_Meta_Theory_AR.md` §7 |
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
