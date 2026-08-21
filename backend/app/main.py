from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import auth, chat, documents, approvals, tickets, metrics
from app.db.database import engine, Base


setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="AI Customer Operations Agent API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(approvals.router, prefix="/api/approvals", tags=["Approvals"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["Tickets"])
app.include_router(metrics.router, prefix="/api/evaluations", tags=["Evaluations"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    from sqlalchemy import text
    from app.db.database import async_session

    checks = {"database": "unknown"}

    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception:
        checks["database"] = "unhealthy"

    all_healthy = all(v == "healthy" for v in checks.values())
    status_code = 200 if all_healthy else 503

    return {"status": "healthy" if all_healthy else "unhealthy", "checks": checks}
