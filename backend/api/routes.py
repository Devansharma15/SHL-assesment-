"""API routes for the SHL Assessment Recommender."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from models.schemas import ChatRequest, ChatResponse, HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for deployment readiness probes.

    Returns:
        200 OK with {"status": "ok"}
    """
    return HealthResponse(status="ok")


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """Process a conversational chat request.

    Accepts the full conversation history and returns assessment recommendations,
    clarifying questions, comparisons, or refinements.

    The API is stateless — every request must include the complete conversation history.

    Args:
        request: ChatRequest with messages array.

    Returns:
        ChatResponse with reply, recommendations, and end_of_conversation flag.

    Raises:
        422: If the request body is invalid or conversation exceeds 8 turns.
        500: If an internal error occurs during processing.
        504: If the LLM response times out.
    """
    from app.main import get_chat_service

    try:
        chat_service = get_chat_service()
        response = await chat_service.process_chat(request)
        return response
    except ValueError as e:
        logger.warning("Validation error: %s", e)
        raise HTTPException(status_code=422, detail=str(e))
    except TimeoutError:
        logger.error("Request timed out.")
        raise HTTPException(status_code=504, detail="Request timed out. Please try again.")
    except Exception as e:
        logger.error("Chat processing error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred. Please try again.")
