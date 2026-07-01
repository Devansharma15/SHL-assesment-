"""Conversation Analyzer — Modules 2 + 9 (Conversation Analyzer + State Manager).

Reconstructs full conversation state from the stateless message history.
Combines entity extraction, stage detection, and readiness estimation.

Purpose:
    On every request, rebuild the complete conversation context from scratch.
    The API is stateless — no memory persists between calls.

Inputs:
    - messages: Full conversation history (list of role/content dicts).

Outputs:
    - ConversationState dataclass with all derived state fields.

Dependencies:
    - agent.requirement_extractor.RequirementExtractor
    - agent.requirement_extractor.HiringRequirements
    - models.enums.ConversationStage

Failure Cases:
    - Very long conversations may have redundant info — handled gracefully.
    - Conflicting requirements across turns — last mention wins.

Engineering Trade-offs:
    - Full re-analysis per request (no caching) trades CPU for correctness.
    - Single pass over messages is O(n) — fast enough for ≤16 messages.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from agent.requirement_extractor import HiringRequirements, RequirementExtractor
from models.enums import ConversationStage

logger = logging.getLogger(__name__)


@dataclass
class ConversationState:
    """Complete reconstructed state of the current conversation."""

    # --- Extracted requirements ---
    requirements: HiringRequirements = field(default_factory=HiringRequirements)

    # --- Conversation metadata ---
    turn_count: int = 0  # Number of user messages
    total_messages: int = 0
    stage: ConversationStage = ConversationStage.GREETING
    is_first_message: bool = True

    # --- Previous recommendations ---
    previous_recommendations: list[str] = field(default_factory=list)
    has_received_recommendations: bool = False

    # --- Clarification tracking ---
    clarification_turns: int = 0  # How many times we've asked for clarification

    # --- Completion ---
    is_complete: bool = False

    @property
    def recommendation_readiness(self) -> float:
        """Score 0.0–1.0 indicating readiness to make recommendations.

        Combines requirement completeness with conversation context.
        Higher values mean we have enough info to retrieve and recommend.
        """
        base = self.requirements.completeness_score

        # Bonus: if user has been very specific in a single message
        if self.turn_count == 1 and base >= 0.35:
            base = min(base + 0.15, 1.0)

        # Bonus: if we've already asked clarification questions
        if self.clarification_turns >= 2:
            base = min(base + 0.20, 1.0)

        # If user provided 3+ requirement fields, they gave enough context
        filled = 5 - len(self.requirements.missing_fields)
        if filled >= 3:
            base = max(base, 0.50)

        return base


class ConversationAnalyzer:
    """Reconstructs conversation state from the full message history.

    Stateless — analyzes the complete message list on every call.
    No data persists between requests.
    """

    # Completion signal patterns
    COMPLETION_PATTERNS: list[re.Pattern] = [
        re.compile(r"\b(thanks|thank you|thank\s+u)\b", re.I),
        re.compile(r"\b(that'?s?\s+all|that\s+is\s+all)\b", re.I),
        re.compile(r"\b(perfect|great|looks?\s+good|awesome|excellent)\b", re.I),
        re.compile(r"\b(i'?m\s+done|no\s+more|nothing\s+else)\b", re.I),
        re.compile(r"\b(bye|goodbye|see\s+you)\b", re.I),
    ]

    @classmethod
    def analyze(cls, messages: list[dict]) -> ConversationState:
        """Analyze full conversation history and reconstruct state.

        Args:
            messages: Complete message history.

        Returns:
            Fully reconstructed ConversationState.
        """
        state = ConversationState()
        state.total_messages = len(messages)

        if not messages:
            return state

        # Count user messages
        user_messages = [m for m in messages if m.get("role") == "user"]
        assistant_messages = [m for m in messages if m.get("role") == "assistant"]
        state.turn_count = len(user_messages)
        state.is_first_message = state.turn_count <= 1

        # Extract requirements from all user messages
        state.requirements = RequirementExtractor.extract(messages)

        # Extract previous recommendations from assistant messages
        state.previous_recommendations = cls._extract_previous_recommendations(
            assistant_messages
        )
        state.has_received_recommendations = len(state.previous_recommendations) > 0

        # Count clarification turns (assistant messages that are questions without recommendations)
        state.clarification_turns = cls._count_clarification_turns(assistant_messages)

        # Detect completion
        if user_messages:
            latest = user_messages[-1]["content"]
            state.is_complete = cls._is_completion_signal(latest)

        # Determine conversation stage
        state.stage = cls._determine_stage(state)

        logger.debug(
            "Conversation state: stage=%s, turns=%d, readiness=%.2f, "
            "has_recs=%s, complete=%s",
            state.stage,
            state.turn_count,
            state.recommendation_readiness,
            state.has_received_recommendations,
            state.is_complete,
        )

        return state

    @classmethod
    def _extract_previous_recommendations(cls, assistant_messages: list[dict]) -> list[str]:
        """Extract assessment names mentioned in previous assistant responses."""
        recommendations: list[str] = []

        for msg in assistant_messages:
            content = msg.get("content", "")
            # Look for assessment-like names (capitalized phrases, often with parentheses)
            # This is a heuristic — the orchestrator uses the LLM's structured output
            name_patterns = [
                re.compile(r'(?:"name":\s*")(.*?)(?:")', re.I),
                re.compile(r"\*\*(.*?)\*\*"),  # Bold names in markdown
                re.compile(r"(?:^|\n)\d+\.\s+(.+?)(?:\n|$)"),  # Numbered lists
                re.compile(r"Shortlist:\s*(.+?)(?:\.|$)", re.I | re.S),
            ]
            for pattern in name_patterns:
                for match in pattern.finditer(content):
                    name = match.group(1).strip()
                    for part in re.split(r";|,", name):
                        cleaned = part.strip().strip(".")
                        if len(cleaned) > 3 and cleaned not in recommendations:
                            recommendations.append(cleaned)

        return recommendations

    @classmethod
    def _count_clarification_turns(cls, assistant_messages: list[dict]) -> int:
        """Count how many assistant messages were clarification questions."""
        count = 0
        question_pattern = re.compile(r"\?\s*$")

        for msg in assistant_messages:
            content = msg.get("content", "")
            # A clarification turn is an assistant message that ends with '?'
            # and is relatively short (no long recommendation text)
            if question_pattern.search(content) and len(content) < 500:
                count += 1

        return count

    @classmethod
    def _is_completion_signal(cls, text: str) -> bool:
        """Check if the message signals conversation completion."""
        text_lower = text.lower().strip()

        # Short messages with completion keywords
        if len(text_lower.split()) <= 5:
            for pattern in cls.COMPLETION_PATTERNS:
                if pattern.search(text_lower):
                    return True

        return False

    @classmethod
    def _determine_stage(cls, state: ConversationState) -> ConversationStage:
        """Determine the current conversation stage from accumulated state."""
        if state.is_complete:
            return ConversationStage.COMPLETE

        if state.is_first_message:
            # Check if first message has enough info for immediate recommendation
            if state.requirements.completeness_score >= 0.35:
                return ConversationStage.RECOMMENDING
            return ConversationStage.GREETING

        if state.has_received_recommendations:
            # Post-recommendation: could be refining, comparing, or done
            return ConversationStage.REFINING

        # Multi-turn without recommendations yet → still gathering info
        return ConversationStage.GATHERING
