"""BM25 keyword search over the SHL assessment catalog."""

from __future__ import annotations

import json
import logging
import pickle
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CATALOG_PATH = DATA_DIR / "shl_product_catalog.json"
BM25_INDEX_PATH = DATA_DIR / "bm25.pkl"


class BM25Store:
    """BM25 keyword search index over SHL assessments."""

    def __init__(self):
        self.bm25: BM25Okapi | None = None
        self.catalog: list[dict] = []
        self.tokenized_corpus: list[list[str]] = []

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Simple whitespace + punctuation tokenizer with lowercasing."""
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return [token for token in text.split() if len(token) > 1]

    def _build_document_text(self, assessment: dict) -> str:
        """Build searchable text from an assessment record."""
        parts = [
            assessment.get("name", ""),
            assessment.get("test_type", ""),
            assessment.get("category", ""),
            assessment.get("description", ""),
            " ".join(assessment.get("keys", [])),
            " ".join(assessment.get("job_families", [])),
            " ".join(assessment.get("job_levels", [])),
        ]
        return " ".join(part for part in parts if part)

    def load_catalog(self, catalog_path: Path | None = None) -> list[dict]:
        """Load catalog from JSON."""
        path = catalog_path or CATALOG_PATH
        with open(path, encoding="utf-8") as f:
            self.catalog = json.load(f)
        logger.info("BM25: Loaded %d assessments.", len(self.catalog))
        return self.catalog

    def build_index(self, catalog: list[dict] | None = None) -> None:
        """Build BM25 index from the catalog."""
        if catalog is not None:
            self.catalog = catalog
        if not self.catalog:
            raise ValueError("No catalog data. Call load_catalog() first.")

        texts = [self._build_document_text(a) for a in self.catalog]
        self.tokenized_corpus = [self._tokenize(text) for text in texts]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

        logger.info("BM25 index built with %d documents.", len(self.tokenized_corpus))

    def save_index(self, index_path: Path | None = None) -> None:
        """Save BM25 index to disk."""
        path = index_path or BM25_INDEX_PATH
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "bm25": self.bm25,
                    "tokenized_corpus": self.tokenized_corpus,
                },
                f,
            )
        logger.info("BM25 index saved to %s", path)

    def load_index(self, index_path: Path | None = None) -> None:
        """Load pre-built BM25 index from disk."""
        path = index_path or BM25_INDEX_PATH
        if not path.exists():
            logger.warning("No pre-built BM25 index found. Building from catalog...")
            self.load_catalog()
            self.build_index()
            self.save_index()
            return

        with open(path, "rb") as f:
            data = pickle.load(f)
        self.bm25 = data["bm25"]
        self.tokenized_corpus = data["tokenized_corpus"]
        self.load_catalog()
        logger.info("BM25 index loaded with %d documents.", len(self.tokenized_corpus))

    def search(self, query: str, top_k: int = 20) -> list[dict]:
        """Search for assessments matching the query keywords.

        Args:
            query: Natural language search query.
            top_k: Number of results to return.

        Returns:
            List of dicts with 'assessment' data and 'score'.
        """
        if self.bm25 is None:
            raise ValueError("BM25 index not loaded.")

        tokenized_query = self._tokenize(query)
        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(tokenized_query)

        # Get top-k indices
        top_indices = sorted(range(len(scores)), key=lambda i: -scores[i])[:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append(
                    {
                        "assessment": self.catalog[idx],
                        "score": float(scores[idx]),
                    }
                )

        return results

    def initialize(self) -> None:
        """Initialize the BM25 store."""
        try:
            self.load_index()
        except Exception as e:
            logger.warning("Failed to load BM25 index, building: %s", e)
            self.load_catalog()
            self.build_index()
            try:
                self.save_index()
            except Exception as save_err:
                logger.warning("Could not save BM25 index: %s", save_err)
