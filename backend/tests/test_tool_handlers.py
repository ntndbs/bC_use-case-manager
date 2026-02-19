"""Unit tests for tool handlers (#173, #174).

Tests _check_role() role hierarchy and _create_use_case() handler
directly without going through the HTTP layer.
"""

import pytest
import pytest_asyncio

from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Role, Industry, Company, UseCase
from services.tool_handlers import _check_role, _create_use_case, _set_status


@dataclass
class FakeUser:
    """Lightweight stand-in for User (avoids SQLAlchemy instrumentation)."""
    id: int
    email: str
    role: Role


def _make_user(role: Role) -> FakeUser:
    """Create a fake user with the given role."""
    return FakeUser(id=1, email=f"{role.value}@test.com", role=role)


# ────────────────────────── _check_role() Unit Tests ──────────────────────────


class TestCheckRoleNoUser:
    """Calling _check_role with no user should always fail."""

    def test_none_user(self):
        result = _check_role(None, Role.READER)
        assert result is not None
        assert "error" in result
        assert "authentifiziert" in result["error"].lower()

    def test_none_user_admin_required(self):
        result = _check_role(None, Role.ADMIN)
        assert result is not None
        assert "error" in result


class TestCheckRoleReader:
    """Reader has the lowest level — can only access READER-level tools."""

    def test_reader_passes_reader(self):
        user = _make_user(Role.READER)
        result = _check_role(user, Role.READER)
        assert result is None  # No error = allowed

    def test_reader_blocked_by_maintainer(self):
        user = _make_user(Role.READER)
        result = _check_role(user, Role.MAINTAINER)
        assert result is not None
        assert "error" in result
        assert "maintainer" in result["error"].lower()

    def test_reader_blocked_by_admin(self):
        user = _make_user(Role.READER)
        result = _check_role(user, Role.ADMIN)
        assert result is not None
        assert "error" in result
        assert "admin" in result["error"].lower()


class TestCheckRoleMaintainer:
    """Maintainer can access READER and MAINTAINER tools."""

    def test_maintainer_passes_reader(self):
        user = _make_user(Role.MAINTAINER)
        result = _check_role(user, Role.READER)
        assert result is None

    def test_maintainer_passes_maintainer(self):
        user = _make_user(Role.MAINTAINER)
        result = _check_role(user, Role.MAINTAINER)
        assert result is None

    def test_maintainer_blocked_by_admin(self):
        user = _make_user(Role.MAINTAINER)
        result = _check_role(user, Role.ADMIN)
        assert result is not None
        assert "error" in result
        assert "admin" in result["error"].lower()


class TestCheckRoleAdmin:
    """Admin can access everything."""

    def test_admin_passes_reader(self):
        user = _make_user(Role.ADMIN)
        result = _check_role(user, Role.READER)
        assert result is None

    def test_admin_passes_maintainer(self):
        user = _make_user(Role.ADMIN)
        result = _check_role(user, Role.MAINTAINER)
        assert result is None

    def test_admin_passes_admin(self):
        user = _make_user(Role.ADMIN)
        result = _check_role(user, Role.ADMIN)
        assert result is None


# ────────────────────────── _create_use_case() Tests ──────────────────────────


@pytest_asyncio.fixture
async def company_in_db(db_session: AsyncSession) -> Company:
    """Seed an industry + company for create_use_case tests."""
    industry = Industry(name="IT")
    db_session.add(industry)
    await db_session.flush()
    company = Company(name="TestCorp", industry_id=industry.id)
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)
    return company


@pytest.mark.asyncio
async def test_create_use_case_success(db_session: AsyncSession, company_in_db: Company):
    """Maintainer can create a use case via the tool handler."""
    user = _make_user(Role.MAINTAINER)
    args = {
        "title": "KI-Chatbot",
        "description": "Ein Chatbot für den Kundenservice.",
        "company_id": company_in_db.id,
    }
    result = await _create_use_case(args, db_session, user=user)
    assert "error" not in result
    assert result["id"] is not None
    assert result["title"] == "KI-Chatbot"
    assert result["status"] == "new"


@pytest.mark.asyncio
async def test_create_use_case_missing_company(db_session: AsyncSession, company_in_db: Company):
    """Creating a use case with a non-existent company returns an error."""
    user = _make_user(Role.MAINTAINER)
    args = {
        "title": "Test",
        "description": "Test description",
        "company_id": 9999,
    }
    result = await _create_use_case(args, db_session, user=user)
    assert "error" in result
    assert "9999" in result["error"]


@pytest.mark.asyncio
async def test_create_use_case_as_reader_blocked(db_session: AsyncSession, company_in_db: Company):
    """Reader cannot create a use case via the tool handler."""
    user = _make_user(Role.READER)
    args = {
        "title": "Should fail",
        "description": "Reader should not be able to create.",
        "company_id": company_in_db.id,
    }
    result = await _create_use_case(args, db_session, user=user)
    assert "error" in result
    assert "berechtigung" in result["error"].lower()


# ────────────────────────── _set_status() Tests ──────────────────────────


@pytest_asyncio.fixture
async def use_case_in_db(db_session: AsyncSession, company_in_db: Company) -> UseCase:
    """Seed a use case with status NEW."""
    uc = UseCase(
        title="Status Test UC",
        description="For status transition tests.",
        company_id=company_in_db.id,
        status="new",
    )
    db_session.add(uc)
    await db_session.commit()
    await db_session.refresh(uc)
    return uc


@pytest.mark.asyncio
async def test_set_status_valid_transition(db_session: AsyncSession, use_case_in_db: UseCase):
    """NEW -> IN_REVIEW is a valid transition."""
    user = _make_user(Role.MAINTAINER)
    result = await _set_status(
        {"use_case_id": use_case_in_db.id, "new_status": "in_review"},
        db_session,
        user=user,
    )
    assert "error" not in result
    assert result["status"] == "in_review"


@pytest.mark.asyncio
async def test_set_status_invalid_transition(db_session: AsyncSession, use_case_in_db: UseCase):
    """NEW -> COMPLETED is not allowed."""
    user = _make_user(Role.MAINTAINER)
    result = await _set_status(
        {"use_case_id": use_case_in_db.id, "new_status": "completed"},
        db_session,
        user=user,
    )
    assert "error" in result
    assert "ungültig" in result["error"].lower()


@pytest.mark.asyncio
async def test_set_status_not_found(db_session: AsyncSession, company_in_db: Company):
    """Setting status on a non-existent use case returns an error."""
    user = _make_user(Role.MAINTAINER)
    result = await _set_status(
        {"use_case_id": 9999, "new_status": "in_review"},
        db_session,
        user=user,
    )
    assert "error" in result
    assert "9999" in result["error"]


@pytest.mark.asyncio
async def test_set_status_as_reader_blocked(db_session: AsyncSession, use_case_in_db: UseCase):
    """Reader cannot change status."""
    user = _make_user(Role.READER)
    result = await _set_status(
        {"use_case_id": use_case_in_db.id, "new_status": "in_review"},
        db_session,
        user=user,
    )
    assert "error" in result
    assert "berechtigung" in result["error"].lower()
