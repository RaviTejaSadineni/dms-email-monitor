from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.analytics import AnalyticsSummaryResponse
from app.services.analytics_service import build_summary
from app.services.auth_service import get_current_user

router = APIRouter(prefix='/analytics', tags=['analytics'])


@router.get('/summary', response_model=AnalyticsSummaryResponse)
async def analytics_summary(session: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)) -> AnalyticsSummaryResponse:
    return await build_summary(session)
