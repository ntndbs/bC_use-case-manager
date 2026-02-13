"""Company model."""

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class Company(Base):
    """Company/Unternehmen that participates in workshops."""
    
    __tablename__ = "companies"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    industry_id: Mapped[int] = mapped_column(ForeignKey("industries.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    industry: Mapped["Industry"] = relationship(
        "Industry",
        back_populates="companies",
        lazy="selectin"
    )
    transcripts: Mapped[list["Transcript"]] = relationship(
        "Transcript",
        back_populates="company",
        lazy="selectin"
    )
    use_cases: Mapped[list["UseCase"]] = relationship(
        "UseCase",
        back_populates="company",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.name}')>"