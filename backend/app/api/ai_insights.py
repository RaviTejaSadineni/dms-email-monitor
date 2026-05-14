from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.analytics_service import build_ai_insights
from app.services.auth_service import get_current_user

router = APIRouter(prefix='/ai-insights', tags=['ai-insights'])


@router.get('/overview')
async def insight_overview(session: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)) -> dict:
    return {'items': await build_ai_insights(session)}
