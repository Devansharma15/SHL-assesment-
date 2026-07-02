"""Retrieval Controller — Module 5.

Decides when retrieval is necessary and builds optimized search queries
from the structured ConversationState.

Purpose:
    Prevent retrieving irrelevant data on off-topic/greeting queries,
    and ensure retrieval uses the richest possible context for accuracy.

Inputs:
    - intent: Detected intent.
    - state: Reconstructed conversation state.

Outputs:
    - should_retrieve (bool)
    - retrieval_query (str)
    - Optional filters

Dependencies:
    - agent.conversation_analyzer.ConversationState
    - models.enums.AgentIntent
"""

from __future__ import annotations

import logging

from agent.conversation_analyzer import ConversationState
from models.enums import AgentIntent

logger = logging.getLogger(__name__)


class RetrievalController:
    """Controls when and how to retrieve from vector stores."""

    @classmethod
    def should_retrieve(cls, intent: AgentIntent, state: ConversationState) -> bool:
        """Determine if retrieval is needed based on intent and state."""
        # Never retrieve on the first message to force clarification
        if state.is_first_message:
            return False

        if intent in {AgentIntent.REFINEMENT, AgentIntent.COMPARISON}:
            return True

        if intent == AgentIntent.RECOMMENDATION:
            # Only retrieve when we have enough context
            return state.recommendation_readiness >= 0.4
            
        return False

    @classmethod
    def build_retrieval_query(cls, intent: AgentIntent, state: ConversationState, latest_message: str) -> str:
        """Build an enriched search query from structured state.

        Args:
            intent: Detected intent.
            state: Reconstructed conversation state.
            latest_message: The raw text of the most recent user message.

        Returns:
            Optimized query string.
        """
        # For pure comparison, the user's message is usually the best query
        if intent == AgentIntent.COMPARISON:
            return latest_message

        # Build query from extracted requirements
        reqs = state.requirements
        query_parts = []

        # 1. Base query from latest message (captures nuance)
        query_parts.append(latest_message)

        # 2. Add Role and Seniority if extracted
        if reqs.role and reqs.role.lower() not in latest_message.lower():
            query_parts.append(reqs.role)
            
        if reqs.seniority and reqs.seniority.lower() not in latest_message.lower():
            query_parts.append(reqs.seniority)

        # 3. Add Skills
        for skill in reqs.technical_skills + reqs.soft_skills:
            if skill.lower() not in latest_message.lower():
                query_parts.append(skill)

        # 4. Add Assessment Types
        for atype in reqs.assessment_types:
            if atype.lower() not in latest_message.lower():
                query_parts.append(atype)

        # 5. Add Industry
        if reqs.industry and reqs.industry.lower() not in latest_message.lower():
            query_parts.append(reqs.industry)

        enriched_query = " ".join(query_parts)
        
        logger.debug(
            "Retrieval query built: intent=%s, original='%s', enriched='%s'",
            intent,
            latest_message,
            enriched_query
        )
        
        return enriched_query
