"""Transcript model for uploaded workshop transcripts."""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class Transcript(Base):
    """Workshop transcript uploaded for analysis."""
    
    __tablename__ = "transcripts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    uploaded_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="transcripts",
        lazy="selectin"
    )
    use_cases: Mapped[list["UseCase"]] = relationship(
        "UseCase",
        back_populates="transcript",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Transcript(id={self.id}, filename='{self.filename}')>"