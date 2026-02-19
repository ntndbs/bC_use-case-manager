"""Tests for auth endpoints: register, login, /me, RBAC."""

import pytest
from httpx import AsyncClient

from db.models import User
from tests.conftest import auth_header


# ---------- Register ----------


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    res = await client.post("/api/auth/register", json={
        "email": "new@test.com",
        "password": "securepass123",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "new@test.com"
    assert data["role"] == "reader"
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {"email": "dup@test.com", "password": "pass123"}
    await client.post("/api/auth/register", json=payload)
    res = await client.post("/api/auth/register", json=payload)
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    res = await client.post("/api/auth/register", json={
        "email": "not-an-email",
        "password": "pass123",
    })
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_password(client: AsyncClient):
    res = await client.post("/api/auth/register", json={
        "email": "no-pass@test.com",
    })
    assert res.status_code == 422


# ---------- Login ----------


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, seed_users: dict[str, User]):
    res = await client.post("/api/auth/login", json={
        "email": "reader@test.com",
        "password": "testpass123",
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, seed_users: dict[str, User]):
    res = await client.post("/api/auth/login", json={
        "email": "reader@test.com",
        "password": "wrongpass",
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    res = await client.post("/api/auth/login", json={
        "email": "ghost@test.com",
        "password": "whatever",
    })
    assert res.status_code == 401


# ---------- /me ----------


@pytest.mark.asyncio
async def test_me_authenticated(client: AsyncClient, seed_users: dict[str, User]):
    user = seed_users["reader"]
    res = await client.get("/api/auth/me", headers=auth_header(user))
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "reader@test.com"
    assert data["role"] == "reader"


@pytest.mark.asyncio
async def test_me_no_token(client: AsyncClient):
    res = await client.get("/api/auth/me")
    assert res.status_code in (401, 403)


@pytest.mark.asyncio
async def test_me_invalid_token(client: AsyncClient):
    res = await client.get("/api/auth/me", headers={
        "Authorization": "Bearer invalid.token.here",
    })
    assert res.status_code == 401


# ---------- RBAC: Admin endpoints ----------


@pytest.mark.asyncio
async def test_list_users_as_admin(client: AsyncClient, seed_users: dict[str, User]):
    res = await client.get("/api/auth/users", headers=auth_header(seed_users["admin"]))
    assert res.status_code == 200
    assert len(res.json()) == 3  # reader, maintainer, admin


@pytest.mark.asyncio
async def test_list_users_as_reader_forbidden(client: AsyncClient, seed_users: dict[str, User]):
    res = await client.get("/api/auth/users", headers=auth_header(seed_users["reader"]))
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_update_role_as_admin(client: AsyncClient, seed_users: dict[str, User]):
    reader = seed_users["reader"]
    res = await client.patch(
        f"/api/auth/users/{reader.id}",
        json={"role": "maintainer"},
        headers=auth_header(seed_users["admin"]),
    )
    assert res.status_code == 200
    assert res.json()["role"] == "maintainer"


@pytest.mark.asyncio
async def test_admin_cannot_change_own_role(client: AsyncClient, seed_users: dict[str, User]):
    admin = seed_users["admin"]
    res = await client.patch(
        f"/api/auth/users/{admin.id}",
        json={"role": "reader"},
        headers=auth_header(admin),
    )
    assert res.status_code == 400
