"""Pydantic schemas for Transcript."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TranscriptBase(BaseModel):
    """Base schema with shared attributes."""
    filename: str
    company_id: int


class TranscriptCreate(TranscriptBase):
    """Schema for creating a transcript."""
    content: str


class TranscriptResponse(TranscriptBase):
    """Schema for API responses."""
    id: int
    created_at: datetime
    uploaded_by_id: int | None = None
    
    model_config = ConfigDict(from_attributes=True)


class TranscriptWithContent(TranscriptResponse):
    """Transcript including full content."""
    content: str