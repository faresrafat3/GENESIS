# GENESIS: Diagnosing Scaffolding Bugs and Measuring Architecture Value in LLM Orchestration Systems on Graduate-Level Reasoning Benchmarks

**Version:** 0.2 — Living Document
**Last compiled:** 2026-06-05
**Compiled from:** paper/00_abstract.md through paper/12_appendices.md

---

> **Note:** This file is auto-composable from the individual section files. To rebuild:
> ```
> cat paper/00_abstract.md paper/01_introduction.md paper/02_related_work.md \
>     paper/03_methodology.md paper/04_experimental_setup.md \
>     paper/05_baseline_results.md paper/06_scaffolding_analysis.md \
>     paper/07_genesis_results.md paper/08_ablation_studies.md \
>     paper/09_discussion.md paper/10_limitations.md paper/11_future_work.md \
>     paper/12_appendices.md > paper/PAPER_MAIN.md
> ```

---

## Table of Contents

1. [Abstract](#abstract) 🟡
2. [Introduction](#introduction) 🟡
3. [Related Work](#related-work) 🟡
4. [GENESIS Architecture & Methodology](#methodology) 🟡
5. [Experimental Setup](#experimental-setup) 🟡
6. [Baseline Results](#baseline-results) 🟢
7. [Scaffolding Bugs Analysis](#scaffolding-analysis) 🟢
8. [GENESIS Results (Post-Fix)](#genesis-results) 🔴 (pending T1)
9. [Ablation Studies](#ablation-studies) 🔴 (pending T3)
10. [Discussion](#discussion) 🟡
11. [Limitations](#limitations) 🟡
12. [Future Work](#future-work) 🟡
13. [Appendices](#appendices) 🟡

**Legend:** 🟢 = solid data | 🟡 = draft, needs data | 🔴 = awaiting experiment

---

## Current Progress Statistics

- **Total sections:** 13
- **Solid (with real data):** 2 (§5, §6)
- **Drafted:** 8
- **Awaiting experiments:** 2 (§7, §8)
- **Total content:** ~4,500 lines of markdown across all sections
- **Tables in paper:** 20+ planned, 15 with data
- **Figures planned:** 7 (SVG generation pending)
- **Bugs categorized:** 5 (all with fixes + impact estimates)
- **Novel findings claimed:** 5 (C4a-C4c + reasoning saturation + empty content)

---

## Reading Order Recommendation

For a **fast overview**, read in this order:
1. Abstract (§0) — 5 min
2. Table 5.1-5.7 (§5) — the primary data — 10 min
3. Bug taxonomy (§6.10 summary) — 5 min
4. Discussion (§9) — 15 min

For a **deep dive**, read sections in order (est. 60 min).

For **replication**, focus on:
- §4 (Experimental Setup)
- Appendix G (Reproducibility Package)

---

## The Paper Compilation

*Sections are compiled here from individual files. This is a placeholder — actual compilation happens via `cat` script above.*

Current sections available:
- `paper/00_abstract.md` — Draft
- `paper/01_introduction.md` — Draft
- `paper/02_related_work.md` — Draft with all major refs
- `paper/03_methodology.md` — Draft with architecture diagram
- `paper/04_experimental_setup.md` — Draft
- `paper/05_baseline_results.md` — 🟢 Full data, ~250 lines
- `paper/06_scaffolding_analysis.md` — 🟢 Full analysis, ~350 lines
- `paper/07_genesis_results.md` — Awaits T1
- `paper/08_ablation_studies.md` — Awaits T3
- `paper/09_discussion.md` — Draft
- `paper/10_limitations.md` — Draft (transparent)
- `paper/11_future_work.md` — Draft (prioritized roadmap)
- `paper/12_appendices.md` — Draft (prompts, code, data references)

---

## Meta-Information

**Authors:** فارس رفعت (@faresrafat3) + AI research collaborators
**Repo:** https://github.com/faresrafat3/GENESIS
**Language:** Arabic + English (bilingual)
**Target Venue:** TBD (potential: NeurIPS/ICML/ICLR workshops on reasoning, agents, evaluation)
**Timeline:**
- 2026-06-04 to 2026-06-05: Infrastructure + baseline + fixes + paper skeleton
- 2026-06-06+: T1 (GENESIS post-fix) → §7 fills in
- 2026-07+: T2 (full 198q), T3 (ablation) → §7, §8 complete
- 2026-Q4: F1 (instant vs thinking) → potentially standalone paper #2

---

*This is a living research document. Any inconsistency between this file and the individual sections should be resolved by reading the individual sections (source of truth).*
