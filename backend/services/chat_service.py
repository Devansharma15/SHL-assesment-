"""Chat service coordinating the agent orchestrator."""

from __future__ import annotations

import logging

from agent.orchestrator import AgentOrchestrator
from retrievers.hybrid_retriever import HybridRetriever
from retrievers.reranker import CrossEncoderReranker
from models.schemas import ChatResponse, Recommendation

logger = logging.getLogger(__name__)


class ChatService:
    """Thin adapter service handling the chat API requests.
    
    Delegates all cognitive and orchestration logic to the AgentOrchestrator.
    """

    def __init__(
        self,
        retriever: HybridRetriever,
        reranker: CrossEncoderReranker,
        catalog: list[dict],
        orchestrator: AgentOrchestrator,
    ):
        self.retriever = retriever
        self.reranker = reranker
        self.catalog = catalog
        self.orchestrator = orchestrator

    async def process_chat(self, request) -> ChatResponse:
        """Process an incoming chat request using the Agent Orchestrator.

        Args:
            request: Validated ChatRequest with conversation history.

        Returns:
            Dictionary matching the ChatResponse schema.
        """
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        if not messages:
            return ChatResponse(
                reply="How can I help you today?",
                recommendations=[],
                end_of_conversation=False,
            )

        # Delegate entirely to the orchestrator
        agent_response = await self.orchestrator.process(
            messages=messages,
            retriever=self.retriever,
            reranker=self.reranker,
            catalog=self.catalog,
        )
        
        # Convert standard dictionary to Pydantic model response
        final_recommendations = []
        for r in agent_response.get("recommendations", []):
            test_type = r.get("test_type")
            if test_type is None:
                test_type = ""
            
            final_recommendations.append(Recommendation(
                name=r.get("name", ""),
                url=r.get("url", ""),
                test_type=test_type,
            ))

        return ChatResponse(
            reply=agent_response.get("reply", "How can I help you find the right SHL assessment?"),
            recommendations=final_recommendations,
            end_of_conversation=agent_response.get("end_of_conversation", False),
        )
