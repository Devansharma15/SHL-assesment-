"""Hybrid retriever combining FAISS semantic search with BM25 keyword search via Reciprocal Rank Fusion."""

from __future__ import annotations

import logging
from collections import defaultdict

from vectorstore.bm25_store import BM25Store
from vectorstore.faiss_store import FAISSStore

logger = logging.getLogger(__name__)


class HybridRetriever:
    """Combines semantic (FAISS) and keyword (BM25) search using Reciprocal Rank Fusion.

    RRF merges ranked result lists without requiring score normalization,
    making it robust to different scoring scales between FAISS and BM25.
    """

    def __init__(
        self,
        faiss_store: FAISSStore,
        bm25_store: BM25Store,
        semantic_top_k: int = 20,
        keyword_top_k: int = 20,
        rrf_k: int = 60,
    ):
        self.faiss_store = faiss_store
        self.bm25_store = bm25_store
        self.semantic_top_k = semantic_top_k
        self.keyword_top_k = keyword_top_k
        self.rrf_k = rrf_k

    @staticmethod
    def reciprocal_rank_fusion(
        result_lists: list[list[dict]],
        k: int = 60,
    ) -> list[dict]:
        """Merge multiple ranked result lists using Reciprocal Rank Fusion.

        RRF score for document d = sum over all lists of 1 / (k + rank(d) + 1)

        Args:
            result_lists: List of ranked result lists. Each result has 'assessment' with 'id'.
            k: RRF constant controlling the impact of high vs. low rankings.

        Returns:
            Merged list sorted by RRF score (descending).
        """
        rrf_scores: dict[str, float] = defaultdict(float)
        assessment_map: dict[str, dict] = {}

        for results in result_lists:
            for rank, result in enumerate(results):
                doc_id = result["assessment"].get("id") or result["assessment"].get("entity_id")
                if not doc_id:
                    continue
                rrf_scores[doc_id] += 1.0 / (k + rank + 1)
                # Keep the assessment data (first occurrence wins)
                if doc_id not in assessment_map:
                    assessment_map[doc_id] = result["assessment"]

        # Sort by RRF score descending
        sorted_ids = sorted(rrf_scores.keys(), key=lambda d: -rrf_scores[d])

        return [
            {"assessment": assessment_map[doc_id], "score": rrf_scores[doc_id]}
            for doc_id in sorted_ids
        ]

    def search(self, query: str, top_k: int | None = None) -> list[dict]:
        """Perform hybrid search combining semantic and keyword results.

        Args:
            query: Natural language search query.
            top_k: Override for the number of results to return after fusion.

        Returns:
            List of dicts with 'assessment' and 'score', sorted by relevance.
        """
        # Semantic search via FAISS
        try:
            semantic_results = self.faiss_store.search(query, top_k=self.semantic_top_k)
            logger.debug("Semantic search returned %d results.", len(semantic_results))
        except Exception as e:
            logger.error("Semantic search failed: %s", e)
            semantic_results = []

        # Keyword search via BM25
        try:
            keyword_results = self.bm25_store.search(query, top_k=self.keyword_top_k)
            logger.debug("Keyword search returned %d results.", len(keyword_results))
        except Exception as e:
            logger.error("Keyword search failed: %s", e)
            keyword_results = []

        # Handle degraded modes
        if not semantic_results and not keyword_results:
            logger.warning("Both search methods returned no results for query: %s", query[:100])
            return []

        # Reciprocal Rank Fusion
        fused = self.reciprocal_rank_fusion(
            [semantic_results, keyword_results],
            k=self.rrf_k,
        )

        # Limit results
        max_results = top_k or (self.semantic_top_k + self.keyword_top_k)
        return fused[:max_results]
