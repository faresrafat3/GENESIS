# Multi-Model GPQA Benchmark Results

**Date:** 2026-06-04 23:15
**Questions:** 20
**Models:** 3
**Key pool:** 11 keys, 11 available now, 0 dead

## Ranking (sorted by our accuracy)

| # | Model | Our % | Official % | Gap | Correct | Invalid | Recovered | Time | q/s |
|---|-------|-------|-----------|-----|---------|---------|-----------|------|-----|
| 1 | `gpt-oss-120b-free` | **65.00** | 80.1 | -15.1 | 13/20 | 5 | 0 | 2096s | 0.01 |
| 2 | `nemotron-3-nano-free` | **55.00** | - | - | 11/20 | 9 | 0 | 349s | 0.06 |
| 3 | `lfm-2.5-thinking-free` | **15.00** | 37.9 | -22.9 | 3/20 | 8 | 0 | 614s | 0.03 |

## Notes

- **Our %**: What we measured in this run
- **Official %**: From vendor's model card (or '-' if not published)
- **Gap**: positive = we beat official, negative = we are below
- Large negative gaps usually indicate: rate limits, free-tier quantization, or scaffolding bugs

## API Key Pool Usage

- **ahmed**: 1 requests, 0 ok, 1 failed (0.0% success) — available
- **faresrafatfares**: 60 requests, 60 ok, 0 failed (100.0% success) — available
- **faresrafat434**: 0 requests, 0 ok, 0 failed (0.0% success) — available
- **faresrafat435**: 0 requests, 0 ok, 0 failed (0.0% success) — available
- **faresrafat436**: 0 requests, 0 ok, 0 failed (0.0% success) — available
- **faresrafat437**: 0 requests, 0 ok, 0 failed (0.0% success) — available
- **faresrafat818**: 0 requests, 0 ok, 0 failed (0.0% success) — available
- **faresrafat433**: 0 requests, 0 ok, 0 failed (0.0% success) — available
- **farmfares1**: 0 requests, 0 ok, 0 failed (0.0% success) — available
- **farmfares2**: 0 requests, 0 ok, 0 failed (0.0% success) — available
- **farmfares3**: 0 requests, 0 ok, 0 failed (0.0% success) — available