"""SHL Assessment Advisor — AI Agent Package.

This package contains the modular orchestration agent responsible for:
- Intent detection and conversation analysis
- Clarification planning and requirement extraction
- Retrieval orchestration and recommendation generation
- Refinement, comparison, and guardrail enforcement
- Hallucination prevention and response formatting

Single public interface:
    from agent import AgentOrchestrator
    result = await orchestrator.process(messages, retriever, reranker, catalog)
"""

from agent.orchestrator import AgentOrchestrator

__all__ = ["AgentOrchestrator"]
