"""Pydantic schemas for the chat endpoint."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat message from the user."""
    message: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    file_content: str | None = Field(None, max_length=512_000)
    file_name: str | None = None


class ChatResponse(BaseModel):
    """Agent response back to the user."""
    reply: str
    session_id: str
    tool_calls_made: list[str] = []
