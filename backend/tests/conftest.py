"""Shared test fixtures: in-memory DB, async client, auth helpers."""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from db.database import Base, get_db
from db.models import User, Role
from core.security import hash_password, create_access_token
from main import app


# In-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Use a single event loop for all tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create tables, yield a session, then drop everything."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client with test DB override."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seed_users(db_session: AsyncSession) -> dict[str, User]:
    """Create one user per role and return them keyed by role name."""
    users = {}
    for role in Role:
        user = User(
            email=f"{role.value}@test.com",
            password_hash=hash_password("testpass123"),
            role=role,
        )
        db_session.add(user)
        users[role.value] = user

    await db_session.commit()
    for u in users.values():
        await db_session.refresh(u)
    return users


def auth_header(user: User) -> dict[str, str]:
    """Generate a Bearer token header for a user."""
    token = create_access_token(user.id, user.email, user.role.value)
    return {"Authorization": f"Bearer {token}"}
