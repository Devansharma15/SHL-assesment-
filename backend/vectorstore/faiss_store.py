"""FAISS vector store for semantic search over the SHL assessment catalog."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import faiss
import numpy as np

from vectorstore.embeddings import EmbeddingService, get_embedding_service

logger = logging.getLogger(__name__)

# Path to the catalog data
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CATALOG_PATH = DATA_DIR / "shl_product_catalog.json"
FAISS_INDEX_PATH = DATA_DIR / "faiss.index"
IDS_PATH = DATA_DIR / "faiss_ids.json"


class FAISSStore:
    """FAISS index for semantic similarity search over SHL assessments."""

    def __init__(self, embedding_service: EmbeddingService | None = None):
        self.embedding_service = embedding_service or get_embedding_service()
        self.index: faiss.Index | None = None
        self.catalog: list[dict] = []
        self.id_map: list[str] = []  # Maps FAISS row index -> assessment ID

    def load_catalog(self, catalog_path: Path | None = None) -> list[dict]:
        """Load the assessment catalog from JSON."""
        path = catalog_path or CATALOG_PATH
        if not path.exists():
            raise FileNotFoundError(f"Catalog not found at {path}")

        with open(path, encoding="utf-8") as f:
            self.catalog = json.load(f)

        logger.info("Loaded %d assessments from catalog.", len(self.catalog))
        return self.catalog

    def _build_embedding_text(self, assessment: dict) -> str:
        """Build the text representation for embedding an assessment.

        Combines multiple fields into a rich text representation that captures
        the assessment's purpose, skills, and target audience.
        """
        parts = [
            assessment.get("name", ""),
            assessment.get("test_type", ""),
            assessment.get("category", ""),
            assessment.get("description", ""),
            " ".join(assessment.get("keys", [])),
            " ".join(assessment.get("job_families", [])),
            " ".join(assessment.get("job_levels", [])),
        ]
        return " | ".join(part for part in parts if part)

    def build_index(self, catalog: list[dict] | None = None) -> None:
        """Build the FAISS index from the assessment catalog.

        Args:
            catalog: Optional list of assessment dicts. If None, uses self.catalog.
        """
        if catalog is not None:
            self.catalog = catalog

        if not self.catalog:
            raise ValueError("No catalog data. Call load_catalog() first.")

        # Build embedding texts
        texts = [self._build_embedding_text(a) for a in self.catalog]
        self.id_map = [str(a.get("entity_id") or a.get("id") or "") for a in self.catalog]

        # Generate embeddings
        logger.info("Generating embeddings for %d assessments...", len(texts))
        embeddings = self.embedding_service.encode(texts)

        # Build FAISS index (IndexFlatIP for inner product = cosine sim with normalized vectors)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)

        logger.info(
            "FAISS index built: %d vectors, %d dimensions.",
            self.index.ntotal,
            dim,
        )

    def save_index(self, index_path: Path | None = None, ids_path: Path | None = None) -> None:
        """Persist the FAISS index and ID mapping to disk."""
        idx_path = index_path or FAISS_INDEX_PATH
        id_path = ids_path or IDS_PATH

        if self.index is None:
            raise ValueError("No index to save. Call build_index() first.")

        faiss.write_index(self.index, str(idx_path))
        with open(id_path, "w", encoding="utf-8") as f:
            json.dump(self.id_map, f)

        logger.info("FAISS index saved to %s", idx_path)

    def load_index(self, index_path: Path | None = None, ids_path: Path | None = None) -> None:
        """Load a pre-built FAISS index from disk."""
        idx_path = index_path or FAISS_INDEX_PATH
        id_path = ids_path or IDS_PATH

        if not idx_path.exists():
            logger.warning("No pre-built FAISS index found. Building from catalog...")
            self.load_catalog()
            self.build_index()
            self.save_index()
            return

        self.index = faiss.read_index(str(idx_path))
        with open(id_path, encoding="utf-8") as f:
            self.id_map = json.load(f)

        self.load_catalog()
        assert self.index is not None
        logger.info("FAISS index loaded: %d vectors.", self.index.ntotal)

    def search(self, query: str, top_k: int = 20) -> list[dict]:
        """Search for the most similar assessments to the query.

        Args:
            query: Natural language search query.
            top_k: Number of results to return.

        Returns:
            List of dicts with 'assessment' data and 'score'.
        """
        if self.index is None:
            raise ValueError("Index not loaded. Call load_index() or build_index() first.")

        # Encode query
        query_embedding = self.embedding_service.encode_query(query)

        # Search
        scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            assessment_id = self.id_map[idx]
            assessment = next(
                (a for a in self.catalog if (a.get("entity_id") or a.get("id")) == assessment_id),
                None,
            )
            if assessment:
                results.append({"assessment": assessment, "score": float(score)})

        return results

    def initialize(self) -> None:
        """Initialize the store: load or build the index."""
        try:
            self.load_index()
        except Exception as e:
            logger.warning("Failed to load index, building from scratch: %s", e)
            self.load_catalog()
            self.build_index()
            try:
                self.save_index()
            except Exception as save_err:
                logger.warning("Could not save index: %s", save_err)
