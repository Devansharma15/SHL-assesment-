"""Sentence-transformer embedding wrapper for bge-small-en-v1.5."""

from __future__ import annotations

import logging
from functools import lru_cache

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Manages sentence-transformer model for generating embeddings."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        """Lazy-load the embedding model."""
        if self._model is None:
            logger.info("Loading embedding model: %s", self.model_name)
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully.")
        return self._model

    def encode(
        self,
        texts: list[str],
        normalize: bool = True,
        batch_size: int = 32,
    ) -> np.ndarray:
        """Encode texts into dense embeddings.

        Args:
            texts: List of text strings to encode.
            normalize: Whether to L2-normalize embeddings (required for cosine similarity via inner product).
            batch_size: Batch size for encoding.

        Returns:
            numpy array of shape (len(texts), embedding_dim).
        """
        # bge-small-en-v1.5 recommends prepending "Represent this sentence: " for queries
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=normalize,
            batch_size=batch_size,
            show_progress_bar=False,
        )
        return np.array(embeddings, dtype=np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        """Encode a single query with the recommended query prefix for bge models.

        Args:
            query: The search query string.

        Returns:
            numpy array of shape (1, embedding_dim).
        """
        # bge models use instruction prefix for queries
        prefixed = f"Represent this sentence for searching relevant passages: {query}"
        return self.encode([prefixed])

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        dim = self.model.get_embedding_dimension()
        if dim is None:
            raise RuntimeError("Could not determine embedding dimension from model.")
        return dim


@lru_cache(maxsize=1)
def get_embedding_service(model_name: str = "BAAI/bge-small-en-v1.5") -> EmbeddingService:
    """Get or create the singleton EmbeddingService."""
    return EmbeddingService(model_name=model_name)
