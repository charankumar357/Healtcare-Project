"""Global exception handlers for the FastAPI application."""

import logging
import traceback
from datetime import datetime, timezone

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("healthbridge.errors")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catch all unhandled exceptions and return structured JSON errors."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except Exception as exc:
            logger.error(
                f"Unhandled error: {exc}\n"
                f"Path: {request.url.path}\n"
                f"Method: {request.method}\n"
                f"Traceback: {traceback.format_exc()}"
            )

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "detail": str(exc) if __import__("app.config", fromlist=["settings"]).settings.debug else "An unexpected error occurred",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "path": str(request.url.path),
                },
            )
