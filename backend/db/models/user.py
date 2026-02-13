"""User model with roles."""

from datetime import datetime
from enum import Enum
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Role(str, Enum):
    """User roles for RBAC."""
    READER = "reader"
    MAINTAINER = "maintainer"
    ADMIN = "admin"


class User(Base):
    """User account for authentication and authorization."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(default=Role.READER)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"