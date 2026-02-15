"""Pydantic schemas for Transcript."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from schemas.use_case import UseCaseResponse


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


class TranscriptWithUseCases(TranscriptResponse):
    """Transcript response including extracted use cases."""
    use_cases: list[UseCaseResponse] = []
