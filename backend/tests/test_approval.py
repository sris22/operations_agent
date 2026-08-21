import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_list_approvals_empty(client: AsyncClient, auth_headers):
    response = await client.get("/api/approvals", headers=auth_headers)
    assert response.status_code == 200
    assert "approvals" in response.json()


@pytest.mark.anyio
async def test_get_nonexistent_approval(client: AsyncClient, auth_headers):
    response = await client.get("/api/approvals/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.anyio
async def test_approve_nonexistent(client: AsyncClient, auth_headers):
    response = await client.post("/api/approvals/99999/approve", headers=auth_headers)
    assert response.status_code == 400


@pytest.mark.anyio
async def test_reject_nonexistent(client: AsyncClient, auth_headers):
    response = await client.post("/api/approvals/99999/reject", headers=auth_headers)
    assert response.status_code == 400


@pytest.mark.anyio
async def test_approvals_require_auth(client: AsyncClient):
    response = await client.get("/api/approvals")
    assert response.status_code == 401
