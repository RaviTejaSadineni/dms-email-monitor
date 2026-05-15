from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.analytics import ImportJob
from app.schemas.analytics import ImportJobCreate, ImportJobRead
from app.services.auth_service import get_current_user
from app.services.import_service import create_import_job

router = APIRouter(prefix='/import', tags=['import'])


@router.get('/jobs', response_model=list[ImportJobRead])
async def list_jobs(session: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)) -> list[ImportJobRead]:
    result = await session.execute(
        select(ImportJob).where(ImportJob.user_id == current_user.id).order_by(ImportJob.created_at.desc())
    )
    jobs = list(result.scalars().all())
    return [ImportJobRead.model_validate(job) for job in jobs]


@router.post('/jobs', response_model=ImportJobRead)
async def create_job(
    payload: ImportJobCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ImportJobRead:
    job = await create_import_job(
        session,
        user=current_user,
        mbox_path=payload.mbox_path,
        batch_size=payload.batch_size,
        background_tasks=background_tasks,
    )
    return ImportJobRead.model_validate(job)


@router.get('/jobs/{job_id}/progress', response_model=ImportJobRead)
async def get_job_progress(job_id: int, session: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)) -> ImportJobRead:
    job = await session.get(ImportJob, job_id)
    return ImportJobRead.model_validate(job)
