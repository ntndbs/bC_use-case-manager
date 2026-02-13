"""Pydantic schemas for Industry."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class IndustryBase(BaseModel):
    """Base schema with shared attributes."""
    name: str
    description: str | None = None


class IndustryCreate(IndustryBase):
    """Schema for creating an industry."""
    pass


class IndustryResponse(IndustryBase):
    """Schema for API responses."""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)