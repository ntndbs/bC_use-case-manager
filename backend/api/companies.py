"""Company endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from db.database import get_db
from db.models import Company, User

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/")
async def list_companies(db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    """List all companies."""
    result = await db.execute(select(Company).order_by(Company.name))
    companies = result.scalars().all()
    return [
        {"id": c.id, "name": c.name, "industry_id": c.industry_id}
        for c in companies
    ]
