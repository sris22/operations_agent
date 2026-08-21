import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_register_user(client: AsyncClient):
    response = await client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "password": "password123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data


@pytest.mark.anyio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "password": "password123",
    })
    response = await client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "password": "password123",
    })
    assert response.status_code == 400


@pytest.mark.anyio
async def test_login_success(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "login@example.com",
        "password": "mypassword",
    })
    response = await client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "mypassword",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["email"] == "login@example.com"


@pytest.mark.anyio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "wrong@example.com",
        "password": "correct",
    })
    response = await client.post("/api/auth/login", json={
        "email": "wrong@example.com",
        "password": "incorrect",
    })
    assert response.status_code == 401


@pytest.mark.anyio
async def test_protected_route(client: AsyncClient):
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_get_me(client: AsyncClient, auth_headers):
    response = await client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "role" in data
