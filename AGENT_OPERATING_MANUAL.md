# 🤖 AGENT_OPERATING_MANUAL — How to Work on This Project Without Damaging It

**Version:** 1.0
**Last updated:** 2026-06-06 (Session 13.7)
**Audience:** Any LLM agent (Claude, GPT, Gemini, Grok, Qwen, etc.) assigned to work on the GENESIS project
**Authority:** This manual encodes the working rules that emerged from Sessions 1–13.7. Following it preserves project quality, performance, and integrity.

> **⚠️ READ THIS BEFORE TOUCHING ANYTHING.** Past agents have made mistakes that took entire sessions to detect and fix (see `AUDIT_REPORT_S13.6.md`). This manual is designed to prevent the next agent from making the same mistakes.

---

## 0) The 60-second project summary

You are working on **GENESIS** — a research paper documenting whether LLM orchestration architectures genuinely improve graduate-level scientific reasoning. The paper (`PAPER.md`, currently v0.7) is the *primary product*. Everything else exists to support it.

The project owner is **Fares Rafat** (referred to as **F.** in formal docs). You are the **Agent** (referred to as **A.**). **F. is the sole author. You are NOT a co-author.** Your contributions are documented transparently in `PAPER.md` §12.2 under a three-layer structure, but you have zero authorial credit. This is intentional and enforces NeurIPS 2025 LLM policy.

The project has been in **Theoretical Mode** since Session 6 (Mode Pivot). No new runs, API calls, or benchmark execution unless F. *explicitly* requests them.

---

## 1) The 8 Non-Negotiable Rules

These are not preferences. They are **hard constraints**. Violating any of them creates work for the next agent and erodes project integrity.

### Rule 1 — Read before writing
**Before any action**, read in this order:
1. `PROJECT_README.md` (5 min) — master entry point
2. `PAPER_PROTOCOL.md` (10 min) — working rules v2.0
3. `PAPER/notes/HANDOFF.md` (5 min) — current operational state
4. `CONTRIBUTION_LEDGER.md` (10 min) — attribution source of truth
5. `MASTER_TIMELINE.md` (15 min) — full history if you need context

Total: ~45 minutes. **Do this every single new session.** No exceptions.

### Rule 2 — Propose, don't unilaterally execute
For any change to `PAPER.md`, `PAPER/theory/*.md`, `PAPER/philosophy/*.md`, `PAPER/ideas/*.md`, or master docs at root:
1. **Propose** the change in a research artifact (e.g., `PAPER/notes/INTERNAL_RE_READING_SESSION_NN.md` or similar)
2. **Wait** for explicit F. authorization (a "تمام" / "نعم اشتغل" / "القرار قرارك" / similar utterance)
3. **Only then execute** the change in a real edit

**Exception (very narrow):** Active misrepresentations that violate research integrity (e.g., the v0.2-vs-v0.7 contradiction in PAPER.md header found in S13.6) may be fixed immediately under the §14 dual-honesty principle, **with explicit documentation in commit message and AUDIT_REPORT explaining why**.

If unsure whether something is "active misrepresentation" vs "addition" → **always treat as addition** (requires authorization).

### Rule 3 — Theoretical Mode is the default
Since Session 6 Mode Pivot, the project is in Theoretical Mode:
- ❌ NO new benchmark runs
- ❌ NO new API calls (for benchmarking purposes)
- ❌ NO new ablation execution
- ❌ NO proposing operational work as a priority
- ✅ Reading, theorizing, integrating literature, writing paper sections

To exit Theoretical Mode, F. must say so explicitly. Until then, all your work is paper-craft.

### Rule 4 — Attribution is sacred (Idea-002 Creative Attribution Rule)
**Every contribution F. makes must be traceable.** Even a paper link he shares is `Idea-NNN` with a full file + ATTRIBUTION_MAP entry + CONTRIBUTION_LEDGER row + paper citation tag.

**Every agent-initiated work must be labeled separately** in `PAPER.md` Appendix D §D.2 + `ATTRIBUTION_MAP.md` "Agent-Initiated Synthesis" section + CONTRIBUTION_LEDGER §1-5.

**If you ever formalize something from F.'s existing docs:** check CONTRIBUTION_LEDGER §1-2 to see if F. originated the idea. **If yes, attribute as "agent-formalized, Fares-originated" not as "agent-initiated".** Session 12 found 3 cases where this rule had been violated; do not add a 4th.

### Rule 5 — Preserve verbatim Arabic utterances exactly
When F. authorizes work via Arabic utterance, preserve it **letter-for-letter** in:
- `CONTRIBUTION_LEDGER.md` §6 (chain of authorizations)
- `PAPER.md` §12.3 (Verbatim Authorization Log)
- Commit messages
- Session log entry

Do NOT translate, paraphrase, or "clean up" Egyptian Arabic. Preserve as Fares typed it.

### Rule 6 — Never `git add -A` or `git add .`
These files appear modified in `git status` but are **NOT agent work**:
- `genesis/tasks/longcot-chess/data/public/evaluate.py` (file-permission diff)
- `genesis/tasks/longcot-chess/reference/reference_target_agent.py` (file-permission diff)
- `push_runs.sh` (file-permission diff)

Always use explicit `git add PATH1 PATH2 PATH3`. Never add everything blindly.

### Rule 7 — Security scan before every push
Before `git push`, run:
```bash
git diff HEAD | grep -E "sk-or-v1-|sk-proj-|gsk_|csk-|AIzaSy|github_pat_|nvapi-|ghp_"
```
Must return empty (excluding occurrences of the *patterns themselves* in documentation, which is fine — they're rules, not credentials). API keys live in `.env` (gitignored) only.

### Rule 8 — Update the documentation chain after every session
At the end of each session, update:
1. `PAPER/notes/HANDOFF.md` — current state + open paths
2. `PAPER/notes/SESSION_LOG.md` — verbose entry for this session
3. `PAPER/ideas/ATTRIBUTION_MAP.md` — new row if agent-initiated work happened
4. `CONTRIBUTION_LEDGER.md` — new authorization utterance in §6 + new attribution rows in §1-7 + run §9 consistency check
5. `MASTER_TIMELINE.md` — new session entry + quick reference table row
6. `PROJECT_README.md` "Last updated" line + any changed counts

If these get out of sync, the next agent operates on a corrupt model of the project.

---

## 2) The delegation pattern — how F. communicates

F. uses a specific delegation pattern. Recognize it:

| F. says | Means | Your response |
|---|---|---|
| `"القرار قرارك"` / `"القرار عندك"` | "Decision is yours — pick the highest-leverage thing from what you've offered" | Select the top recommendation from your most recent HANDOFF options; execute; document |
| `"نعم اشتغل"` / `"تمام اشتغل"` | "Yes, execute the previously-proposed work" | Execute exactly what was just proposed |
| `"تمام"` | "Continue / proceed / OK" | Usually authorizes the most-recent proposal. **If ambiguous, ask for clarification.** |
| `"جميل"` | "Good" — implicit approval | Often paired with delegation; treat similarly |
| A link to a paper or an idea | New Idea-NNN incoming | Create `PAPER/ideas/idea_NNN_*.md` file, add to ATTRIBUTION_MAP, integrate per Idea-002 rule |
| A direct instruction in Arabic | Direct order | Execute literally; preserve verbatim quote |
| `"وقف"` / `"خلاص"` / `"بطل"` | "Stop / halt the current work" | Stop immediately, document the stop in HANDOFF |

**Critical:** "تمام" by itself does NOT authorize *new* paper content. It authorizes the most-recent specific *proposal*. If you've offered 5 paths and F. says "تمام", that's authorization for your **top-recommended path** (the one you marked ⭐ TOP PICK), not all 5.

---

## 3) The two-layer project structure

The repo contains two distinct projects. Do not confuse them:

| Layer | Era | Status | Files |
|---|---|---|---|
| **Layer A** (pre-paper prototype) | Before Session 1 | Frozen / archived candidate | `README.md`, `virtual_genesis/`, `SETUP_AND_RUN_GUIDE.md`, `STRATEGIC_DEVELOPMENT_PLAN_*.md`, ~90 of the 122 `GENESIS_*_AR.md` files |
| **Layer B** (paper era — current) | Sessions 1–present | Active | `PAPER.md`, `PROJECT_README.md`, `MASTER_TIMELINE.md`, `CONTRIBUTION_LEDGER.md`, all `PAPER/`, `genesis/`, `tools/`, paper-relevant `tasks/`, `runs/run_53/` |

**You work on Layer B.** Layer A is preserved for context. Do NOT modify Layer A files unless F. specifically asks.

See `CLEANUP_INVENTORY_S13.7.md` for the full mapping of which files are Layer A vs Layer B.

---

## 4) The 5 epistemic artifacts you may produce

Per Meta-Theory §9, every cognitive contribution should be an **epistemic artifact** with 5 properties. When you produce new content, mentally check it has these:

| Property | Question |
|---|---|
| **Memory value** | Does it preserve something worth remembering? |
| **Decision value** | Does it inform a future decision? |
| **Reuse value** | Will it be cited/referenced later? |
| **Explanatory value** | Does it explain a phenomenon or answer a question? |
| **Test value** | Does it generate or sharpen testable claims? |

If a piece of work doesn't have at least 3 of these, ask whether it should exist.

---

## 5) Locked numbers — never change without new run + F. authorization

These empirical anchors are **immutable** without new measurements F. has authorized:

| Number | Value | Source |
|---|---|---|
| gpt-oss-120b GPQA Diamond official | 80.1% | NVIDIA model card |
| Pure baseline (n=20) | 75.00% | run_57 |
| GENESIS pre-fix (n=198) | 30.30% | run_53 (buggy) |
| GENESIS post-fix Gen1 / Gen2 | 65.00% / 65.00% | run_57 |
| A3 no_pipeline Gen1 / Gen2 | 70.00% / 60.00% | run_58 |
| LEAP Putnam 2025 | 0% → 100% (+100) | T5.92 |
| LEAP vs GENESIS gap | 110 points | computed |
| Reasoning saturation median tokens | 989 (correct) vs 6,836 (incorrect) | run_57 |
| Empty content rate | 35% (7/20) | run_57 |
| T5.94 length-vs-accuracy r | −0.54 | Chen et al. on GPT-OSS + GPQA |
| Tests | 463/463 passing | local |
| Master Index theft scope | 5.1–5.94 | `GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md` |
| Epistemic artifacts produced | 11 | 4 theories + 1 phil + 4 thefts + 2 ideas |
| Foundational docs in repo | 122 (9 priority re-read) | `ls GENESIS_*_AR.md` |
| Sessions completed | 1 through 13.7 | this manual + MASTER_TIMELINE |

If you find yourself wanting to change one of these numbers → **STOP** and check with F.

---

## 6) The 3 governance rules summarized

These come from the project history. Internalize them.

### Rule G1 — Mode Pivot (Session 6, verbatim from F.)
> *"هنعمل اسكيب لمواضيع التشغيل، احنا هنضبطها على الورقة وفلسفياً ونظرياً المشروع بالكامل بالأفكار اللي لسه هتجي."*

**Operational:** No runs. Theory + philosophy + paper depth + ideas only.

### Rule G2 — Creative Attribution (Idea-002, Session 7, verbatim from F.)
> *"تمام خلي بالك اضافه السرقه الشرعيه القويه دي كفكره مني فلو عندك حاجات زي كده ابداعيه باي شكل اعملها تمام ونعم اشتغل"*

**Operational:** Every F. contribution traced. Every agent-initiated work labeled. See Rule 4 above.

### Rule G3 — Documentation Honesty (Session 13.5 + S13.6)
The 3 master docs (PROJECT_README, MASTER_TIMELINE, CONTRIBUTION_LEDGER) + AUDIT_REPORT must stay consistent. The 18 mechanical consistency checks in CONTRIBUTION_LEDGER §9 must all be GREEN.

**Operational:** Update all 5 documentation files at end of every session (Rule 8 above).

---

## 7) What to do when F. gives you a new idea (Idea-NNN flow)

F. shares a paper link, observation, question, or insight → you follow this exact flow:

### Step 1: Create the Idea file (within 5 minutes of receiving)
File: `PAPER/ideas/idea_NNN_short_name.md`
Contents:
- Verbatim F. utterance/link (exact characters)
- Date received
- Layer assignment (always Layer 1 since F. originated)
- Initial impression (what kind of artifact will this become?)

### Step 2: Add row to `PAPER/ideas/ATTRIBUTION_MAP.md`
Status: `Received` → later `In Progress` → later `Integrated`

### Step 3: Add row to `CONTRIBUTION_LEDGER.md` §3 (Ideas)
Full provenance per template

### Step 4: Move to `INBOX.md` → `IN_PROGRESS.md` as you work

### Step 5: Integrate per F. authorization
- If F. says "نعم اشتغل" → execute integration into paper
- Otherwise wait

### Step 6: When integrated, document outputs
- Update `INTEGRATED.md`
- Add paper section + theory/philosophy files as appropriate
- Update `PAPER.md` §12.2 if structural impact

### Step 7: Update master docs
- HANDOFF, SESSION_LOG, MASTER_TIMELINE per Rule 8

**Example trace:** Idea-001 (LEAP) went from F.'s Session 6 link to: T5.92 theft + Theory-07/08/09 + Phil-07 + §8.5 with 7 sub-sections + Tables 16-17 + Figures 11-12 + Future Work Tracks A-E. **Every step is traceable** in CONTRIBUTION_LEDGER.

---

## 8) How to extend or expand the paper

If F. authorizes a substantive paper addition:

### Pre-flight
- [ ] Locked numbers untouched
- [ ] No agent co-authorship implied anywhere
- [ ] Three-layer attribution clear for new content
- [ ] If new theory/philosophy → check CONTRIBUTION_LEDGER §1-2 for F. precursors first
- [ ] If new theft → add row to Master Index (5.NN) + create theft memo

### During edit
- Update `PAPER.md` semver per `PAPER_PROTOCOL.md` §7:
  - **Major version bump (v0.7 → v1.0):** new section added, big result change, major theory
  - **Minor version bump (v0.7 → v0.8):** new figure/table/idea/theory
  - **Patch version bump (v0.7 → v0.7.1):** small edits, citation additions, error fixes
- Update header version + footer version simultaneously (S13.6 audit found drift)
- Update §12.2 if new contribution layer

### Post-flight
- Run the 18 CONTRIBUTION_LEDGER §9 consistency checks
- Update all 5 docs per Rule 8
- Security scan, explicit `git add`, commit with full message, push

---

## 9) How to handle ambiguity

When F.'s instruction is ambiguous:

### Option A: Ask for clarification
Use the question-tool. Offer 3-5 specific options + agent recommendation. Wait for response.

### Option B: Make the conservative choice and document it
If the ambiguous instruction is low-risk and obviously aligned with project direction, you may proceed *as long as you*:
1. State explicitly in commit message what interpretation you chose and why
2. Note in HANDOFF that F. can revert if interpretation was wrong
3. Mark the work as "interpretive — pending Fares review"

**Default to Option A** unless time pressure is real and risk is low.

---

## 10) How to handle conflicts between docs

If two docs in the project disagree, **resolution rules from PROJECT_README + AUDIT_REPORT S13.6:**

| Question about... | Authoritative doc |
|---|---|
| Attribution / who did what | `CONTRIBUTION_LEDGER.md` |
| What happened in session N | `MASTER_TIMELINE.md` |
| Where to find file X | `PROJECT_README.md` |
| Scientific claim in paper | `PAPER.md` itself (header must match footer per S13.6 C1) |
| Working rules | `PAPER_PROTOCOL.md` |
| Open paths | `PAPER/notes/HANDOFF.md` |
| Cleanup state | `CLEANUP_INVENTORY_S13.7.md` |

If you find disagreement: **document it in your next commit + update both files to match the authoritative one + note in AUDIT_REPORT.**

---

## 11) How to do a session well — checklist

### Start of session
- [ ] Read PROJECT_README + HANDOFF + CONTRIBUTION_LEDGER §9
- [ ] Identify F.'s latest utterance + intent
- [ ] Identify which "Path" from HANDOFF is being authorized (if any)
- [ ] State your interpretation back to F. before executing (if any doubt)

### During session
- [ ] Stay in Theoretical Mode unless F. explicitly authorizes otherwise
- [ ] Update notes file for major activity as you work
- [ ] Check CONTRIBUTION_LEDGER §1-2 if formalizing anything from F.'s foundational docs
- [ ] Preserve verbatim Arabic utterances

### End of session
- [ ] Update all 5 documentation files (Rule 8)
- [ ] Run 18 CONTRIBUTION_LEDGER §9 checks; report any failures
- [ ] Security scan
- [ ] Explicit `git add` (never `-A`)
- [ ] Comprehensive commit message including: what was done, why, files touched, what's pending
- [ ] Push
- [ ] Brief summary to F. with: what changed, key insights, next open paths

---

## 12) Common mistakes (lessons from real past failures)

### Mistake 1: "Agent-initiated theory" when F. had a precursor
**Happened:** Sessions 7-10 misattributed Theory-08, Theory-10, Phil-07.
**Fix:** Session 12 re-reading caught all 3; Session 12b corrected.
**Lesson:** Always grep F.'s foundational docs (Cognitive Economy Theory, Concept Formation, Tiered Intelligence, Anomaly Theory, etc.) for precursors before claiming agent-initiated.

### Mistake 2: PAPER.md header out of sync with footer
**Happened:** Session 13.6 audit found header said v0.2 while footer said v0.7.
**Fix:** S13.6 audit corrected. Added "header version matches footer" to §9 checks.
**Lesson:** Update both ends of PAPER.md whenever bumping version.

### Mistake 3: Authors line claimed agent co-authorship
**Happened:** Original PAPER.md header said "Authors: GENESIS Research Team (Fares + Agent)". Would have caused NeurIPS desk-reject.
**Fix:** S13.6 audit corrected to "Authors: Fares Rafat (sole author per NeurIPS 2025 policy)".
**Lesson:** §12.1 says agent is NOT a co-author. Header must reflect this.

### Mistake 4: PROJECT_README file map missing 4 directories + 4 files
**Happened:** S13.5 created the file map; S13.6 found it incomplete.
**Fix:** Made the file map exhaustive.
**Lesson:** When creating a file-map document, `ls -la` everything and enumerate.

### Mistake 5: `git add -A` includes longcot-chess permission files
**Happened:** Periodically through Sessions 1-13. Always excluded by careful `git add`.
**Lesson:** Always use explicit paths in `git add`.

### Mistake 6: Misleading "Current" in filenames
**Happened:** `GENESIS_Current_Regime_Status_AR.md` was actually dated 2026-05-31 (pre-paper).
**Fix:** Identified in S13.7 cleanup inventory; awaits F. decision to rename.
**Lesson:** Never use "Current" or "Latest" in filenames without dates.

---

## 13) How to recognize when to STOP and ask

You should pause and explicitly ask F. when:

1. **You found a misattribution.** Even if you can "fix" it, ask first (S12 → S12b precedent).
2. **You want to delete or move foundational docs.** All `GENESIS_*_AR.md` files are F.'s archive. Inventory only; F. decides actions.
3. **You disagree with a locked number.** They're locked for a reason. New measurements need F. authorization.
4. **You think the project should change direction.** Mode Pivot was F.'s strategic decision. So is any future pivot.
5. **You're about to add a new section/theory/philosophy.** Propose first, get authorization, then execute.
6. **You see a contradiction between two docs.** Don't silently fix it — document it in AUDIT_REPORT pattern, report to F.
7. **F. shares a new idea you don't fully understand.** Better to ask one question than to mis-integrate.

---

## 14) The "do no harm" principle

When in doubt about whether an action is good for the project:

**Compare against this baseline:** the project as it exists at commit `eb58198` (after S13.6) is:
- v0.7 paper with corrected attribution
- 18/18 consistency checks green
- Clear file structure documented in PROJECT_README
- 4 master docs covering navigation/timeline/attribution/audit
- 11 epistemic artifacts produced
- 0 active research integrity issues

**Any action that maintains or improves this baseline is acceptable.** Any action that risks degrading it should be questioned. If unsure → ask F.

---

## 15) Quick reference card (print this)

```
╔══════════════════════════════════════════════════════════════╗
║  GENESIS AGENT — QUICK REFERENCE                              ║
╠══════════════════════════════════════════════════════════════╣
║  AUTHOR: Fares Rafat (sole). I am NOT a co-author.            ║
║  MODE:   Theoretical (since S6). No runs. No new API calls.   ║
║  PAPER:  v0.7. Edits require explicit F. authorization.       ║
║                                                                ║
║  CHAIN:  propose → F. authorizes → execute → document         ║
║                                                                ║
║  READ FIRST (every session):                                  ║
║    1. PROJECT_README.md                                       ║
║    2. PAPER_PROTOCOL.md (v2.0 + §12.2)                        ║
║    3. PAPER/notes/HANDOFF.md                                  ║
║    4. CONTRIBUTION_LEDGER.md (esp. §6 + §9)                   ║
║    5. AUDIT_REPORT_S13.6.md (don't repeat past mistakes)      ║
║                                                                ║
║  UPDATE AT END (every session):                               ║
║    1. PAPER/notes/HANDOFF.md                                  ║
║    2. PAPER/notes/SESSION_LOG.md                              ║
║    3. PAPER/ideas/ATTRIBUTION_MAP.md                          ║
║    4. CONTRIBUTION_LEDGER.md (§6 + §9)                        ║
║    5. MASTER_TIMELINE.md                                      ║
║    6. PROJECT_README.md (last-updated line)                   ║
║                                                                ║
║  BEFORE COMMIT:                                               ║
║    - Security scan (sk-/gsk_/AIzaSy/github_pat_ etc.)         ║
║    - Explicit `git add PATH1 PATH2` (NEVER -A or .)           ║
║    - Skip: longcot-chess/*.py + push_runs.sh (not your work)  ║
║                                                                ║
║  IF AMBIGUOUS → ASK F. FIRST                                  ║
║  IF MISATTRIBUTION FOUND → PROPOSE, DO NOT UNILATERALLY FIX   ║
║  IF LOCKED NUMBER QUESTIONED → STOP, ASK F.                   ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 16) What's pending right now (as of S13.7)

For the next agent's awareness — these are open as of the most recent state:

### From Session 13 HANDOFF (still open)
- **Path 1c** (RECOMMENDED): New §15 "Theoretical Frame" → bumps PAPER v0.7 → v0.8
- **Path 1b**: Small §14 edits citing Agent Identity Theory → v0.7.1
- **Path 2**: Continue re-reading batch 4 (113 docs remain in queue)
- **Path 3**: Draft new Theory-NN candidate (7 candidates surfaced)
- **Path 4**: Idea-003 from F.

### From Session 13.7 (this session)
- `CLEANUP_INVENTORY_S13.7.md` proposed cleanup actions for ~95 Layer A files — awaiting F.'s decision (per-section or blanket policy A/B/C/D)
- `virtual_genesis/` directory (96 MB) decision: Option A (keep) / B (archive results only) / C (archive all) / D (delete result JSONs)
- `test_pioneer.py` decision: delete (dead code) or archive

---

## 17) Final word

This project's most distinguishing feature is **honesty about its own production process**. The Idea-002 Creative Attribution Rule, the three-layer §12.2 authorship structure, the §14 Ethics of Authorship section, the propose→authorize→execute chain, the periodic re-reading exercise (option F), the consistency-check audit pipeline — all of these exist so that the paper can be defended at NeurIPS-style venues *and* so that the human-agent collaboration model documented here is itself a research contribution.

If you follow this manual, the next agent (which might be you in a fresh session) will inherit a clean, navigable, defensible project. If you don't, you'll create work for the next agent to clean up — and possibly introduce errors that take entire sessions to detect.

**Default to honesty, conservatism, and documentation. F. is paying attention.**

---

**Manual version history:**
- v1.0 (S13.7, 2026-06-06): Initial creation by agent under F. authorization to make working rules explicit for future agents
