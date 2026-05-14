from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, ai_insights, analytics, attachments, auth, contracts, emails, health, import_router, search
from app.config import get_settings
from app.database import init_db
from app.middleware.auth_middleware import BearerPassthroughMiddleware
from app.middleware.rate_limiter import SimpleRateLimiterMiddleware

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.add_middleware(BearerPassthroughMiddleware)
app.add_middleware(SimpleRateLimiterMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
async def on_startup() -> None:
    await init_db()


app.include_router(auth.router, prefix='/api')
app.include_router(import_router.router, prefix='/api')
app.include_router(emails.router, prefix='/api')
app.include_router(contracts.router, prefix='/api')
app.include_router(analytics.router, prefix='/api')
app.include_router(ai_insights.router, prefix='/api')
app.include_router(attachments.router, prefix='/api')
app.include_router(search.router, prefix='/api')
app.include_router(admin.router, prefix='/api')
app.include_router(health.router, prefix='/api')
