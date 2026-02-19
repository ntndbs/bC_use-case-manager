"""RBAC permission tests across all protected endpoints (#172).

Tests that Reader cannot perform write operations,
but Maintainer/Admin can — covering companies, industries,
transcripts, and user management.
"""

import pytest
from httpx import AsyncClient

from db.models import User, Transcript
from tests.conftest import auth_header


# ────────────────────────── Industries ──────────────────────────


@pytest.mark.asyncio
async def test_create_industry_as_reader_forbidden(client: AsyncClient, seed_data: dict):
    """Reader cannot create an industry."""
    reader = seed_data["users"]["reader"]
    res = await client.post(
        "/api/industries/",
        json={"name": "Neue Branche", "description": "Test"},
        headers=auth_header(reader),
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_create_industry_as_maintainer(client: AsyncClient, seed_data: dict):
    """Maintainer can create an industry."""
    maintainer = seed_data["users"]["maintainer"]
    res = await client.post(
        "/api/industries/",
        json={"name": "Energie", "description": "Energiesektor"},
        headers=auth_header(maintainer),
    )
    assert res.status_code == 201
    assert res.json()["name"] == "Energie"


@pytest.mark.asyncio
async def test_list_industries_as_reader(client: AsyncClient, seed_data: dict):
    """Reader can list industries."""
    reader = seed_data["users"]["reader"]
    res = await client.get("/api/industries/", headers=auth_header(reader))
    assert res.status_code == 200
    assert isinstance(res.json(), list)


# ────────────────────────── Companies ──────────────────────────


@pytest.mark.asyncio
async def test_create_company_as_reader_forbidden(client: AsyncClient, seed_data: dict):
    """Reader cannot create a company."""
    reader = seed_data["users"]["reader"]
    res = await client.post(
        "/api/companies/",
        json={"name": "Neue Firma", "industry_id": seed_data["industry"].id},
        headers=auth_header(reader),
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_create_company_as_maintainer(client: AsyncClient, seed_data: dict):
    """Maintainer can create a company."""
    maintainer = seed_data["users"]["maintainer"]
    res = await client.post(
        "/api/companies/",
        json={"name": "MaintainerCorp", "industry_id": seed_data["industry"].id},
        headers=auth_header(maintainer),
    )
    assert res.status_code == 201
    assert res.json()["name"] == "MaintainerCorp"


@pytest.mark.asyncio
async def test_list_companies_as_reader(client: AsyncClient, seed_data: dict):
    """Reader can list companies."""
    reader = seed_data["users"]["reader"]
    res = await client.get("/api/companies/", headers=auth_header(reader))
    assert res.status_code == 200
    assert isinstance(res.json(), list)


# ────────────────────────── Transcripts ──────────────────────────


@pytest.mark.asyncio
async def test_upload_transcript_as_reader_forbidden(client: AsyncClient, seed_data: dict):
    """Reader cannot upload a transcript."""
    reader = seed_data["users"]["reader"]
    res = await client.post(
        "/api/transcripts/",
        data={"company_id": str(seed_data["company"].id)},
        files={"file": ("test.txt", b"Some transcript content", "text/plain")},
        headers=auth_header(reader),
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_list_transcripts_as_reader(client: AsyncClient, seed_data: dict):
    """Reader can list transcripts."""
    reader = seed_data["users"]["reader"]
    res = await client.get("/api/transcripts/", headers=auth_header(reader))
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_extract_transcript_as_reader_forbidden(
    client: AsyncClient, seed_data: dict, db_session
):
    """Reader cannot trigger extraction on a transcript."""
    # Create a transcript in DB first
    transcript = Transcript(
        filename="test.txt",
        content="Some content",
        company_id=seed_data["company"].id,
    )
    db_session.add(transcript)
    await db_session.commit()
    await db_session.refresh(transcript)

    reader = seed_data["users"]["reader"]
    res = await client.post(
        f"/api/transcripts/{transcript.id}/extract",
        headers=auth_header(reader),
    )
    assert res.status_code == 403


# ────────────────────────── User Management (Admin) ──────────────────────────


@pytest.mark.asyncio
async def test_delete_user_as_admin(client: AsyncClient, seed_data: dict):
    """Admin can delete a user."""
    admin = seed_data["users"]["admin"]
    reader = seed_data["users"]["reader"]
    res = await client.delete(
        f"/api/auth/users/{reader.id}",
        headers=auth_header(admin),
    )
    assert res.status_code == 204


@pytest.mark.asyncio
async def test_delete_user_as_reader_forbidden(client: AsyncClient, seed_data: dict):
    """Reader cannot delete a user."""
    reader = seed_data["users"]["reader"]
    maintainer = seed_data["users"]["maintainer"]
    res = await client.delete(
        f"/api/auth/users/{maintainer.id}",
        headers=auth_header(reader),
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_delete_user_as_maintainer_forbidden(client: AsyncClient, seed_data: dict):
    """Maintainer cannot delete a user."""
    maintainer = seed_data["users"]["maintainer"]
    reader = seed_data["users"]["reader"]
    res = await client.delete(
        f"/api/auth/users/{reader.id}",
        headers=auth_header(maintainer),
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_admin_cannot_delete_self(client: AsyncClient, seed_data: dict):
    """Admin cannot delete their own account."""
    admin = seed_data["users"]["admin"]
    res = await client.delete(
        f"/api/auth/users/{admin.id}",
        headers=auth_header(admin),
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_list_users_as_maintainer_forbidden(client: AsyncClient, seed_data: dict):
    """Maintainer cannot list all users."""
    maintainer = seed_data["users"]["maintainer"]
    res = await client.get("/api/auth/users", headers=auth_header(maintainer))
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_update_role_as_reader_forbidden(client: AsyncClient, seed_data: dict):
    """Reader cannot update user roles."""
    reader = seed_data["users"]["reader"]
    maintainer = seed_data["users"]["maintainer"]
    res = await client.patch(
        f"/api/auth/users/{maintainer.id}",
        json={"role": "admin"},
        headers=auth_header(reader),
    )
    assert res.status_code == 403


# ────────────────────────── Unauthenticated Access ──────────────────────────


@pytest.mark.asyncio
async def test_protected_endpoints_without_token(client: AsyncClient):
    """All protected endpoints reject requests without a token."""
    endpoints = [
        ("GET", "/api/industries/"),
        ("GET", "/api/companies/"),
        ("GET", "/api/use-cases/"),
        ("GET", "/api/transcripts/"),
        ("GET", "/api/auth/me"),
        ("GET", "/api/auth/users"),
    ]
    for method, url in endpoints:
        res = await client.request(method, url)
        assert res.status_code in (401, 403), f"{method} {url} returned {res.status_code}"
