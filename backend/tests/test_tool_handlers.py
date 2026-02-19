"""Unit tests for _check_role() in tool handlers (#173).

Tests the role-checking function directly with different roles,
verifying that READER < MAINTAINER < ADMIN hierarchy is enforced.
"""

import pytest

from dataclasses import dataclass

from db.models import Role
from services.tool_handlers import _check_role


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
