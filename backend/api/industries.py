"""Industry endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user, require_role
from db.database import get_db
from db.models import Industry, User, Role
from schemas.industry import IndustryCreate

router = APIRouter(prefix="/industries", tags=["industries"])


@router.get("/")
async def list_industries(db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    """List all industries."""
    result = await db.execute(select(Industry).order_by(Industry.name))
    industries = result.scalars().all()
    return [
        {"id": i.id, "name": i.name, "description": i.description}
        for i in industries
    ]


@router.post("/", status_code=201)
async def create_industry(
    body: IndustryCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(Role.MAINTAINER)),
):
    """Create a new industry."""
    existing = await db.execute(select(Industry).where(Industry.name == body.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Industry with this name already exists")

    industry = Industry(name=body.name, description=body.description)
    db.add(industry)
    await db.commit()
    await db.refresh(industry)
    return {"id": industry.id, "name": industry.name, "description": industry.description}
