"""
GENESIS Skill Engine — Skill Retriever
========================================
Component: SKILL_ENGINE.retriever
Source: SkillOps + SAGE

STOLEN_FROM:
  SkillOps (arXiv:2605.13716):
    - Hybrid retrieval: r(s,τ) = λ·BM25(s,τ) + (1-λ)·semantic(s,τ)
    - Precondition filtering BEFORE retrieval (not after)
    - Only return skills whose P is satisfied

  SAGE (arXiv:2602.05975):
    - BM25 > LLM-based retrievers for precise queries
    - Keyword-based search outperforms semantic for skill names

GENESIS_ADAPTATION:
  - Simple BM25 via term frequency (no external lib needed)
  - Semantic via keyword overlap (no embeddings — free tier)
  - Filter by domain and task_type first (fast pre-filter)
  - Returns ranked list for Meta-Agent selection

CALLED_BY:
  - genesis/skill_engine/__init__.py: retrieve()
  - genesis/orchestrator.py Section 5b: best skills → feedback
  - genesis/skill_engine/evolver.py: find relevant existing skills
"""

from __future__ import annotations

import math
import re
from collections import Counter

from genesis.skill_engine.skill import Skill
from genesis.skill_engine.library import SkillLibrary


class SkillRetriever:
    """
    Hybrid BM25 + semantic retrieval with precondition filtering.
    SkillOps: r(s,τ) = λ·BM25 + (1-λ)·semantic
    """

    def __init__(self, lambda_bm25: float = 0.6):
        self.lambda_bm25 = lambda_bm25

    def retrieve(
        self,
        query: str,
        library: SkillLibrary,
        top_k: int = 3,
        domain_filter: str | None = None,
        task_type_filter: str | None = None,
        context: dict | None = None,
    ) -> list[Skill]:
        """
        SkillOps: retrieve relevant skills.
        Steps:
          1. Pre-filter by domain/task_type
          2. Check preconditions (P)
          3. Score: λ·BM25 + (1-λ)·semantic
          4. Return top-k
        """
        skills = library.list_all()

        # Step 1: domain/task_type pre-filter
        if domain_filter:
            skills = [s for s in skills if s.domain == domain_filter or not s.domain]
        if task_type_filter:
            skills = [
                s for s in skills
                if not s.task_types or task_type_filter in s.task_types
            ]

        # Step 2: precondition check (SkillOps P)
        if context:
            valid_skills = []
            for s in skills:
                ok, _ = s.contract.check_preconditions(context)
                if ok:
                    valid_skills.append(s)
            skills = valid_skills

        if not skills:
            return []

        # Step 3: score
        scored = []
        query_tokens = self._tokenize(query)
        corpus = [self._tokenize(s.description + " " + " ".join(s.when_to_use)) for s in skills]

        for i, skill in enumerate(skills):
            bm25 = self._bm25_score(query_tokens, corpus[i], corpus)
            sem = self._semantic_score(query_tokens, corpus[i])
            score = self.lambda_bm25 * bm25 + (1 - self.lambda_bm25) * sem
            # Boost by performance_score
            perf_boost = skill.performance_score / 200  # 0→0, 100→0.5
            scored.append((score + perf_boost, skill))

        # Sort descending
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:top_k]]

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization: lowercase words, no stopwords."""
        stopwords = {"the", "a", "an", "is", "it", "for", "of", "to", "in",
                     "and", "or", "with", "at", "on", "by", "من", "في", "على"}
        tokens = re.findall(r'\w+', text.lower())
        return [t for t in tokens if t not in stopwords and len(t) > 2]

    def _bm25_score(
        self,
        query_tokens: list[str],
        doc_tokens: list[str],
        corpus: list[list[str]],
        k1: float = 1.5,
        b: float = 0.75,
    ) -> float:
        """
        BM25 scoring.
        SAGE insight: BM25 > LLM-based retrieval for precise queries.
        """
        if not doc_tokens or not query_tokens:
            return 0.0

        N = len(corpus)
        avg_dl = sum(len(d) for d in corpus) / max(N, 1)
        dl = len(doc_tokens)
        doc_counter = Counter(doc_tokens)

        score = 0.0
        corpus_counters = [Counter(d) for d in corpus]

        for term in query_tokens:
            # IDF
            df = sum(1 for c in corpus_counters if term in c)
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
            # TF
            tf = doc_counter.get(term, 0)
            tf_norm = tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl / max(avg_dl, 1)))
            score += idf * tf_norm

        # Normalize
        return min(score / (len(query_tokens) * 3), 1.0)

    def _semantic_score(self, query_tokens: list[str], doc_tokens: list[str]) -> float:
        """
        Simple semantic score via token overlap.
        No embeddings needed — free tier compatible.
        """
        if not query_tokens or not doc_tokens:
            return 0.0
        query_set = set(query_tokens)
        doc_set = set(doc_tokens)
        intersection = query_set & doc_set
        union = query_set | doc_set
        return len(intersection) / len(union) if union else 0.0
