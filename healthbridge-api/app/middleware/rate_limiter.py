"""Redis-backed rate limiting middleware."""

import time
import logging
from typing import Optional

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

logger = logging.getLogger("healthbridge.rate_limiter")


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Simple sliding-window rate limiter backed by Redis.

    Falls back to in-memory dict if Redis is unavailable.
    """

    def __init__(self, app, max_requests: Optional[int] = None):
        super().__init__(app)
        self.max_requests = max_requests or settings.rate_limit_per_minute
        self._memory_store: dict[str, list[float]] = {}
        self._redis = None
        self._redis_available = False

    async def _get_redis(self):
        """Lazy connect to Redis."""
        if self._redis is None:
            try:
                import redis.asyncio as aioredis
                self._redis = aioredis.from_url(
                    settings.redis_url, decode_responses=True
                )
                await self._redis.ping()
                self._redis_available = True
            except Exception:
                self._redis_available = False
        return self._redis if self._redis_available else None

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ("/health", "/docs", "/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"

        is_allowed = await self._check_rate_limit(key)
        if not is_allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Limit: {self.max_requests}/minute",
            )

        return await call_next(request)

    async def _check_rate_limit(self, key: str) -> bool:
        """Check if request is within rate limit."""
        redis = await self._get_redis()
        now = time.time()
        window = 60  # 1 minute

        if redis:
            return await self._check_redis(redis, key, now, window)
        return self._check_memory(key, now, window)

    async def _check_redis(self, redis, key: str, now: float, window: int) -> bool:
        pipe = redis.pipeline()
        pipe.zremrangebyscore(key, 0, now - window)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, window)
        results = await pipe.execute()
        count = results[2]
        return count <= self.max_requests

    def _check_memory(self, key: str, now: float, window: int) -> bool:
        if key not in self._memory_store:
            self._memory_store[key] = []
        # Remove old entries
        self._memory_store[key] = [
            t for t in self._memory_store[key] if t > now - window
        ]
        self._memory_store[key].append(now)
        return len(self._memory_store[key]) <= self.max_requests
