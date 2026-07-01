"""Hallucination Guard — Module 11.

Ensures every recommendation produced by the LLM exists in the actual catalog.
Prevents the agent from hallucinating fake assessments, URLs, or features.

Purpose:
    Maintain strict groundedness against the real catalog data.

Inputs:
    - llm_recommendations: List of dicts returned by LLM.
    - catalog: List of all valid assessment dicts.

Outputs:
    - Validated list of recommendations with exact catalog names and URLs.

Dependencies:
    None.
"""

from __future__ import annotations

import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class HallucinationGuard:
    """Validates LLM recommendations against ground-truth catalog."""

    @classmethod
    def validate(cls, llm_recommendations: list[dict], catalog: list[dict]) -> list[dict]:
        """Validate that recommendations reference real catalog assessments.

        Checks each recommendation name against the catalog and filters out
        hallucinated assessments. Corrects URLs if the LLM hallucinated them.

        Args:
            llm_recommendations: Raw recommendation dicts from the LLM.
            catalog: Full catalog data.

        Returns:
            Filtered list containing only valid catalog assessments, capped at 10.
        """
        if not llm_recommendations:
            return []

        catalog_names = {a["name"].lower() for a in catalog}
        catalog_by_name = {a["name"].lower(): a for a in catalog}

        validated = []
        
        for rec in llm_recommendations:
            # Handle string-only recommendations (if LLM failed schema)
            if isinstance(rec, str):
                name = rec.lower()
                rec_dict = {"name": rec, "test_type": "", "why_recommended": ""}
            else:
                name = rec.get("name", "").lower()
                rec_dict = dict(rec)  # Copy

            if not name:
                continue

            # 1. Exact match
            if name in catalog_names:
                catalog_entry = catalog_by_name[name]
                cls._merge_catalog_data(rec_dict, catalog_entry)
                validated.append(rec_dict)
                continue

            # 2. Substring match (e.g., LLM outputs "Verify G+" but catalog is "SHL Verify G+")
            matched = False
            for catalog_name, catalog_entry in catalog_by_name.items():
                if catalog_name in name or name in catalog_name:
                    cls._merge_catalog_data(rec_dict, catalog_entry)
                    validated.append(rec_dict)
                    matched = True
                    break
                    
            if matched:
                continue

            # 3. Fuzzy match fallback for slight typos (e.g., OPQ-32 vs OPQ32)
            best_ratio = 0.0
            best_match = None
            
            for catalog_name, catalog_entry in catalog_by_name.items():
                ratio = SequenceMatcher(None, name, catalog_name).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = catalog_entry
                    
            if best_ratio > 0.85 and best_match:  # High similarity threshold
                cls._merge_catalog_data(rec_dict, best_match)
                validated.append(rec_dict)
                continue

            # Filtered out completely
            logger.warning("Filtered out hallucinated recommendation: '%s'", rec.get("name", name))

        return validated[:10]  # Hard cap at 10 per requirements

    @classmethod
    def _merge_catalog_data(cls, target_rec: dict, catalog_entry: dict) -> None:
        """Merge authoritative catalog data into the LLM recommendation.
        
        This guarantees the name and URL are 100% correct, overriding
        any LLM hallucinations for these fields.
        """
        # Force canonical name
        target_rec["name"] = catalog_entry.get("name", "")
        
        # Force canonical URL (handle schema difference where link might be used instead of url)
        target_rec["url"] = catalog_entry.get("link") or catalog_entry.get("url", "")
        
        # Add test_type if LLM didn't provide one
        if not target_rec.get("test_type"):
            # Catalog schema might have it under 'keys' or 'category' or 'test_type'
            keys = catalog_entry.get("keys", [])
            target_rec["test_type"] = keys[0] if keys else catalog_entry.get("test_type", "")
