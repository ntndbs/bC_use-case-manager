"""Company endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user, require_role
from db.database import get_db
from db.models import Company, Industry, User, Role
from schemas.company import CompanyCreate

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


@router.post("/", status_code=201)
async def create_company(
    body: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(Role.MAINTAINER)),
):
    """Create a new company."""
    industry = await db.get(Industry, body.industry_id)
    if not industry:
        raise HTTPException(status_code=404, detail="Industry not found")

    existing = await db.execute(select(Company).where(Company.name == body.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Company with this name already exists")

    company = Company(name=body.name, industry_id=body.industry_id)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return {"id": company.id, "name": company.name, "industry_id": company.industry_id}
