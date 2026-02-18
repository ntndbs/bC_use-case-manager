"""Authentication endpoints: register, login, current user."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import BaseModel

from core.dependencies import get_current_user, require_role
from core.security import create_access_token, hash_password, verify_password
from db.database import get_db
from db.models import User, Role
from schemas.user import UserCreate, UserLogin, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user with role READER."""
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate and return a JWT access token."""
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account deactivated")

    token = create_access_token(user.id, user.email, user.role.value)
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
async def current_user(user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return user


# ---------- Admin: User management ----------


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(Role.ADMIN)),
):
    """List all users (admin only)."""
    result = await db.execute(select(User).order_by(User.email))
    return result.scalars().all()


class RoleUpdate(BaseModel):
    role: Role


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    body: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_role(Role.ADMIN)),
):
    """Update a user's role (admin only)."""
    if current.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = body.role
    await db.commit()
    await db.refresh(user)
    return user
