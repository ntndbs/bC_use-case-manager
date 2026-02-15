"""Use Case CRUD endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import UseCase, Company
from db.models.use_case import UseCaseStatus
from schemas.use_case import (
    UseCaseCreate,
    UseCaseUpdate,
    UseCaseResponse,
    UseCaseListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/use-cases", tags=["use-cases"])


# ---------- E2-UC1: List use cases with filters ----------

@router.get("/", response_model=UseCaseListResponse)
async def list_use_cases(
    company_id: int | None = None,
    status: UseCaseStatus | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List use cases with optional filters for company, status and search."""
    query = select(UseCase)

    if company_id is not None:
        query = query.where(UseCase.company_id == company_id)
    if status is not None:
        query = query.where(UseCase.status == status)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            UseCase.title.ilike(pattern) | UseCase.description.ilike(pattern)
        )

    # Total count (before pagination)
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    # Paginate
    query = query.order_by(UseCase.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    use_cases = result.scalars().all()

    return UseCaseListResponse(
        data=use_cases,
        total=total,
        page=page,
        per_page=per_page,
    )


# ---------- E2-UC2: Get single use case ----------

@router.get("/{use_case_id}", response_model=UseCaseResponse)
async def get_use_case(
    use_case_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single use case by ID."""
    use_case = await db.get(UseCase, use_case_id)
    if not use_case:
        raise HTTPException(status_code=404, detail="Use case not found")
    return use_case
