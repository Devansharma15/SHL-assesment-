"""Pydantic models for request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class Message(BaseModel):
    """A single message in the conversation."""

    role: str = Field(..., pattern="^(user|assistant)$", description="Message role")
    content: str = Field(..., min_length=1, max_length=5000, description="Message content")


class ChatRequest(BaseModel):
    """Request body for POST /chat."""

    messages: list[Message] = Field(..., min_length=1, description="Conversation history")

    @field_validator("messages")
    @classmethod
    def validate_turn_count(cls, v: list[Message]) -> list[Message]:
        # Max 8 turns = 16 messages (user + assistant per turn)
        if len(v) > 16:
            raise ValueError(
                "Maximum conversation length of 8 turns exceeded. Please start a new conversation."
            )
        return v

    @field_validator("messages")
    @classmethod
    def validate_first_message_is_user(cls, v: list[Message]) -> list[Message]:
        if v and v[0].role != "user":
            raise ValueError("First message must be from the user.")
        return v


class Recommendation(BaseModel):
    """A single assessment recommendation."""

    name: str = Field(..., description="Assessment name")
    url: str = Field(..., description="SHL product page URL")
    test_type: str = Field(..., description="Type of assessment")


class ChatResponse(BaseModel):
    """Response body for POST /chat."""

    reply: str = Field(..., description="Assistant's text reply")
    recommendations: list[Recommendation] = Field(
        default_factory=list, description="Assessment recommendations (0-10)"
    )
    end_of_conversation: bool = Field(False, description="Whether the conversation is complete")

    @field_validator("recommendations")
    @classmethod
    def validate_recommendation_count(cls, v: list[Recommendation]) -> list[Recommendation]:
        if len(v) > 10:
            raise ValueError("Maximum of 10 recommendations per response.")
        return v


class HealthResponse(BaseModel):
    """Response body for GET /health."""

    status: str = Field(default="ok", description="Service status")


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str = Field(..., description="Error message")
