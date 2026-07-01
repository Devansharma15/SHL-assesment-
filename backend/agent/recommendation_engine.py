"""Recommendation Engine — Module 6.

Generates standard assessment recommendations.

Purpose:
    Given a set of retrieved catalog entries and the extracted requirements,
    prompts the LLM to select and explain the best fits.

Inputs:
    - state: ConversationState
    - catalog_context: Formatted string of retrieved assessments
    - messages: Conversation history

Outputs:
    - Raw LLM response dict

Dependencies:
    - agent.prompts
    - services.llm_service
"""

from __future__ import annotations

import logging

from agent.conversation_analyzer import ConversationState
from agent.prompts import build_recommendation_prompt
from services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generates recommendations from catalog context."""

    @classmethod
    async def generate(
        cls,
        state: ConversationState,
        catalog_context: str,
        messages: list[dict],
    ) -> dict:
        """Generate recommendations based on requirements and catalog context."""
        
        system_prompt = build_recommendation_prompt(state, catalog_context)
        llm = get_llm_service()
        
        logger.debug("RecommendationEngine calling LLM...")
        raw_response = await llm.generate(system_prompt, messages)
        
        return raw_response
