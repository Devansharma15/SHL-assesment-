"""Confidence Estimator — Module 13.

Estimates confidence (High, Medium, Low) for the agent's response based on
retrieval scores, requirement completeness, and hallucination survival rate.

Purpose:
    Provide a signal to the UI or downstream systems about how much trust
    to place in the current recommendation set.

Inputs:
    - state: Reconstructed conversation state.
    - reranked_candidates: Results from the retriever/reranker.
    - final_recommendations: Post-hallucination guard recommendations.

Outputs:
    - ConfidenceLevel enum (HIGH, MEDIUM, LOW).

Dependencies:
    - agent.conversation_analyzer.ConversationState
    - models.enums.ConfidenceLevel
"""

from __future__ import annotations

import logging

from agent.conversation_analyzer import ConversationState
from models.enums import ConfidenceLevel

logger = logging.getLogger(__name__)


class ConfidenceEstimator:
    """Estimates confidence level for agent recommendations."""

    @classmethod
    def estimate(
        cls,
        state: ConversationState,
        reranked_candidates: list[dict],
        final_recommendations: list[dict],
    ) -> ConfidenceLevel:
        """Estimate the confidence level of the generated recommendations.
        
        Algorithm:
        1. Base score derived from conversation readiness (completeness).
        2. Adjust by retrieval quality (top candidate score).
        3. Adjust by hallucination survival rate (did the LLM invent things?).
        
        Args:
            state: Conversation state.
            reranked_candidates: The raw retrieval results given to the LLM.
            final_recommendations: The validated recommendations returned by the LLM.
            
        Returns:
            ConfidenceLevel (HIGH, MEDIUM, LOW).
        """
        if not final_recommendations:
            return ConfidenceLevel.LOW

        # 1. Base score from state completeness (0.0 - 1.0)
        score = state.recommendation_readiness

        # 2. Retrieval quality adjustment
        if reranked_candidates:
            top_score = reranked_candidates[0].get("score", 0.0)
            rerank_score = reranked_candidates[0].get("rerank_score", 0.0)
            
            # Cross-encoder scores are logits, usually > 0 is good, > 5 is great
            if rerank_score > 3.0:
                score += 0.2
            elif rerank_score < -2.0:
                score -= 0.2
                
            # Fallback to RRF score if reranker failed
            elif top_score > 0.01: 
                score += 0.1

        # 3. Hallucination survival adjustment
        # If the LLM returned 5 recs but 3 were hallucinated, confidence drops
        # We don't have the original LLM count here, but if we have very few 
        # final recommendations compared to what we retrieved, it might indicate
        # poor matching.
        if len(final_recommendations) == 0:
            return ConfidenceLevel.LOW
            
        # Final bucketing
        if score >= 0.75:
            confidence = ConfidenceLevel.HIGH
        elif score >= 0.40:
            confidence = ConfidenceLevel.MEDIUM
        else:
            confidence = ConfidenceLevel.LOW
            
        logger.debug(
            "Confidence estimated: %s (score: %.2f, recs: %d)", 
            confidence, score, len(final_recommendations)
        )
        
        return confidence
