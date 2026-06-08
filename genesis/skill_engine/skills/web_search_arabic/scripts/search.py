"""
web_search_arabic skill script
================================
Executes web search with Arabic-optimized strategy.
Called by skill_use tool or directly in target_agent.py.
"""
import json
import os
import sys


def search_with_evidence(query: str, local_filter: str = "", max_results: int = 10) -> dict:
    """
    Global-first search with evidence tracking.
    Returns: {results: list, evidence_log_path: str, hallucination_rate: float}
    """
    try:
        from genesis.tools.web_search import web_search, extract_keywords, EvidenceLog
    except ImportError:
        return {"error": "genesis.tools.web_search not available", "results": []}

    evidence_log = EvidenceLog()

    # Step 1: Extract keywords (SAGE precision)
    keywords = extract_keywords(query)
    if not keywords:
        keywords = query.split()[:4]

    # Step 2: Global search first
    global_query = " ".join(keywords)
    results = web_search(global_query, mode="quick", num_results=max_results, evidence_log=evidence_log)

    # Step 3: Deep read top result
    if results:
        deep = web_search(results[0].url, mode="read", evidence_log=evidence_log)
        if deep:
            results[0].content = deep[0].content

    # Step 4: Local filter results (not queries)
    if local_filter:
        local_relevant = [
            r for r in results
            if local_filter.lower() in (r.title + r.snippet).lower()
        ]
        # Keep global + add local-relevant
        results = results + [r for r in local_relevant if r not in results]

    # Step 5: Save evidence log
    working_dir = os.getenv("GENESIS_SANDBOX_ARGS_WORKING_DIR", "/tmp")
    log_path = os.path.join(working_dir, "evidence_log.json")
    try:
        evidence_log.save(log_path)
    except Exception:
        pass

    return {
        "results": [r.to_dict() for r in results[:max_results]],
        "evidence_log_path": log_path,
        "hallucination_rate": evidence_log.hallucination_rate,
        "searches_performed": evidence_log.searches_performed,
        "keywords_used": keywords,
    }


if __name__ == "__main__":
    args_file = os.getenv("GENESIS_SANDBOX_ARGS")
    if args_file and os.path.exists(args_file):
        with open(args_file) as f:
            args = json.load(f)
    else:
        args = {"query": sys.argv[1] if len(sys.argv) > 1 else "test query"}

    result = search_with_evidence(
        query=args.get("query", ""),
        local_filter=args.get("local_filter", ""),
        max_results=args.get("max_results", 10),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
