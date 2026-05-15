from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.analytics import ImportJob
from app.schemas.analytics import ImportJobCreate, ImportJobRead
from app.services.auth_service import get_current_user
from app.services.import_service import create_import_job, create_import_job_from_upload

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


@router.post('/upload', response_model=ImportJobRead)
async def create_job_from_upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    batch_size: int = Form(500),
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ImportJobRead:
    original_name = Path(file.filename or '').name
    if not original_name:
        raise HTTPException(status_code=400, detail='file name is required')
    if Path(original_name).suffix.lower() != '.mbox':
        raise HTTPException(status_code=400, detail='only .mbox import files are supported')

    imports_root = (get_settings().uploads_path.parent / 'imports').resolve()
    upload_dir = imports_root / str(uuid4())
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_path = upload_dir / original_name

    try:
        with saved_path.open('wb') as output:
            while chunk := await file.read(1024 * 1024):
                output.write(chunk)
    finally:
        await file.close()

    job = await create_import_job_from_upload(
        session,
        user=current_user,
        resolved_path=saved_path,
        batch_size=batch_size,
        background_tasks=background_tasks,
    )
    return ImportJobRead.model_validate(job)


@router.get('/jobs/{job_id}/progress', response_model=ImportJobRead)
async def get_job_progress(job_id: int, session: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)) -> ImportJobRead:
    job = await session.get(ImportJob, job_id)
    return ImportJobRead.model_validate(job)
