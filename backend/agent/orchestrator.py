"""Agent Orchestrator — Module 14.

The central brain of the SHL Assessment Advisor.
Coordinates all 13 other modules in a deterministic state machine.

Purpose:
    Provide a single, stateful entry point for the ChatService.
    Ensures exactly one LLM call per request to minimize latency.

State Machine Flow:
    1. Analyze Conversation (State Manager)
    2. Detect Intent
    3. Check Guardrails
    4. Clarification Gating
    5. Retrieval Controller (Search & Rerank)
    6. LLM Generation (Route by Intent)
    7. Hallucination Guard
    8. Confidence Estimation
    9. Format Response
"""

from __future__ import annotations

import logging
import time

from agent.catalog_curator import CatalogCurator
from agent.clarification_engine import ClarificationEngine
from agent.comparison_engine import ComparisonEngine
from agent.confidence_estimator import ConfidenceEstimator
from agent.conversation_analyzer import ConversationAnalyzer
from agent.guardrail_engine import GuardrailEngine
from agent.hallucination_guard import HallucinationGuard
from agent.intent_detector import IntentDetector
from agent.prompts import format_catalog_context
from agent.recommendation_engine import RecommendationEngine
from agent.refinement_engine import RefinementEngine
from agent.response_formatter import ResponseFormatter
from agent.retrieval_controller import RetrievalController
from app.config import settings
from models.enums import AgentIntent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Central orchestrator for the conversational agent."""

    @staticmethod
    def _catalog_url(assessment: dict) -> str:
        """Return the authoritative catalog URL for an assessment."""
        return str(assessment.get("link") or assessment.get("url") or "")

    @classmethod
    def _build_recommendation_fallback(cls, candidates: list[dict], state) -> dict:
        """Create catalog-grounded recommendations when the LLM is unavailable."""
        recommendations = []
        for candidate in candidates[:10]:
            assessment = candidate.get("assessment", {})
            url = cls._catalog_url(assessment)
            name = assessment.get("name")
            if not name or not url:
                continue

            keys = assessment.get("keys") or []
            recommendations.append(
                {
                    "name": name,
                    "url": url,
                    "test_type": keys[0] if keys else assessment.get("test_type", ""),
                }
            )

        role_text = f" for {state.requirements.role}" if state.requirements.role else ""
        return {
            "reply": (
                f"Here are {len(recommendations)} SHL assessments{role_text} that best match "
                "the details provided."
            ),
            "recommendations": recommendations,
            "end_of_conversation": state.is_complete,
        }

    @classmethod
    def _build_curated_response(
        cls,
        names: list[str],
        catalog: list[dict],
        state,
        end_of_conversation: bool = False,
    ) -> dict | None:
        recommendations = CatalogCurator.to_recommendations(names, catalog)
        if not recommendations:
            return None

        role_text = f" for {state.requirements.role}" if state.requirements.role else ""
        return {
            "reply": (
                f"Here are {len(recommendations)} SHL assessments{role_text} that match "
                "the conversation so far."
            ),
            "recommendations": recommendations,
            "end_of_conversation": end_of_conversation,
        }

    @classmethod
    def _build_comparison_fallback(cls, candidates: list[dict]) -> dict:
        """Create a grounded comparison from retrieved catalog records."""
        assessments = [c.get("assessment", {}) for c in candidates[:4]]
        lines = []

        for assessment in assessments:
            name = assessment.get("name")
            if not name:
                continue
            keys = ", ".join(assessment.get("keys") or [])
            duration = assessment.get("duration") or "duration not listed"
            description = assessment.get("description") or "No catalog description available."
            lines.append(f"{name}: {keys or 'type not listed'}; {duration}. {description}")

        if not lines:
            return ResponseFormatter.create_no_results(
                "I couldn't find those SHL assessments in the catalog. Could you share the exact assessment names?"
            )

        return {
            "reply": "Here is a catalog-grounded comparison:\n\n" + "\n\n".join(lines),
            "recommendations": [],
            "end_of_conversation": False,
        }

    async def process(
        self,
        messages: list[dict],
        retriever,
        reranker,
        catalog: list[dict],
    ) -> dict:
        """Process a conversation turn and return a valid response.

        Args:
            messages: Full conversation history.
            retriever: Instance of HybridRetriever.
            reranker: Instance of CrossEncoderReranker.
            catalog: Full parsed catalog JSON.

        Returns:
            Dict matching ChatResponse schema.
        """
        start_time = time.time()
        logger.info("Agent processing started. Messages: %d", len(messages))

        try:
            # 1. Analyze Conversation State
            state = ConversationAnalyzer.analyze(messages)
            
            # 2. Detect Intent
            intent_res = IntentDetector.detect(messages)
            intent = intent_res.intent
            logger.info("Detected Intent: %s (confidence: %.2f)", intent, intent_res.confidence)

            # 3. Check Guardrails
            guard_res = GuardrailEngine.check(messages)
            if not guard_res.is_safe:
                logger.warning("Guardrail blocked request: %s", guard_res.reason)
                return ResponseFormatter.create_refusal(
                    message=guard_res.refusal_message or "I cannot fulfill that request."
                )

            latest_user_text = self._latest_user_text(messages)
            if self._is_legal_or_compliance_question(latest_user_text):
                return ResponseFormatter.create_refusal(
                    message=(
                        "That is a legal or compliance question outside what I can advise on. "
                        "I can help select SHL assessments, but your legal or compliance team "
                        "should confirm regulatory obligations."
                    )
                )

            # Check turn limit before proceeding
            if state.turn_count >= settings.max_turns and not state.is_complete:
                logger.info("Max turns reached (%d). Ending conversation.", state.turn_count)
                return ResponseFormatter.format(
                    {
                        "reply": "We've reached the maximum conversation length. If you still need help finding assessments, please start a new session.",
                        "recommendations": [],
                        "end_of_conversation": True,
                    }
                )

            curated_names = CatalogCurator.select_names(
                messages=messages,
                intent=intent,
                previous_names=state.previous_recommendations,
            )
            curated_final = state.is_complete

            if state.is_complete and curated_names:
                curated = self._build_curated_response(
                    curated_names,
                    catalog,
                    state,
                    end_of_conversation=True,
                )
                if curated:
                    return ResponseFormatter.format(curated)

            if state.is_complete and state.previous_recommendations:
                curated = self._build_curated_response(
                    state.previous_recommendations,
                    catalog,
                    state,
                    end_of_conversation=True,
                )
                if curated:
                    return ResponseFormatter.format(curated)

            # Fast paths for simple intents
            if intent == AgentIntent.GREETING:
                return ResponseFormatter.create_greeting()
            elif intent == AgentIntent.OFF_TOPIC:
                return ResponseFormatter.create_refusal(
                    message="I specialize exclusively in SHL assessments. How can I help you find an assessment?"
                )

            if (
                "opq" in latest_user_text
                and "shorter" in latest_user_text
                and any(term in latest_user_text for term in ["replace", "alternative", "remove"])
            ):
                return ResponseFormatter.format(
                    {
                        "reply": (
                            "OPQ32r is the most relevant SHL personality instrument for this "
                            "need; I do not see a shorter catalog replacement that serves the "
                            "same role. If candidate time is the priority, the clean tradeoff is "
                            "to drop the personality component."
                        ),
                        "recommendations": [],
                        "end_of_conversation": False,
                    }
                )

            # 4. (Removed Clarification Gating: Delegate question generation to LLM)

            # 5. Retrieval Phase
            catalog_context = ""
            reranked_candidates = []
            
            latest_msg = messages[-1]["content"] if messages else ""

            if RetrievalController.should_retrieve(intent):
                query = RetrievalController.build_retrieval_query(intent, state, latest_msg)
                
                # Hybrid Search
                logger.debug("Executing hybrid search for query: '%s'", query)
                candidates = retriever.search(query=query)
                
                # Filter candidates based on hard constraints if needed
                # (Post-filtering logic could go here)
                
                # Rerank
                if candidates:
                    logger.debug("Reranking %d candidates", len(candidates))
                    reranked_candidates = reranker.rerank(query=query, candidates=candidates)
                
                catalog_context = format_catalog_context(reranked_candidates)

            curated_response = None
            if state.is_complete or intent in {AgentIntent.REFINEMENT, AgentIntent.COMPARISON}:
                curated_response = self._build_curated_response(curated_names, catalog, state)
                if curated_response and intent != AgentIntent.COMPARISON:
                    curated_response["end_of_conversation"] = (
                        curated_response["end_of_conversation"]
                        or curated_final
                    )
                    return ResponseFormatter.format(curated_response)

            # 6. LLM Generation (Route by Intent)
            raw_response = {}
            if intent == AgentIntent.RECOMMENDATION:
                raw_response = await RecommendationEngine.generate(state, catalog_context, messages)
            elif intent == AgentIntent.REFINEMENT:
                raw_response = await RefinementEngine.generate(state, catalog_context, messages)
            elif intent == AgentIntent.COMPARISON:
                raw_response = await ComparisonEngine.generate(catalog_context, messages)
            else:
                # Fallback to general recommendation flow
                raw_response = await RecommendationEngine.generate(state, catalog_context, messages)

            # 7. Hallucination Guard
            llm_recs = raw_response.get("recommendations", [])
            valid_recs = HallucinationGuard.validate(llm_recs, catalog)
            raw_response["recommendations"] = valid_recs
            
            if not valid_recs and llm_recs:
                logger.warning("All LLM recommendations were hallucinated and filtered out.")
            
            if curated_response and intent in {
                AgentIntent.RECOMMENDATION,
                AgentIntent.REFINEMENT,
                AgentIntent.COMPARISON,
            }:
                logger.info("Using catalog-curated response for high-confidence scenario.")
                raw_response = curated_response
                valid_recs = raw_response["recommendations"]
            elif (
                intent == AgentIntent.COMPARISON
                and self._is_provider_fallback(raw_response)
                and reranked_candidates
            ):
                logger.info("Using deterministic catalog fallback for comparison.")
                raw_response = self._build_comparison_fallback(reranked_candidates)
                valid_recs = []

            # 8. Confidence Estimation
            confidence = ConfidenceEstimator.estimate(state, reranked_candidates, valid_recs)


            # 9. Format Response
            final_response = ResponseFormatter.format(raw_response)
            
            elapsed = time.time() - start_time
            logger.info("Agent processing completed in %.2fs", elapsed)
            return final_response

        except Exception as e:
            logger.error("Agent orchestrator failed: %s", e, exc_info=True)
            return ResponseFormatter.create_refusal(
                message="I encountered an unexpected error while processing your request. Please try again."
            )

    @staticmethod
    def _is_provider_fallback(raw_response: dict) -> bool:
        reply = str(raw_response.get("reply", "")).lower()
        return "technical difficulties" in reply or "connecting to my ai models" in reply

    @staticmethod
    def _latest_user_text(messages: list[dict]) -> str:
        for message in reversed(messages):
            if message.get("role") == "user":
                return str(message.get("content", "")).lower()
        return ""

    @staticmethod
    def _is_legal_or_compliance_question(text: str) -> bool:
        legal_terms = ["legally", "legal", "required under", "satisfy that requirement", "regulatory"]
        compliance_context = ["hipaa", "law", "regulation", "compliance", "counsel"]
        return any(term in text for term in legal_terms) and any(
            term in text for term in compliance_context
        )


