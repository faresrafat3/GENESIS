---
name: web_search_arabic
description: Search web for Arabic platforms/opportunities with global-first strategy and evidence tracking
domain: research
version: 1.0.0
task_types:
  - micro_task
  - research
  - fact_finding
  - platform_verification
---

# web_search_arabic

## When to use
- Task requires finding platforms, opportunities, or facts not in training data
- Information freshness is critical (2024-2026 data needed)
- Platform availability for Arabic speakers needs verification
- Claims need source URLs (credibility required)

## Core principles
1. **Global first**: Search globally WITHOUT region filter initially
2. **Keywords before queries**: Extract precise keywords first (SAGE: BM25 precision)
3. **Every claim needs a source**: Use EvidenceLog for tracking
4. **Mark unknown explicitly**: "UNVERIFIED" not silence
5. **Multi-mode search**: quick for discovery, read for depth

## Recommended tools
- `web_search(query, mode="quick")` — broad discovery (Serper)
- `web_search(url, mode="read")` — deep page reading (Jina)
- `extract_keywords(query)` — precise keyword extraction
- `EvidenceLog` — claim source tracking

## Workflow
Step 1: Decompose task into 3-5 search sub-goals (most important first)
Step 2: For each sub-goal:
  a. `extract_keywords(sub_goal)` → 3-5 keywords
  b. `web_search(" ".join(keywords), mode="quick")` → broad results
  c. `web_search(best_url, mode="read")` → deep content for top result
Step 3: For each claim extracted:
  - `evidence_log.add_claim(claim, source_url=url, confidence="HIGH|MEDIUM|LOW|UNVERIFIED")`
Step 4: Apply regional filter AFTER global discovery (not before)
Step 5: `evidence_log.save("evidence_log.json")`
Step 6: Mark claims without sources explicitly as "UNVERIFIED"

## Example
```python
from genesis.tools.web_search import web_search, EvidenceLog, extract_keywords

evidence_log = EvidenceLog()
keywords = extract_keywords("micro-task platforms payment Egypt")
results = web_search(" ".join(keywords), mode="quick")

for r in results[:3]:
    page = web_search(r.url, mode="read")
    # Extract claims, add to evidence_log
    evidence_log.add_claim(
        "Clickworker pays via PayPal",
        source_url=r.url, source_date=r.date,
        confidence="MEDIUM", quote="relevant quote"
    )
evidence_log.save("evidence_log.json")
print(f"Hallucination rate: {evidence_log.hallucination_rate:.0%}")
```
