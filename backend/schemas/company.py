"""Pydantic schemas for Company."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CompanyBase(BaseModel):
    """Base schema with shared attributes."""
    name: str
    industry_id: int


class CompanyCreate(CompanyBase):
    """Schema for creating a company."""
    pass


class CompanyResponse(CompanyBase):
    """Schema for API responses."""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CompanyWithIndustry(CompanyResponse):
    """Company with nested industry info."""
    industry: "IndustryResponse"
    
    
# Avoid circular import
from schemas.industry import IndustryResponse
CompanyWithIndustry.model_rebuild()