import structlog
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)


async def app_error_handler(request: Request, exc: Exception) -> dict:
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "unhandled_error",
        error=str(exc),
        path=request.url.path,
        request_id=request_id,
    )
    return {"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}}


async def http_exception_handler(request: Request, exc) -> dict:
    request_id = getattr(request.state, "request_id", "unknown")
    return {
        "error": {
            "code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "request_id": request_id,
        }
    }
