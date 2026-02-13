"""Pydantic schemas for User."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

from db.models.user import Role


class UserBase(BaseModel):
    """Base schema with shared attributes."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str


class UserLogin(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for API responses (no password!)."""
    id: int
    role: Role
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data encoded in JWT."""
    user_id: int
    email: str
    role: Role