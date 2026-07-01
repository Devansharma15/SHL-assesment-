"""Refinement Engine — Module 7.

Updates existing recommendations based on user feedback or new constraints.

Purpose:
    Allows the user to narrow or expand their search without starting over.

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
from agent.prompts import build_refinement_prompt
from services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class RefinementEngine:
    """Updates recommendations based on new constraints."""

    @classmethod
    async def generate(
        cls,
        state: ConversationState,
        catalog_context: str,
        messages: list[dict],
    ) -> dict:
        """Generate refined recommendations based on updated requirements."""
        
        system_prompt = build_refinement_prompt(state, catalog_context)
        llm = get_llm_service()
        
        logger.debug("RefinementEngine calling LLM...")
        raw_response = await llm.generate(system_prompt, messages)
        
        return raw_response
