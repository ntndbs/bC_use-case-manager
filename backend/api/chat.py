"""Chat endpoint for the AI agent."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from db.database import get_db
from db.models import User
from schemas.chat import ChatRequest, ChatResponse
from services.agent import run_agent, store_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Send a message to the AI agent and receive a response."""
    user_message = payload.message

    # Handle optional file attachment
    if payload.file_content and payload.file_name:
        if not payload.file_name.endswith(".txt"):
            raise HTTPException(status_code=400, detail="Only .txt files are supported")

        size_kb = len(payload.file_content.encode("utf-8")) // 1024
        store_file(payload.session_id, payload.file_name, payload.file_content)
        user_message += f"\n\n[Datei angehängt: {payload.file_name}, {size_kb} KB]"

    reply, tools_called = await run_agent(
        user_message=user_message,
        session_id=payload.session_id,
        db=db,
        user=user,
    )

    return ChatResponse(
        reply=reply,
        session_id=payload.session_id,
        tool_calls_made=tools_called,
    )
