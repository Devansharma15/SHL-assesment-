"""Comparison Engine — Module 8.

Compares two or more assessments side-by-side.

Purpose:
    When a user asks "what is the difference between X and Y", this engine
    retrieves both and prompts the LLM to compare them across dimensions.

Inputs:
    - catalog_context: Formatted string of retrieved assessments to compare
    - messages: Conversation history

Outputs:
    - Raw LLM response dict

Dependencies:
    - agent.prompts
    - services.llm_service
"""

from __future__ import annotations

import logging

from agent.prompts import build_comparison_prompt
from services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class ComparisonEngine:
    """Compares multiple assessments."""

    @classmethod
    async def generate(
        cls,
        catalog_context: str,
        messages: list[dict],
    ) -> dict:
        """Generate comparison based on retrieved catalog context."""
        
        system_prompt = build_comparison_prompt(catalog_context)
        llm = get_llm_service()
        
        logger.debug("ComparisonEngine calling LLM...")
        raw_response = await llm.generate(system_prompt, messages)
        
        return raw_response
