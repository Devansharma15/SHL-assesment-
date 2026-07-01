"""Intent Detector — Module 1.

Detects user intent from the latest message and conversation context.
Uses deterministic pattern matching (no LLM call) for low latency.

Purpose:
    Classify what the user wants so the orchestrator can route accordingly.

Inputs:
    - messages: Full conversation history (list of role/content dicts).

Outputs:
    - IntentResult: intent enum, confidence float, reason string.

Dependencies:
    - models.enums.AgentIntent
    - services.guardrails.Guardrails (for injection detection)

Failure Cases:
    - Ambiguous messages → returns UNKNOWN with low confidence
    - Very short messages → may misclassify; orchestrator handles gracefully

Engineering Trade-offs:
    - Deterministic over LLM-based: saves ~500ms latency per request.
    - Pattern matching can miss nuanced intents, but the orchestrator
      compensates with conversation stage context.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from models.enums import AgentIntent

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class IntentResult:
    """Result of intent detection."""

    intent: AgentIntent
    confidence: float  # 0.0 to 1.0
    reason: str


class IntentDetector:
    """Detects user intent from message text and conversation context.

    Classification is fully deterministic — no LLM call required.
    Uses layered detection: injection → off-topic → greeting → comparison →
    refinement → recommendation → unknown.
    """

    # --- Greeting patterns ---
    GREETING_PATTERNS: list[re.Pattern] = [
        re.compile(r"^(hi|hello|hey|good\s+(morning|afternoon|evening)|greetings|howdy)\b", re.I),
        re.compile(r"^(what can you do|how can you help|what do you do)\b", re.I),
        re.compile(r"^(help|start|begin)\s*$", re.I),
    ]

    # --- Comparison signals ---
    COMPARISON_SIGNALS: set[str] = {
        "compare",
        "comparison",
        "difference",
        "differences",
        "versus",
        "vs",
        "vs.",
        "between",
        "which is better",
        "pros and cons",
        "similarities",
        "how does .* compare",
        "better than",
        "worse than",
    }

    _compiled_comparison: list[re.Pattern] = [
        re.compile(rf"\b{s}\b" if " " not in s else s, re.I)
        for s in COMPARISON_SIGNALS
    ]

    # --- Refinement signals ---
    REFINEMENT_SIGNALS: set[str] = {
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
        "actually",
        "update",
        "modify",
    }

    _compiled_refinement: list[re.Pattern] = [
        re.compile(rf"\b{s}\b", re.I) for s in REFINEMENT_SIGNALS
    ]

    # --- Conversation completion signals ---
    COMPLETION_SIGNALS: set[str] = {
        "thanks",
        "thank you",
        "that's all",
        "that is all",
        "thats all",
        "perfect",
        "great, thanks",
        "looks good",
        "i'm done",
        "im done",
        "all good",
        "no more questions",
        "bye",
        "goodbye",
    }

    _compiled_completion: list[re.Pattern] = [
        re.compile(rf"\b{re.escape(s)}\b", re.I) for s in COMPLETION_SIGNALS
    ]

    @classmethod
    def detect(cls, messages: list[dict]) -> IntentResult:
        """Detect the user's intent from conversation history.

        Uses a priority-based detection chain:
        1. Prompt injection (highest priority — safety)
        2. Off-topic detection
        3. Conversation completion
        4. Greeting (first message, short)
        5. Comparison request
        6. Refinement request (requires prior assistant recommendations)
        7. Default: recommendation

        Args:
            messages: Full conversation history.

        Returns:
            IntentResult with classified intent, confidence, and reason.
        """
        if not messages:
            return IntentResult(
                intent=AgentIntent.UNKNOWN,
                confidence=0.0,
                reason="No messages provided.",
            )

        # Extract latest user message
        latest_user_msg = cls._get_latest_user_message(messages)
        if not latest_user_msg:
            return IntentResult(
                intent=AgentIntent.UNKNOWN,
                confidence=0.0,
                reason="No user message found.",
            )

        latest_text = latest_user_msg.strip()
        latest_lower = latest_text.lower()

        # --- 1. Prompt injection check ---
        from services.guardrails import Guardrails

        if Guardrails.check_injection(latest_text):
            return IntentResult(
                intent=AgentIntent.PROMPT_INJECTION,
                confidence=0.95,
                reason="Prompt injection pattern detected.",
            )

        # --- 2. Off-topic check ---
        if Guardrails.check_off_topic(latest_text):
            return IntentResult(
                intent=AgentIntent.OFF_TOPIC,
                confidence=0.90,
                reason="Off-topic query detected.",
            )

        # --- 3. Conversation completion ---
        if cls._is_completion(latest_lower):
            return IntentResult(
                intent=AgentIntent.GREETING,  # Completion uses greeting to end gracefully
                confidence=0.85,
                reason="Conversation completion signal detected.",
            )

        # --- 4. Greeting detection ---
        if cls._is_greeting(latest_text, messages):
            return IntentResult(
                intent=AgentIntent.GREETING,
                confidence=0.90,
                reason="Greeting or opening message detected.",
            )

        # --- 5. Comparison request ---
        if cls._is_comparison(latest_lower):
            return IntentResult(
                intent=AgentIntent.COMPARISON,
                confidence=0.90,
                reason="Comparison keywords detected.",
            )

        # --- 6. Refinement request ---
        if cls._is_refinement(latest_lower, messages):
            return IntentResult(
                intent=AgentIntent.REFINEMENT,
                confidence=0.85,
                reason="Refinement signal detected with prior recommendations.",
            )

        # --- 7. Default: Recommendation ---
        return IntentResult(
            intent=AgentIntent.RECOMMENDATION,
            confidence=0.80,
            reason="Default: user appears to be requesting assessment recommendations.",
        )

    @classmethod
    def _get_latest_user_message(cls, messages: list[dict]) -> str | None:
        """Extract the content of the most recent user message."""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                return msg["content"]
        return None

    @classmethod
    def _is_greeting(cls, text: str, messages: list[dict]) -> bool:
        """Detect greeting intent.

        A greeting is: a short message matching greeting patterns,
        typically at the start of conversation (≤ 2 messages).
        """
        # Only treat as greeting if it's early in the conversation
        user_msg_count = sum(1 for m in messages if m.get("role") == "user")
        if user_msg_count > 1:
            return False

        # Check pattern match
        for pattern in cls.GREETING_PATTERNS:
            if pattern.search(text):
                return True

        # Very short first message with no assessment-related content
        if len(text.split()) <= 3 and user_msg_count == 1:
            assessment_words = {"assess", "test", "hire", "recruit", "candidate", "role", "developer"}
            if not any(w in text.lower() for w in assessment_words):
                return True

        return False

    @classmethod
    def _is_comparison(cls, text_lower: str) -> bool:
        """Detect comparison intent."""
        for pattern in cls._compiled_comparison:
            if pattern.search(text_lower):
                return True
        return False

    @classmethod
    def _is_refinement(cls, text_lower: str, messages: list[dict]) -> bool:
        """Detect refinement intent.

        Requires both: (a) refinement keywords present AND
        (b) prior assistant messages exist (something to refine).
        """
        has_prior_assistant = any(m.get("role") == "assistant" for m in messages)
        if not has_prior_assistant:
            return False

        for pattern in cls._compiled_refinement:
            if pattern.search(text_lower):
                return True
        return False

    @classmethod
    def _is_completion(cls, text_lower: str) -> bool:
        """Detect conversation completion signals."""
        for pattern in cls._compiled_completion:
            if pattern.search(text_lower):
                return True
        return False
