from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware


class BearerPassthroughMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        return await call_next(request)
