from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path, PurePath
from typing import Iterable

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.models.analytics import ImportJob
from app.models.attachment import Attachment
from app.models.classification import Classification
from app.models.email import Email
from app.models.user import User
from app.redis_client import publish_json
from app.services.ai_service import get_ai_service
from app.services.classification_service import classify_email
from app.services.contract_service import STAGE_MAP, upsert_contract
from app.services.thread_service import get_or_create_thread
from app.utils.mbox_parser import ParsedEmail, iter_mbox_messages

QUEUE_NAME = 'dms:import:jobs'


def _thread_key(email: ParsedEmail) -> str:
    if email.thread_header_id:
        return email.thread_header_id
    if email.in_reply_to:
        return email.in_reply_to.strip()
    references = '-'.join(email.references[:2])
    participants = '-'.join(sorted({email.sender, *email.recipients_to, *email.recipients_cc}))
    return f"{email.subject_normalized[:120]}::{references or participants[:80]}"


def _resolve_import_path(mbox_path: str) -> Path:
    settings = get_settings()
    relative_path = PurePath(mbox_path.strip().replace('\\', '/'))
    if relative_path.is_absolute() or '..' in relative_path.parts:
        raise HTTPException(status_code=400, detail='mbox path must be relative to a configured import root')
    if relative_path.suffix.lower() != '.mbox':
        raise HTTPException(status_code=400, detail='only .mbox import files are supported')
    for root in settings.import_allowed_roots:
        candidate = root.joinpath(*relative_path.parts)
        if candidate.exists() and candidate.is_file():
            return candidate
    raise HTTPException(status_code=404, detail='mbox path not found')


async def create_import_job(
    session: AsyncSession,
    *,
    user: User | None,
    mbox_path: str,
    batch_size: int,
    background_tasks: BackgroundTasks,
) -> ImportJob:
    path = _resolve_import_path(mbox_path)
    return await _create_import_job_from_path(
        session,
        user=user,
        path=path,
        batch_size=batch_size,
        background_tasks=background_tasks,
    )


async def create_import_job_from_upload(
    session: AsyncSession,
    *,
    user: User | None,
    resolved_path: Path,
    batch_size: int,
    background_tasks: BackgroundTasks,
) -> ImportJob:
    path = resolved_path.resolve()
    if not path.is_absolute():
        raise HTTPException(status_code=400, detail='uploaded file path must be absolute')
    if path.suffix.lower() != '.mbox':
        raise HTTPException(status_code=400, detail='only .mbox import files are supported')
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail='uploaded file not found')
    return await _create_import_job_from_path(
        session,
        user=user,
        path=path,
        batch_size=batch_size,
        background_tasks=background_tasks,
    )


async def _create_import_job_from_path(
    session: AsyncSession,
    *,
    user: User | None,
    path: Path,
    batch_size: int,
    background_tasks: BackgroundTasks,
) -> ImportJob:
    job = ImportJob(
        user_id=user.id if user else None,
        filename=path.name,
        file_size_bytes=path.stat().st_size,
        status='queued',
        total_emails=0,
        processed_count=0,
        error_count=0,
        started_at=None,
        completed_at=None,
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)
    await publish_json(f'import-job:{job.id}', {'status': 'queued', 'processed_count': 0, 'total_emails': 0})
    background_tasks.add_task(process_import_job, job.id, str(path), batch_size)
    return job


async def process_import_job(job_id: int, mbox_path: str, batch_size: int) -> None:
    settings = get_settings()
    ai_service = get_ai_service()
    async with AsyncSessionLocal() as session:
        job = await session.get(ImportJob, job_id)
        if job is None:
            return
        job.status = 'running'
        job.started_at = datetime.now(timezone.utc).isoformat()
        emails = list(iter_mbox_messages(mbox_path))
        job.total_emails = len(emails)
        await session.commit()
        await publish_json(
            f'import-job:{job.id}',
            {'status': job.status, 'processed_count': job.processed_count, 'total_emails': job.total_emails},
        )

        for index in range(0, len(emails), max(batch_size, 1)):
            batch = emails[index : index + max(batch_size, 1)]
            try:
                await _persist_batch(session, batch, job_id, settings.uploads_path, ai_service)
                job.processed_count += len(batch)
            except Exception as exc:  # pragma: no cover
                job.error_count += len(batch)
                job.errors.append({'batch_start': index, 'error': str(exc)})
            await session.commit()
            await publish_json(
                f'import-job:{job.id}',
                {
                    'status': job.status,
                    'processed_count': job.processed_count,
                    'total_emails': job.total_emails,
                    'error_count': job.error_count,
                },
            )

        job.status = 'completed' if job.error_count == 0 else 'completed_with_errors'
        job.completed_at = datetime.now(timezone.utc).isoformat()
        await session.commit()
        await publish_json(
            f'import-job:{job.id}',
            {
                'status': job.status,
                'processed_count': job.processed_count,
                'total_emails': job.total_emails,
                'error_count': job.error_count,
                'completed_at': job.completed_at,
            },
        )


async def _persist_batch(
    session: AsyncSession,
    batch: Iterable[ParsedEmail],
    job_id: int,
    uploads_root: Path,
    ai_service,
) -> None:
    batch = list(batch)
    if not batch:
        return
    message_ids = [email.message_id for email in batch]
    existing_ids = set(
        (
            await session.execute(select(Email.message_id).where(Email.message_id.in_(message_ids)))
        ).scalars()
    )
    for parsed in batch:
        if parsed.message_id in existing_ids:
            continue
        classification = classify_email(parsed.subject, parsed.body_plain or parsed.body_html or '', parsed.sender)
        participants = [parsed.sender, *parsed.recipients_to, *parsed.recipients_cc, *parsed.recipients_bcc]
        stage = STAGE_MAP.get(classification.category)
        thread = await get_or_create_thread(
            session,
            thread_key=_thread_key(parsed),
            subject_normalized=parsed.subject_normalized,
            participants=[participant for participant in participants if participant],
            sent_at=parsed.sent_at,
            stage=stage,
            priority=classification.priority,
        )
        email = Email(
            message_id=parsed.message_id,
            thread=thread,
            subject=parsed.subject,
            sender=parsed.sender,
            recipients_to=parsed.recipients_to,
            recipients_cc=parsed.recipients_cc,
            recipients_bcc=parsed.recipients_bcc,
            body_plain=parsed.body_plain,
            body_html=parsed.body_html,
            sent_at=parsed.sent_at,
            received_at=parsed.received_at,
            labels=parsed.labels,
            priority=classification.priority,
            category=classification.category,
            sentiment=classification.sentiment,
            ai_summary=await ai_service.summarize_email(parsed.subject, parsed.body_plain or parsed.body_html or ''),
            is_spam=classification.is_spam,
            raw_headers=parsed.raw_headers,
            import_batch_id=str(job_id),
            size_bytes=parsed.size_bytes,
            has_attachments=parsed.has_attachments,
            is_forwarded=parsed.is_forwarded,
            is_auto_reply=parsed.is_auto_reply,
            language=parsed.language,
            thread_header_id=parsed.thread_header_id,
            in_reply_to=parsed.in_reply_to,
            references=parsed.references,
        )
        session.add(email)
        await session.flush()
        thread.email_count += 1
        content = ' '.join(filter(None, [parsed.subject, parsed.body_plain, parsed.body_html]))
        await upsert_contract(session, thread, classification.contract_numbers, content, stage, participants)
        session.add(
            Classification(
                email_id=email.id,
                category=classification.category,
                priority=classification.priority,
                confidence=classification.confidence,
                classified_by='ai',
                classified_at=datetime.now(timezone.utc),
            )
        )
        attachment_dir = uploads_root / str(email.id)
        attachment_dir.mkdir(parents=True, exist_ok=True)
        for attachment in parsed.attachments:
            file_path = attachment_dir / attachment.filename
            file_path.write_bytes(attachment.payload)
            excerpt = attachment.payload[:4000].decode('utf-8', errors='replace') if attachment.payload else ''
            analysis = await ai_service.analyze_attachment(attachment.filename, excerpt)
            session.add(
                Attachment(
                    email_id=email.id,
                    filename=attachment.filename,
                    content_type=attachment.content_type,
                    size_bytes=len(attachment.payload),
                    storage_path=str(file_path),
                    ai_extracted_text=excerpt,
                    ai_analysis=analysis,
                )
            )
