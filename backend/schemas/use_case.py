"""Pydantic schemas for UseCase."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from db.models.use_case import UseCaseStatus


class Stakeholder(BaseModel):
    """Single stakeholder entry."""
    name: str
    role: str | None = None


class UseCaseBase(BaseModel):
    """Base schema with shared attributes."""
    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    stakeholders: list[Stakeholder] | None = None
    expected_benefit: str | None = None


class UseCaseCreate(UseCaseBase):
    """Schema for creating a use case."""
    company_id: int
    transcript_id: int | None = None


class UseCaseUpdate(BaseModel):
    """Schema for updating a use case (all fields optional)."""
    title: str | None = None
    description: str | None = None
    stakeholders: list[Stakeholder] | None = None
    expected_benefit: str | None = None
    status: UseCaseStatus | None = None


class UseCaseResponse(UseCaseBase):
    """Schema for API responses."""
    id: int
    status: UseCaseStatus
    company_id: int
    transcript_id: int | None = None
    created_by_id: int | None = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UseCaseListResponse(BaseModel):
    """Paginated list of use cases."""
    data: list[UseCaseResponse]
    total: int
    page: int = 1
    per_page: int = 20