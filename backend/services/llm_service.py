"""LLM service."""

from __future__ import annotations

import asyncio
import importlib
import json
import logging
import re
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

genai: Any = importlib.import_module("google.generativeai")
genai_types: Any = importlib.import_module("google.generativeai.types")


class LLMProviderError(Exception):
    """Raised when an LLM provider fails."""
    pass


class LLMService:
    """Wrapper for LLM API calls using Gemini.
    """

    def __init__(self):
        if settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel(
                    model_name=settings.llm_model,
                )
            except Exception as e:
                logger.warning("Failed to initialize Gemini client: %s", e)
                self.model = None
        else:
            self.model = None

    async def generate(self, system_prompt: str, messages: list[dict]) -> dict:
        """Generate response using Gemini.
        
        Args:
            system_prompt: The complete system prompt (rules + context).
            messages: Conversation history.
            
        Returns:
            Parsed JSON dict guaranteed to contain 'reply', 'recommendations', 'end_of_conversation'.
        """
        if not self.model:
            logger.error("Gemini model not initialized.")
            return self._get_fallback_response()

        raw_text = None
        
        try:
            raw_text = await self._call_gemini(system_prompt, messages)
        except Exception as e:
            logger.warning("Gemini provider failed: %s", e)

        if not raw_text:
            return self._get_fallback_response()

        return self._parse_json_response(raw_text)

    async def _call_gemini(self, system_prompt: str, messages: list[dict]) -> str:
        """Call Gemini API asynchronously."""
        # Convert messages to Gemini format
        gemini_messages = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_messages.append({"role": role, "parts": [msg["content"]]})
            
        generation_config = genai.types.GenerationConfig(
            temperature=settings.llm_temperature,
            max_output_tokens=settings.llm_max_output_tokens,
            response_mime_type="application/json",
        )
        
        safety_settings = {
            genai_types.HarmCategory.HARM_CATEGORY_HARASSMENT: (
                genai_types.HarmBlockThreshold.BLOCK_NONE
            ),
            genai_types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: (
                genai_types.HarmBlockThreshold.BLOCK_NONE
            ),
            genai_types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: (
                genai_types.HarmBlockThreshold.BLOCK_NONE
            ),
            genai_types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: (
                genai_types.HarmBlockThreshold.BLOCK_NONE
            ),
        }

        # We need to run sync gemini client in thread pool
        def _generate():
            # For System prompt in older API we prepend it or pass it in system_instruction
            # generativeai supports system_instruction on GenerativeModel initialization
            # or we can pass it as a user message first. Let's create a specific model instance.
            model = genai.GenerativeModel(
                model_name=settings.llm_model,
                system_instruction=system_prompt
            )
            response = model.generate_content(
                gemini_messages,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            return response.text
            
        return await asyncio.to_thread(_generate)

    @staticmethod
    def _parse_json_response(text: str) -> dict:
        """Parse JSON from LLM response text."""
        if not text:
            return {}

        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*\n?", "", text)
            text = re.sub(r"\n?```\s*$", "", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse LLM JSON response: %s", e)
            
            # Try regex extraction
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            # Fallback wrapper
            return {
                "reply": text,
                "recommendations": [],
                "end_of_conversation": False,
            }

    @staticmethod
    def _get_fallback_response() -> dict:
        """Graceful fallback when all providers fail."""
        return {
            "reply": "I'm currently experiencing technical difficulties connecting to my AI models. Please try again in a moment.",
            "recommendations": [],
            "end_of_conversation": False,
        }


# Singleton
_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    """Get or create the singleton LLMService."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
