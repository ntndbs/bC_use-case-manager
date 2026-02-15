"""Chat endpoint for the AI agent."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from schemas.chat import ChatRequest, ChatResponse
from services.agent import run_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Send a message to the AI agent and receive a response."""
    reply, tools_called = await run_agent(
        user_message=payload.message,
        session_id=payload.session_id,
        db=db,
    )

    return ChatResponse(
        reply=reply,
        session_id=payload.session_id,
        tool_calls_made=tools_called,
    )
