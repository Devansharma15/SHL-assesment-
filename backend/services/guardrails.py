"""Guardrails module for input validation and prompt injection defense."""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


class Guardrails:
    """Input validation and safety guardrails for the chat API.

    Defends against:
    - Prompt injection attacks
    - Off-topic queries
    - Malicious input patterns
    - Excessive input length
    """

    # Prompt injection patterns (case-insensitive)
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"ignore\s+(all\s+)?above",
        r"disregard\s+(all\s+)?previous",
        r"forget\s+(all\s+)?previous",
        r"system\s*prompt",
        r"reveal\s+(your\s+)?instructions",
        r"show\s+(me\s+)?(your\s+)?prompt",
        r"what\s+are\s+your\s+instructions",
        r"act\s+as\s+(a\s+)?(?!recruiter|hr)",  # "act as X" where X is not recruiter/HR
        r"pretend\s+(to\s+be|you\s+are)",
        r"you\s+are\s+now\s+(?!helping)",
        r"jailbreak",
        r"DAN\s+mode",
        r"developer\s+mode",
        r"bypass\s+(safety|filter|restriction)",
        r"override\s+(your|the)\s+(rules|instructions|system)",
    ]

    # Compiled patterns for efficiency
    _compiled_patterns = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

    # Off-topic indicators (queries clearly unrelated to assessments)
    OFF_TOPIC_PATTERNS = [
        r"(?:write|generate|create)\s+(?:me\s+)?(?:a\s+)?(?:\w+\s+)*(?:code|script|program|essay|poem|story)",
        r"(?:how|what)(?:\s+(?:do|does|is|are)|'s)?\s+(?:the\s+)?(?:weather|stock|crypto|bitcoin)",
        r"(?:translate|convert)\s+(?:this|the\s+following)\s+(?:to|into)",
        r"(?:play|tell)\s+(?:me\s+)?(?:a\s+)?(?:game|joke|riddle)",
        r"(?:legal|medical)\s+advice",
        r"(?:hire|fire|terminate)\s+(?:this|the)\s+(?:person|candidate|employee)",
    ]

    _compiled_off_topic = [re.compile(p, re.IGNORECASE) for p in OFF_TOPIC_PATTERNS]

    @classmethod
    def check_injection(cls, text: str) -> bool:
        """Check if the text contains prompt injection patterns.

        Args:
            text: User message text.

        Returns:
            True if injection detected, False otherwise.
        """
        for pattern in cls._compiled_patterns:
            if pattern.search(text):
                logger.warning("Prompt injection detected: %s", pattern.pattern)
                return True
        return False

    @classmethod
    def check_off_topic(cls, text: str) -> bool:
        """Check if the query is clearly off-topic.

        Args:
            text: User message text.

        Returns:
            True if off-topic detected, False otherwise.
        """
        for pattern in cls._compiled_off_topic:
            if pattern.search(text):
                logger.info("Off-topic query detected: %s", pattern.pattern)
                return True
        return False

    @classmethod
    def validate_input(cls, messages: list[dict]) -> dict | None:
        """Validate the full message list for safety issues.

        Args:
            messages: List of message dicts with 'role' and 'content'.

        Returns:
            None if valid, or a dict with 'blocked' reason if validation fails.
        """
        if not messages:
            return {
                "blocked": True,
                "reason": "empty_messages",
                "reply": "Please provide a message to get started.",
            }

        # Check the latest user message for injection
        latest_user_msg = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                latest_user_msg = msg["content"]
                break

        if not latest_user_msg:
            return {
                "blocked": True,
                "reason": "no_user_message",
                "reply": "Please ask a question about SHL assessments.",
            }

        # Check for whitespace-only messages
        if not latest_user_msg.strip():
            return {
                "blocked": True,
                "reason": "empty_content",
                "reply": "Please provide a message to get started.",
            }

        # Check for prompt injection
        if cls.check_injection(latest_user_msg):
            return {
                "blocked": True,
                "reason": "injection_detected",
                "reply": (
                    "I'm designed specifically to help you find the right SHL assessments "
                    "for your hiring needs. How can I assist you with assessment selection?"
                ),
            }

        # Check for off-topic queries
        if cls.check_off_topic(latest_user_msg):
            return {
                "blocked": True,
                "reason": "off_topic",
                "reply": (
                    "I specialize in SHL assessment recommendations for talent evaluation. "
                    "I'm not able to help with that particular request, but I'd be happy to help "
                    "you find the right assessments for your hiring needs. What role are you "
                    "looking to fill?"
                ),
            }

        return None  # Valid input

    @classmethod
    def get_refusal_response(cls) -> dict:
        """Get a standard refusal response for blocked requests."""
        return {
            "reply": (
                "I'm designed specifically to help you find the right SHL assessments. "
                "How can I assist you with assessment selection today?"
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }
