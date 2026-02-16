"""Company endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import Company

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/")
async def list_companies(db: AsyncSession = Depends(get_db)):
    """List all companies."""
    result = await db.execute(select(Company).order_by(Company.name))
    companies = result.scalars().all()
    return [
        {"id": c.id, "name": c.name, "industry_id": c.industry_id}
        for c in companies
    ]
