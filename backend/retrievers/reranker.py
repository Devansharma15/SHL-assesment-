"""Cross-encoder reranker for improving retrieval precision."""

from __future__ import annotations

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """Reranks candidate assessments using a cross-encoder model.

    Cross-encoders jointly encode (query, document) pairs and produce
    a relevance score, providing much higher accuracy than bi-encoder
    similarity scores at the cost of being slower (hence used on top-K results only).
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        """Lazy-load the cross-encoder model."""
        if self._model is None:
            logger.info("Loading cross-encoder reranker: %s", self.model_name)
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(self.model_name)
            logger.info("Cross-encoder loaded successfully.")
        return self._model

    def _build_document_text(self, assessment: dict) -> str:
        """Build text representation for reranking."""
        parts = [
            assessment.get("name", ""),
            assessment.get("test_type", ""),
            assessment.get("description", ""),
            " ".join(assessment.get("skills_measured", [])),
        ]
        return " | ".join(part for part in parts if part)

    def rerank(
        self,
        query: str,
        candidates: list[dict],
        top_k: int = 10,
    ) -> list[dict]:
        """Rerank candidates using the cross-encoder.

        Args:
            query: The original search query.
            candidates: List of candidate dicts with 'assessment' key.
            top_k: Number of top results to return after reranking.

        Returns:
            Reranked list of dicts with 'assessment' and updated 'score'.
        """
        if not candidates:
            return []

        # Build (query, document) pairs
        pairs = [(query, self._build_document_text(c["assessment"])) for c in candidates]

        # Score all pairs
        try:
            scores = self.model.predict(pairs)
        except Exception as e:
            logger.error("Cross-encoder reranking failed: %s", e)
            # Fallback: return original order
            return candidates[:top_k]

        # Attach scores and sort
        for candidate, score in zip(candidates, scores):
            candidate["rerank_score"] = float(score)

        reranked = sorted(candidates, key=lambda c: -c["rerank_score"])

        return reranked[:top_k]


@lru_cache(maxsize=1)
def get_reranker(model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> CrossEncoderReranker:
    """Get or create the singleton reranker."""
    return CrossEncoderReranker(model_name=model_name)
