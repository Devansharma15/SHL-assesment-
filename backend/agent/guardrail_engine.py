"""Guardrail Engine — Module 10.

Detects prompt injection, off-topic queries, and malicious intent.
Wraps and extends the existing guardrails service.

Purpose:
    Protect the agent from malicious prompts, role overrides, and
    ensure responses stay within the HR assessment domain.

Inputs:
    - messages: Full conversation history.

Outputs:
    - GuardrailResult with safe flag and reason.

Dependencies:
    - services.guardrails.Guardrails
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from services.guardrails import Guardrails

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class GuardrailResult:
    """Result of the guardrail check."""

    is_safe: bool
    reason: str = ""
    refusal_message: str = ""


class GuardrailEngine:
    """Enforces safety and domain constraints on user inputs."""

    # Additional patterns beyond the base Guardrails service
    EXTENDED_INJECTION_PATTERNS = [
        re.compile(r"\b(competitor|other\s+provider|workday|hirevue|pymetrics|korn\s+ferry|dismantl|testgorilla)\b", re.I),
        re.compile(r"\b(what\s+(is|are)\s+(your|the)\s+core\s+instruction)\b", re.I),
        re.compile(r"print\s+(your\s+)?(initial\s+)?(prompt|instruction|core\s+instruction)", re.I),
    ]

    @classmethod
    def check(cls, messages: list[dict]) -> GuardrailResult:
        """Check conversation history against safety and domain rules.

        Args:
            messages: Full conversation history.

        Returns:
            GuardrailResult indicating safety status.
        """
        # Run the existing robust guardrail validation
        validation = Guardrails.validate_input(messages)
        
        if validation and validation.get("blocked"):
            return GuardrailResult(
                is_safe=False,
                reason=validation.get("reason", "blocked_by_base_guardrail"),
                refusal_message=validation.get("reply", "I cannot fulfill that request."),
            )

        # Run extended checks on the latest user message
        latest_user_msg = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                latest_user_msg = msg["content"]
                break

        if latest_user_msg:
            # Competitor check
            for pattern in cls.EXTENDED_INJECTION_PATTERNS:
                if pattern.search(latest_user_msg):
                    logger.warning("Extended guardrail violation: %s", pattern.pattern)
                    return GuardrailResult(
                        is_safe=False,
                        reason="competitor_or_instruction_extraction",
                        refusal_message=(
                            "I'm specifically designed to recommend and discuss SHL assessments. "
                            "How can I help you find the right SHL assessment for your needs?"
                        ),
                    )

            # Gibberish check
            cleaned_msg = re.sub(r'[^a-zA-Z]', '', latest_user_msg).lower()
            if cleaned_msg:
                known_words = {
                    "hi", "hello", "hey", "yes", "yep", "no", "nope", "ok", "okay", "done", 
                    "opq", "shl", "hr", "ic", "vp", "ceo", "cto", "cfo", "dev", "qa", "ux", 
                    "ui", "api", "aws", "gcp", "sql", "ai", "ml", "us", "uk", "eu", "bot", 
                    "cpa", "job", "role", "app", "web", "sys", "net", "ops", "cxo", "sv",
                    "any", "all", "na", "n/a", "none"
                }
                if len(cleaned_msg) <= 4 and cleaned_msg not in known_words:
                    vowels = set("aeiouy")
                    has_vowel = any(c in vowels for c in cleaned_msg)
                    is_repeating = len(set(cleaned_msg)) == 1
                    is_known_gibberish = cleaned_msg in {"fef", "sf", "asdf", "fdsa", "qwer", "rewq"}
                    
                    if not has_vowel or is_repeating or is_known_gibberish:
                        logger.warning("Gibberish detected: %s", latest_user_msg)
                        return GuardrailResult(
                            is_safe=False,
                            reason="gibberish_detected",
                            refusal_message="I didn't quite catch that. Could you please clarify your response?",
                        )

        # All clear
        return GuardrailResult(is_safe=True)
