from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(prefix='/health', tags=['health'])


@router.get('')
async def health_check() -> dict:
    settings = get_settings()
    return {
        'status': 'ok',
        'app_name': settings.app_name,
        'features': {
            'jwt_auth': True,
            'async_sqlalchemy': True,
            'redis_queue': True,
            'azure_openai_ready': settings.azure_openai_api_key != 'changeme',
        },
    }
