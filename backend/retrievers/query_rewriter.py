"""Query rewriter that extracts intent and builds enriched search queries from conversation context."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class QueryRewriter:
    """Extracts the effective search query from multi-turn conversation context.

    For a stateless API where each request carries the full conversation history,
    the query rewriter synthesizes the latest user intent by combining:
    - The most recent user message
    - Key entities from prior turns (job role, seniority, skills)
    - Refinement context from assistant responses

    This is done heuristically (no LLM call) to keep latency low.
    """

    # Keywords that signal a refinement or modification of prior recommendations
    REFINEMENT_SIGNALS = {
        "add",
        "also",
        "include",
        "additionally",
        "plus",
        "more",
        "remove",
        "exclude",
        "without",
        "drop",
        "less",
        "instead",
        "rather",
        "change",
        "switch",
        "replace",
        "what about",
        "how about",
        "can you also",
    }

    # Keywords that signal a comparison request
    COMPARISON_SIGNALS = {
        "compare",
        "difference",
        "versus",
        "vs",
        "between",
        "which is better",
        "pros and cons",
        "similarities",
    }

    @staticmethod
    def extract_latest_query(messages: list[dict]) -> str:
        """Extract the most recent user message as the base query."""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                return msg["content"].strip()
        return ""

    @staticmethod
    def extract_conversation_context(messages: list[dict]) -> dict:
        """Extract key context from the full conversation history.

        Returns a dict with extracted entities like job_role, seniority,
        skills_mentioned, and assessment_types.
        """
        context = {
            "job_role": None,
            "seniority": None,
            "skills_mentioned": [],
            "assessment_types": [],
            "all_user_messages": [],
        }

        seniority_keywords = {
            "entry": "Entry Level",
            "junior": "Entry Level",
            "graduate": "Entry Level",
            "mid": "Mid Level",
            "intermediate": "Mid Level",
            "senior": "Senior",
            "lead": "Senior",
            "executive": "Executive",
            "director": "Executive",
            "manager": "Senior",
            "c-suite": "Executive",
            "vp": "Executive",
        }

        assessment_keywords = {
            "cognitive": "Cognitive Ability",
            "personality": "Personality Assessment",
            "behavioral": "Behavioral Assessment",
            "coding": "Skills Simulation",
            "technical": "Knowledge Test",
            "simulation": "Skills Simulation",
            "situational": "Behavioral Assessment",
            "leadership": "Leadership",
            "interview": "Interview",
        }

        for msg in messages:
            if msg.get("role") != "user":
                continue

            content = msg["content"].lower()
            context["all_user_messages"].append(msg["content"])

            # Extract seniority
            for keyword, level in seniority_keywords.items():
                if keyword in content and not context["seniority"]:
                    context["seniority"] = level

            # Extract assessment type preferences
            for keyword, atype in assessment_keywords.items():
                if keyword in content and atype not in context["assessment_types"]:
                    context["assessment_types"].append(atype)

        return context

    @classmethod
    def is_comparison_request(cls, query: str) -> bool:
        """Check if the query is a comparison request."""
        query_lower = query.lower()
        return any(signal in query_lower for signal in cls.COMPARISON_SIGNALS)

    @classmethod
    def is_refinement_request(cls, query: str) -> bool:
        """Check if the query is a refinement of previous recommendations."""
        query_lower = query.lower()
        return any(signal in query_lower for signal in cls.REFINEMENT_SIGNALS)

    @classmethod
    def build_search_query(cls, messages: list[dict]) -> str:
        """Build an enriched search query from the full conversation context.

        Combines the latest user message with relevant context from prior turns
        to produce a comprehensive search query for the retriever.

        Args:
            messages: Full conversation history (list of role/content dicts).

        Returns:
            Enriched search query string.
        """
        latest_query = cls.extract_latest_query(messages)
        if not latest_query:
            return ""

        # For comparison requests, use the query directly
        if cls.is_comparison_request(latest_query):
            return latest_query

        # Extract context from history
        context = cls.extract_conversation_context(messages)

        # Build enriched query
        query_parts = [latest_query]

        # Add seniority context if not already in the query
        if context["seniority"] and context["seniority"].lower() not in latest_query.lower():
            query_parts.append(context["seniority"])

        # Add assessment type preferences if not in query
        for atype in context["assessment_types"]:
            if atype.lower() not in latest_query.lower():
                query_parts.append(atype)

        enriched_query = " ".join(query_parts)
        logger.debug("Query rewritten: '%s' -> '%s'", latest_query, enriched_query)

        return enriched_query
