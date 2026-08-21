import os
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("LLM_API_KEY", "test-key")
os.environ.setdefault("EMBEDDING_API_KEY", "test-key")
os.environ.setdefault("ENTERPRISE_API_BASE_URL", "http://localhost:8001")

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_token(client: AsyncClient):
    response = await client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123",
    })
    response = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123",
    })
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
