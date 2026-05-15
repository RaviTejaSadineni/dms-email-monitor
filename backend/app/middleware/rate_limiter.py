from __future__ import annotations

from collections import defaultdict, deque
from time import monotonic

from fastapi import HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware


class SimpleRateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 300):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.history: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request, call_next):
        key = request.client.host if request.client else 'unknown'
        now = monotonic()
        bucket = self.history[key]
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= self.requests_per_minute:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail='Rate limit exceeded')
        bucket.append(now)
        return await call_next(request)
