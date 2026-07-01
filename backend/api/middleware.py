"""Middleware for CORS, request logging, and timeout handling."""

from __future__ import annotations

import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs request method, path, status, and duration."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
            duration = time.time() - start_time
            logger.info(
                "%s %s → %d (%.2fs)",
                method,
                path,
                response.status_code,
                duration,
            )
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "%s %s → 500 (%.2fs) ERROR: %s",
                method,
                path,
                duration,
                str(e),
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Enforces a maximum response timeout."""

    async def dispatch(self, request: Request, call_next):
        import asyncio

        timeout = settings.response_timeout_seconds

        try:
            response = await asyncio.wait_for(
                call_next(request),
                timeout=timeout,
            )
            return response
        except TimeoutError:
            logger.error(
                "Request to %s timed out after %ds",
                request.url.path,
                timeout,
            )
            return JSONResponse(
                status_code=504,
                content={"detail": f"Request timed out after {timeout} seconds."},
            )
