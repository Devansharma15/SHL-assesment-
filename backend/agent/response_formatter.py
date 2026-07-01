"""Response Formatter — Module 12.

Ensures the final response adheres strictly to the required JSON schema.
Handles malformed LLM outputs, missing fields, and enforces constraints.

Purpose:
    Guarantee that the API never crashes due to bad LLM formatting and
    always returns a valid ChatResponse schema.

Inputs:
    - raw_response: Dict parsed from the LLM.
    - is_refusal: Boolean indicating if this is a guardrail refusal.
    - default_reply: Fallback reply text.

Outputs:
    - Validated dict matching ChatResponse schema.

Dependencies:
    - None
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Enforces strict output schema formatting."""

    @classmethod
    def format(
        cls,
        raw_response: Any,
        is_refusal: bool = False,
        is_gathering: bool = False,
        default_reply: str = "I can help you find the right SHL assessments.",
    ) -> dict:
        """Validate and normalize the response structure.
        
        Args:
            raw_response: The dictionary to format.
            is_refusal: If true, forces end_of_conversation to false and clears recs.
            is_gathering: If true, forces end_of_conversation to false and clears recs.
            default_reply: Reply to use if raw_response is missing one.
            
        Returns:
            Dict guaranteed to match ChatResponse schema.
        """
        if not isinstance(raw_response, dict):
            logger.warning("ResponseFormatter received non-dict: %s", type(raw_response))
            raw_response = {"reply": str(raw_response) if raw_response else default_reply}

        # 1. Ensure required fields exist with correct types
        reply = raw_response.get("reply")
        if not reply or not isinstance(reply, str):
            reply = default_reply

        recs = raw_response.get("recommendations", [])
        if not isinstance(recs, list):
            recs = []

        eoc = raw_response.get("end_of_conversation", False)
        if not isinstance(eoc, bool):
            # Try to cast string "true"/"false"
            if isinstance(eoc, str):
                eoc = eoc.lower() == "true"
            else:
                eoc = False

        # 2. Refusal or Gathering override (strict schema enforcement)
        if is_refusal or is_gathering:
            recs = []
            eoc = False

        # 3. Format recommendations
        formatted_recs = []
        for rec in recs:
            if not isinstance(rec, dict):
                continue
                
            name = rec.get("name")
            url = rec.get("url")
            
            # Name and URL are strictly required by the frontend schema
            if not name or not url:
                continue
                
            formatted_rec = {
                "name": str(name),
                "url": str(url),
                "test_type": str(rec.get("test_type", "")),
                "why_recommended": str(rec.get("why_recommended", "")),
                # Note: The agent orchestrator might inject 'confidence' here later
            }
            formatted_recs.append(formatted_rec)

        # 4. Cap at 10 recommendations
        formatted_recs = formatted_recs[:10]

        if formatted_recs:
            names = [rec["name"] for rec in formatted_recs]
            missing_names = [name for name in names if name.lower() not in reply.lower()]
            if missing_names:
                reply = f"{reply}\n\nShortlist: {'; '.join(names)}."

        return {
            "reply": reply,
            "recommendations": formatted_recs,
            "end_of_conversation": eoc,
        }

    @classmethod
    def create_refusal(cls, message: str) -> dict:
        """Create a standard refusal response."""
        return cls.format(
            raw_response={"reply": message},
            is_refusal=True,
        )

    @classmethod
    def create_clarification(cls, question: str) -> dict:
        """Create a clarification response (no recommendations)."""
        return cls.format(
            raw_response={"reply": question},
            is_refusal=False,
            is_gathering=True,
        )

    @classmethod
    def create_greeting(cls, greeting: str = "Hello! I'm the SHL Assessment Advisor. How can I help you evaluate your talent today?") -> dict:
        """Create a standard greeting response."""
        return cls.format(
            raw_response={"reply": greeting},
            is_refusal=False,
            is_gathering=True,
        )

    @classmethod
    def create_no_results(cls, message: str = "I couldn't find any SHL assessments that exactly match those requirements. Could you broaden your criteria?") -> dict:
        """Create a response when retrieval or hallucination guard yields zero results."""
        return cls.format(
            raw_response={"reply": message},
            is_refusal=False,
        )
