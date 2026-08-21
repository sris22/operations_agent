import os
import pytest
from httpx import AsyncClient, ASGITransport

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("LLM_API_KEY", "test-key")
os.environ.setdefault("EMBEDDING_API_KEY", "test-key")
os.environ.setdefault("ENTERPRISE_API_BASE_URL", "http://localhost:8001")

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_token(client: AsyncClient):
    from app.db.database import engine, Base
    from app.db.models import user, conversation, message, document, document_chunk  # noqa: F401
    from app.db.models import tool_execution, approval, ticket, evaluation_run  # noqa: F401

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        pytest.skip("PostgreSQL not available")

    await client.post("/api/auth/register", json={
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
