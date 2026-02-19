"""Tests for Use Case CRUD endpoints and status transitions."""

import pytest
from httpx import AsyncClient

from tests.conftest import auth_header


# ---------- List ----------


@pytest.mark.asyncio
async def test_list_use_cases(client: AsyncClient, seed_data: dict):
    res = await client.get("/api/use-cases/", headers=auth_header(seed_data["users"]["reader"]))
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert len(data["data"]) >= 1
    assert data["data"][0]["title"] == "Test Use Case"


@pytest.mark.asyncio
async def test_list_use_cases_unauthenticated(client: AsyncClient):
    res = await client.get("/api/use-cases/")
    assert res.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_use_cases_filter_by_status(client: AsyncClient, seed_data: dict):
    headers = auth_header(seed_data["users"]["reader"])
    res = await client.get("/api/use-cases/?status=new", headers=headers)
    assert res.status_code == 200
    assert res.json()["total"] >= 1

    res = await client.get("/api/use-cases/?status=archived", headers=headers)
    assert res.status_code == 200
    assert res.json()["total"] == 0


# ---------- Get ----------


@pytest.mark.asyncio
async def test_get_use_case(client: AsyncClient, seed_data: dict):
    uc_id = seed_data["use_case"].id
    res = await client.get(f"/api/use-cases/{uc_id}", headers=auth_header(seed_data["users"]["reader"]))
    assert res.status_code == 200
    assert res.json()["id"] == uc_id
    assert res.json()["title"] == "Test Use Case"


@pytest.mark.asyncio
async def test_get_use_case_not_found(client: AsyncClient, seed_data: dict):
    res = await client.get("/api/use-cases/9999", headers=auth_header(seed_data["users"]["reader"]))
    assert res.status_code == 404


# ---------- Create ----------


@pytest.mark.asyncio
async def test_create_use_case_as_maintainer(client: AsyncClient, seed_data: dict):
    res = await client.post("/api/use-cases/", json={
        "title": "Neuer Use Case",
        "description": "Beschreibung des Use Cases.",
        "company_id": seed_data["company"].id,
    }, headers=auth_header(seed_data["users"]["maintainer"]))
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Neuer Use Case"
    assert data["status"] == "new"


@pytest.mark.asyncio
async def test_create_use_case_as_reader_forbidden(client: AsyncClient, seed_data: dict):
    res = await client.post("/api/use-cases/", json={
        "title": "Nicht erlaubt",
        "description": "Reader darf nicht erstellen.",
        "company_id": seed_data["company"].id,
    }, headers=auth_header(seed_data["users"]["reader"]))
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_create_use_case_invalid_company(client: AsyncClient, seed_data: dict):
    res = await client.post("/api/use-cases/", json={
        "title": "Bad Company",
        "description": "Firma existiert nicht.",
        "company_id": 9999,
    }, headers=auth_header(seed_data["users"]["maintainer"]))
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_create_use_case_missing_title(client: AsyncClient, seed_data: dict):
    res = await client.post("/api/use-cases/", json={
        "description": "Kein Titel.",
        "company_id": seed_data["company"].id,
    }, headers=auth_header(seed_data["users"]["maintainer"]))
    assert res.status_code == 422


# ---------- Update ----------


@pytest.mark.asyncio
async def test_update_use_case(client: AsyncClient, seed_data: dict):
    uc_id = seed_data["use_case"].id
    res = await client.patch(f"/api/use-cases/{uc_id}", json={
        "title": "Aktualisierter Titel",
    }, headers=auth_header(seed_data["users"]["maintainer"]))
    assert res.status_code == 200
    assert res.json()["title"] == "Aktualisierter Titel"


@pytest.mark.asyncio
async def test_update_use_case_rating(client: AsyncClient, seed_data: dict):
    uc_id = seed_data["use_case"].id
    res = await client.patch(f"/api/use-cases/{uc_id}", json={
        "rating_effort": 3,
        "rating_benefit": 5,
    }, headers=auth_header(seed_data["users"]["maintainer"]))
    assert res.status_code == 200
    data = res.json()
    assert data["rating_effort"] == 3
    assert data["rating_benefit"] == 5
    assert data["rating_average"] == 4.0


@pytest.mark.asyncio
async def test_update_use_case_invalid_rating(client: AsyncClient, seed_data: dict):
    uc_id = seed_data["use_case"].id
    res = await client.patch(f"/api/use-cases/{uc_id}", json={
        "rating_effort": 6,
    }, headers=auth_header(seed_data["users"]["maintainer"]))
    assert res.status_code == 422


# ---------- Status transitions ----------


@pytest.mark.asyncio
async def test_valid_status_transition(client: AsyncClient, seed_data: dict):
    uc_id = seed_data["use_case"].id
    headers = auth_header(seed_data["users"]["maintainer"])

    # new -> in_review (valid)
    res = await client.patch(f"/api/use-cases/{uc_id}", json={
        "status": "in_review",
    }, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "in_review"


@pytest.mark.asyncio
async def test_invalid_status_transition(client: AsyncClient, seed_data: dict):
    uc_id = seed_data["use_case"].id
    headers = auth_header(seed_data["users"]["maintainer"])

    # new -> completed (invalid, must go through in_review first)
    res = await client.patch(f"/api/use-cases/{uc_id}", json={
        "status": "completed",
    }, headers=headers)
    assert res.status_code == 409


# ---------- Archive / Restore ----------


@pytest.mark.asyncio
async def test_archive_use_case(client: AsyncClient, seed_data: dict):
    uc_id = seed_data["use_case"].id
    res = await client.delete(f"/api/use-cases/{uc_id}", headers=auth_header(seed_data["users"]["admin"]))
    assert res.status_code == 200
    assert res.json()["status"] == "archived"


@pytest.mark.asyncio
async def test_archive_as_maintainer_forbidden(client: AsyncClient, seed_data: dict):
    uc_id = seed_data["use_case"].id
    res = await client.delete(f"/api/use-cases/{uc_id}", headers=auth_header(seed_data["users"]["maintainer"]))
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_restore_archived_use_case(client: AsyncClient, seed_data: dict):
    uc_id = seed_data["use_case"].id
    admin_headers = auth_header(seed_data["users"]["admin"])

    # First archive it
    await client.delete(f"/api/use-cases/{uc_id}", headers=admin_headers)

    # Then restore
    res = await client.patch(f"/api/use-cases/{uc_id}/restore", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "new"


@pytest.mark.asyncio
async def test_restore_non_archived_fails(client: AsyncClient, seed_data: dict):
    uc_id = seed_data["use_case"].id
    res = await client.patch(f"/api/use-cases/{uc_id}/restore", headers=auth_header(seed_data["users"]["admin"]))
    assert res.status_code == 409


# ---------- Permanent delete ----------


@pytest.mark.asyncio
async def test_permanent_delete(client: AsyncClient, seed_data: dict):
    uc_id = seed_data["use_case"].id
    admin_headers = auth_header(seed_data["users"]["admin"])
    res = await client.delete(f"/api/use-cases/{uc_id}/permanent", headers=admin_headers)
    assert res.status_code == 204

    # Verify it's gone
    res = await client.get(f"/api/use-cases/{uc_id}", headers=admin_headers)
    assert res.status_code == 404
