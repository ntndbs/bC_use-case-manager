"""Industry model."""

from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class Industry(Base):
    """Industry/Branche that companies belong to."""
    
    __tablename__ = "industries"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    companies: Mapped[list["Company"]] = relationship(
        "Company", 
        back_populates="industry",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Industry(id={self.id}, name='{self.name}')>"