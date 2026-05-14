from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.analytics import ImportJob
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.auth import UserRead
from app.services.auth_service import get_current_user

router = APIRouter(prefix='/admin', tags=['admin'])


@router.get('/overview')
async def admin_overview(session: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)) -> dict:
    if current_user.role != 'admin':
        return {'users': [], 'import_jobs': [], 'audit_logs': []}
    users = list((await session.execute(select(User))).scalars().all())
    jobs = list((await session.execute(select(ImportJob).order_by(ImportJob.created_at.desc()))).scalars().all())
    logs = list((await session.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(25))).scalars().all())
    return {
        'users': [UserRead.model_validate(user) for user in users],
        'import_jobs': [job.id for job in jobs],
        'audit_logs': [log.action for log in logs],
    }
