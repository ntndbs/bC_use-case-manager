"""UseCase model - the core entity."""

from datetime import datetime
from enum import Enum
from typing import Any
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class UseCaseStatus(str, Enum):
    """Status progression for use cases."""
    NEW = "new"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class UseCase(Base):
    """Use Case extracted from workshops or created manually."""
    
    __tablename__ = "use_cases"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    stakeholders: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    expected_benefit: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[UseCaseStatus] = mapped_column(default=UseCaseStatus.NEW)
    
    # Ratings (1-5, nullable)
    rating_effort: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating_benefit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating_feasibility: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating_data_availability: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating_strategic_relevance: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Foreign Keys
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    transcript_id: Mapped[int | None] = mapped_column(ForeignKey("transcripts.id"), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="use_cases",
        lazy="selectin"
    )
    transcript: Mapped["Transcript | None"] = relationship(
        "Transcript",
        back_populates="use_cases",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<UseCase(id={self.id}, title='{self.title[:30]}...', status='{self.status}')>"