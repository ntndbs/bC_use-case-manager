"""Pydantic schemas for API validation."""

from schemas.industry import IndustryCreate, IndustryResponse
from schemas.company import CompanyCreate, CompanyResponse, CompanyWithIndustry
from schemas.user import UserCreate, UserLogin, UserResponse, Token, TokenData
from schemas.transcript import TranscriptCreate, TranscriptResponse, TranscriptWithContent
from schemas.use_case import (
    UseCaseCreate, 
    UseCaseUpdate, 
    UseCaseResponse, 
    UseCaseListResponse,
    Stakeholder,
)

__all__ = [
    # Industry
    "IndustryCreate",
    "IndustryResponse",
    # Company
    "CompanyCreate",
    "CompanyResponse",
    "CompanyWithIndustry",
    # User
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
    # Transcript
    "TranscriptCreate",
    "TranscriptResponse",
    "TranscriptWithContent",
    # UseCase
    "UseCaseCreate",
    "UseCaseUpdate",
    "UseCaseResponse",
    "UseCaseListResponse",
    "Stakeholder",
]