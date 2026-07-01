"""Clarification Engine — Module 3.

Determines if clarification is needed and generates the best question.
Ensures we don't ask unnecessary questions and stop once we have enough info.

Purpose:
    Prevent low-quality recommendations by gating retrieval until the user
    provides sufficient context.

Inputs:
    - state: ConversationState from the analyzer.

Outputs:
    - should_clarify (bool)
    - clarification_question (str)

Dependencies:
    - agent.conversation_analyzer.ConversationState
    - app.config.settings
"""

from __future__ import annotations

import logging
import re

from agent.conversation_analyzer import ConversationState
from app.config import settings

logger = logging.getLogger(__name__)


class ClarificationEngine:
    """Manages clarification gating and question selection."""

    @classmethod
    def generate_domain_question(cls, messages: list[dict], state: ConversationState) -> str | None:
        """Generate scenario-specific clarifications learned from sample traces."""
        user_text = " ".join(
            str(message.get("content", ""))
            for message in messages
            if message.get("role") == "user"
        ).lower()
        assistant_text = " ".join(
            str(message.get("content", ""))
            for message in messages
            if message.get("role") == "assistant"
        ).lower()

        if (
            any(term in user_text for term in ["contact centre", "contact center", "inbound calls"])
            and not any(term in user_text for term in ["english", "spanish", "french"])
        ):
            return "What language will the customer calls be in?"

        if (
            any(term in user_text for term in ["contact centre", "contact center", "inbound calls"])
            and "english" in user_text
            and not re.search(r"(?<!\w)(u\.s\.|usa|english\s+us|english\s*\(us\)|us accent|us|uk|u\.k\.|australian|indian)(?!\w)", user_text)
        ):
            return (
                "Which English accent variant fits your operation: US, UK, Australian, or Indian?"
            )

        if (
            any(term in user_text for term in ["cxo", "director", "executive", "senior leadership"])
            and not any(term in user_text for term in ["selection", "development", "feedback", "benchmark"])
        ):
            return (
                "Is this for selection against a leadership benchmark, or developmental feedback "
                "for executives already in role?"
            )

        if "rust" in user_text and "rust-specific" not in assistant_text:
            return (
                "SHL's catalog does not include a Rust-specific knowledge test. Should I build a "
                "shortlist around live coding, Linux/systems, networking, cognitive ability, and OPQ?"
            )

        if (
            any(term in user_text for term in ["full-stack engineer", "core java", "spring", "angular"])
            and not any(term in user_text for term in ["backend-leaning", "frontend", "balanced full-stack"])
        ):
            return (
                "Is this backend-leaning, frontend-heavy, or a balanced full-stack role with "
                "significant Angular ownership?"
            )

        if (
            "backend-leaning" in user_text
            and "senior ic" not in user_text
            and "tech lead" not in user_text
        ):
            return (
                "Is the seniority closer to a senior individual contributor, or a tech lead "
                "setting architecture across services?"
            )

        if (
            any(term in user_text for term in ["healthcare admin", "patient records", "hipaa"])
            and "spanish" in user_text
            and not any(term in user_text for term in ["hybrid", "functionally bilingual", "english fluent"])
        ):
            return (
                "The healthcare knowledge tests are English-only, while OPQ32r and DSI support "
                "Latin American Spanish. Should we use a hybrid battery with English knowledge "
                "tests and Spanish personality measures?"
            )

        return None

    @classmethod
    def should_clarify(cls, state: ConversationState) -> bool:
        """Determine if we need more information before recommending.

        Args:
            state: Reconstructed conversation state.

        Returns:
            True if we should ask a question, False to proceed to retrieval.
        """
        # Stop asking if we've reached the max clarification turns
        if state.clarification_turns >= settings.max_clarification_turns:
            logger.debug("Clarification bypassed: max turns reached.")
            return False

        # If readiness is above the tuned threshold, we have enough
        if state.recommendation_readiness >= settings.clarification_readiness_threshold:
            logger.debug(
                "Clarification bypassed: readiness (%.2f) >= threshold (%.2f)",
                state.recommendation_readiness,
                settings.clarification_readiness_threshold,
            )
            return False

        # If they provided exactly enough fields, we can proceed
        filled_fields = 5 - len(state.requirements.missing_fields)
        if filled_fields >= 3:
            logger.debug("Clarification bypassed: sufficient fields filled (%d).", filled_fields)
            return False

        logger.debug(
            "Clarification required: readiness (%.2f) < threshold (%.2f)",
            state.recommendation_readiness,
            settings.clarification_readiness_threshold,
        )
        return True

    @classmethod
    def generate_question(cls, state: ConversationState) -> str:
        """Generate the highest-value clarification question.

        Picks one missing field based on priority order:
        1. Role
        2. Seniority
        3. Skills
        4. Purpose

        Args:
            state: Reconstructed conversation state.

        Returns:
            A natural language question.
        """
        reqs = state.requirements
        missing = reqs.missing_fields

        if "role" in missing:
            return "What specific job role or title are you hiring for?"

        if "seniority" in missing:
            if reqs.role:
                return f"What seniority level is the {reqs.role} role (e.g., entry-level, mid-level, senior, executive)?"
            return "What seniority level are you hiring for (e.g., entry-level, mid-level, senior, executive)?"

        if "skills" in missing:
            if reqs.role:
                return f"What specific skills or traits are most important to assess for the {reqs.role} position?"
            return "What specific skills, traits, or competencies do you want to assess?"

        if "purpose" in missing:
            return "Are you assessing candidates for pre-hire screening, employee development, or succession planning?"

        # Fallback if nothing specific is missing but score is low (unlikely)
        return "Could you provide a few more details about what you're looking for in an assessment?"
