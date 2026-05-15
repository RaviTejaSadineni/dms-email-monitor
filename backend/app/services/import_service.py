from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path, PurePath
from math import ceil
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
from app.redis_client import get_redis, publish_json
from app.services.ai_service import get_ai_service
from app.services.classification_service import classify_email
from app.services.contract_service import STAGE_MAP, upsert_contract
from app.services.thread_service import get_or_create_thread
from app.utils.mbox_parser import ParsedEmail, count_mbox_messages, iter_mbox_messages

QUEUE_NAME = 'dms:import:jobs'
logger = logging.getLogger(__name__)
LIVE_STATS_KEY_PREFIX = 'import-job-live'
RECENT_EVENTS_LIMIT = 100
BINARY_EXTENSIONS = {
    '.pdf',
    '.png',
    '.jpg',
    '.jpeg',
    '.gif',
    '.bmp',
    '.webp',
    '.doc',
    '.docx',
    '.ppt',
    '.pptx',
    '.xls',
    '.xlsx',
    '.zip',
    '.7z',
    '.rar',
    '.gz',
    '.tar',
}
BINARY_CONTENT_TYPE_PREFIXES = (
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument',
    'application/zip',
    'application/octet-stream',
    'image/',
)


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


def _live_stats_key(job_id: int) -> str:
    return f'{LIVE_STATS_KEY_PREFIX}:{job_id}'


def _format_size(size_bytes: int) -> str:
    if size_bytes <= 0:
        return '0B'
    units = ('B', 'KB', 'MB', 'GB', 'TB')
    value = float(size_bytes)
    unit_index = 0
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    if unit_index == 0:
        return f'{int(value)}{units[unit_index]}'
    return f'{value:.1f}{units[unit_index]}'


def _is_binary_attachment(filename: str, content_type: str | None) -> bool:
    extension = Path(filename).suffix.lower()
    if extension in BINARY_EXTENSIONS:
        return True
    normalized_content_type = (content_type or '').lower()
    return normalized_content_type.startswith(BINARY_CONTENT_TYPE_PREFIXES)


def _build_attachment_excerpt(filename: str, content_type: str | None, payload: bytes) -> str:
    if not payload:
        return ''
    if _is_binary_attachment(filename, content_type):
        return f'[Binary file: {filename}, {_format_size(len(payload))}]'
    raw_excerpt = payload[:4000].decode('utf-8', errors='replace')
    return raw_excerpt.replace('\x00', '')


def _add_recent_event(live_stats: dict, event_type: str, message: str) -> None:
    live_stats['recent_events'].append(
        {'type': event_type, 'message': message, 'timestamp': datetime.now(timezone.utc).isoformat()}
    )
    if len(live_stats['recent_events']) > RECENT_EVENTS_LIMIT:
        live_stats['recent_events'] = live_stats['recent_events'][-RECENT_EVENTS_LIMIT:]


def _calculate_rate(processed_count: int, started_at: datetime) -> float:
    elapsed_seconds = max((datetime.now(timezone.utc) - started_at).total_seconds(), 1.0)
    return round(processed_count / elapsed_seconds, 2)


def _estimated_remaining(total_emails: int, processed_count: int, emails_per_second: float) -> int | None:
    if emails_per_second <= 0:
        return None
    remaining = max(total_emails - processed_count, 0)
    return int(round(remaining / emails_per_second))


async def _publish_live_stats(job_id: int, live_stats: dict) -> None:
    redis = await get_redis()
    await redis.set(_live_stats_key(job_id), json.dumps(live_stats, default=str))


async def get_import_job_live_stats(job: ImportJob) -> dict:
    redis = await get_redis()
    cached = await redis.get(_live_stats_key(job.id))
    if cached:
        try:
            payload = json.loads(cached)
            payload['job_id'] = job.id
            payload['status'] = job.status
            payload['processed_count'] = job.processed_count
            payload['total_emails'] = job.total_emails
            payload['error_count'] = job.error_count
            return payload
        except Exception:  # pragma: no cover
            pass
    return {
        'job_id': job.id,
        'status': job.status,
        'total_emails': job.total_emails,
        'processed_count': job.processed_count,
        'error_count': job.error_count,
        'threads_created': 0,
        'contracts_found': 0,
        'attachments_extracted': 0,
        'spam_filtered': 0,
        'emails_per_second': 0.0,
        'estimated_remaining_seconds': None,
        'current_batch_start': 0,
        'category_distribution': {
            'Legal Review': 0,
            'Finance Review': 0,
            'Negotiation': 0,
            'General': 0,
            'Spam': 0,
        },
        'priority_distribution': {'P1': 0, 'P2': 0, 'P3': 0, 'P4': 0},
        'recent_events': [],
        'current_email_subject': None,
    }


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
    effective_batch_size = max(batch_size, 1)
    async with AsyncSessionLocal() as session:
        job = await session.get(ImportJob, job_id)
        if job is None:
            return
        started_at = datetime.now(timezone.utc)
        live_stats = {
            'job_id': job_id,
            'status': 'running',
            'total_emails': 0,
            'processed_count': 0,
            'error_count': 0,
            'threads_created': 0,
            'contracts_found': 0,
            'attachments_extracted': 0,
            'spam_filtered': 0,
            'emails_per_second': 0.0,
            'estimated_remaining_seconds': None,
            'current_batch_start': 0,
            'category_distribution': {
                'Legal Review': 0,
                'Finance Review': 0,
                'Negotiation': 0,
                'General': 0,
                'Spam': 0,
            },
            'priority_distribution': {'P1': 0, 'P2': 0, 'P3': 0, 'P4': 0},
            'recent_events': [],
            'current_email_subject': None,
        }
        try:
            job.status = 'running'
            job.started_at = started_at.isoformat()
            job.total_emails = count_mbox_messages(mbox_path)
            logger.info('Import job %s started, %s emails to process', job_id, job.total_emails)
            await session.commit()
            live_stats['total_emails'] = job.total_emails
            _add_recent_event(live_stats, 'info', f'Import started for {job.filename}')
            await _publish_live_stats(job.id, live_stats)
            await publish_json(
                f'import-job:{job.id}',
                {'status': job.status, 'processed_count': job.processed_count, 'total_emails': job.total_emails},
            )

            batch: list[ParsedEmail] = []
            batch_start = 0
            total_batches = max(1, ceil(job.total_emails / effective_batch_size)) if job.total_emails else 1
            batch_index = 0
            use_savepoint = bool(session.bind and session.bind.dialect.name != 'sqlite')

            for parsed_email in iter_mbox_messages(mbox_path):
                batch.append(parsed_email)
                if len(batch) < effective_batch_size:
                    continue
                current_batch = batch
                batch = []
                batch_index += 1
                live_stats['current_batch_start'] = batch_start
                _add_recent_event(live_stats, 'info', f'Processing batch {batch_index}/{total_batches}')
                try:
                    if use_savepoint:
                        async with session.begin_nested():
                            batch_stats = await _persist_batch(session, current_batch, job_id, settings.uploads_path, ai_service)
                    else:
                        batch_stats = await _persist_batch(session, current_batch, job_id, settings.uploads_path, ai_service)
                    job.processed_count += len(current_batch)
                    live_stats['processed_count'] = job.processed_count
                    live_stats['threads_created'] += batch_stats['threads_created']
                    live_stats['contracts_found'] += batch_stats['contracts_found']
                    live_stats['attachments_extracted'] += batch_stats['attachments_extracted']
                    live_stats['spam_filtered'] += batch_stats['spam_filtered']
                    for category, count in batch_stats['category_distribution'].items():
                        live_stats['category_distribution'][category] = live_stats['category_distribution'].get(category, 0) + count
                    for priority, count in batch_stats['priority_distribution'].items():
                        live_stats['priority_distribution'][priority] = live_stats['priority_distribution'].get(priority, 0) + count
                    live_stats['current_email_subject'] = batch_stats['current_email_subject']
                    logger.info('Job %s: processed batch, %s/%s done', job_id, job.processed_count, job.total_emails)
                except Exception as exc:  # pragma: no cover
                    logger.error('Job %s: batch error: %s', job_id, exc)
                    await session.rollback()
                    job = await session.get(ImportJob, job_id)
                    if job is None:
                        return
                    job.error_count += len(current_batch)
                    job.errors = [*job.errors, {'batch_start': batch_start, 'error': str(exc)}]
                    _add_recent_event(live_stats, 'warning', f'⚠️ Batch error: skipped {len(current_batch)} emails')
                await session.commit()
                live_stats['error_count'] = job.error_count
                live_stats['status'] = job.status
                live_stats['emails_per_second'] = _calculate_rate(job.processed_count, started_at)
                live_stats['estimated_remaining_seconds'] = _estimated_remaining(
                    job.total_emails, job.processed_count, live_stats['emails_per_second']
                )
                await _publish_live_stats(job.id, live_stats)
                await publish_json(
                    f'import-job:{job.id}',
                    {
                        'status': job.status,
                        'processed_count': job.processed_count,
                        'total_emails': job.total_emails,
                        'error_count': job.error_count,
                    },
                )
                batch_start += len(current_batch)

            if batch:
                batch_index += 1
                live_stats['current_batch_start'] = batch_start
                _add_recent_event(live_stats, 'info', f'Processing batch {batch_index}/{total_batches}')
                try:
                    if use_savepoint:
                        async with session.begin_nested():
                            batch_stats = await _persist_batch(session, batch, job_id, settings.uploads_path, ai_service)
                    else:
                        batch_stats = await _persist_batch(session, batch, job_id, settings.uploads_path, ai_service)
                    job.processed_count += len(batch)
                    live_stats['processed_count'] = job.processed_count
                    live_stats['threads_created'] += batch_stats['threads_created']
                    live_stats['contracts_found'] += batch_stats['contracts_found']
                    live_stats['attachments_extracted'] += batch_stats['attachments_extracted']
                    live_stats['spam_filtered'] += batch_stats['spam_filtered']
                    for category, count in batch_stats['category_distribution'].items():
                        live_stats['category_distribution'][category] = live_stats['category_distribution'].get(category, 0) + count
                    for priority, count in batch_stats['priority_distribution'].items():
                        live_stats['priority_distribution'][priority] = live_stats['priority_distribution'].get(priority, 0) + count
                    live_stats['current_email_subject'] = batch_stats['current_email_subject']
                    logger.info('Job %s: processed batch, %s/%s done', job_id, job.processed_count, job.total_emails)
                except Exception as exc:  # pragma: no cover
                    logger.error('Job %s: batch error: %s', job_id, exc)
                    await session.rollback()
                    job = await session.get(ImportJob, job_id)
                    if job is None:
                        return
                    job.error_count += len(batch)
                    job.errors = [*job.errors, {'batch_start': batch_start, 'error': str(exc)}]
                    _add_recent_event(live_stats, 'warning', f'⚠️ Batch error: skipped {len(batch)} emails')
                await session.commit()
                live_stats['error_count'] = job.error_count
                live_stats['status'] = job.status
                live_stats['emails_per_second'] = _calculate_rate(job.processed_count, started_at)
                live_stats['estimated_remaining_seconds'] = _estimated_remaining(
                    job.total_emails, job.processed_count, live_stats['emails_per_second']
                )
                await _publish_live_stats(job.id, live_stats)
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
            live_stats['status'] = job.status
            live_stats['processed_count'] = job.processed_count
            live_stats['error_count'] = job.error_count
            live_stats['emails_per_second'] = _calculate_rate(job.processed_count, started_at)
            live_stats['estimated_remaining_seconds'] = 0
            _add_recent_event(
                live_stats,
                'success',
                f'Import complete: {job.processed_count} processed with {job.error_count} errors',
            )
            await _publish_live_stats(job.id, live_stats)
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
            logger.info('Job %s completed', job_id)
        except Exception as exc:  # pragma: no cover
            logger.exception('Job %s failed: %s', job_id, exc)
            await session.rollback()
            job = await session.get(ImportJob, job_id)
            if job is None:
                return
            job.status = 'failed'
            job.completed_at = datetime.now(timezone.utc).isoformat()
            job.error_count += 1
            job.errors = [*job.errors, {'batch_start': -1, 'error': str(exc)}]
            await session.commit()
            live_stats['status'] = job.status
            live_stats['processed_count'] = job.processed_count
            live_stats['error_count'] = job.error_count
            _add_recent_event(live_stats, 'error', f'Import failed: {exc}')
            await _publish_live_stats(job.id, live_stats)
            await publish_json(
                f'import-job:{job.id}',
                {
                    'status': job.status,
                    'processed_count': job.processed_count,
                    'total_emails': job.total_emails,
                    'error_count': job.error_count,
                    'completed_at': job.completed_at,
                    'errors': job.errors,
                },
            )


async def _persist_batch(
    session: AsyncSession,
    batch: Iterable[ParsedEmail],
    job_id: int,
    uploads_root: Path,
    ai_service,
) -> dict:
    batch = list(batch)
    if not batch:
        return {
            'threads_created': 0,
            'contracts_found': 0,
            'attachments_extracted': 0,
            'spam_filtered': 0,
            'category_distribution': {},
            'priority_distribution': {},
            'current_email_subject': None,
        }
    stats = {
        'threads_created': 0,
        'contracts_found': 0,
        'attachments_extracted': 0,
        'spam_filtered': 0,
        'category_distribution': {},
        'priority_distribution': {},
        'current_email_subject': None,
    }
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
        if thread.email_count == 0:
            stats['threads_created'] += 1
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
        stats['current_email_subject'] = parsed.subject[:120]
        if classification.is_spam:
            stats['spam_filtered'] += 1
        category = classification.category or 'General'
        stats['category_distribution'][category] = (
            stats['category_distribution'].get(category, 0) + 1
        )
        if classification.priority:
            stats['priority_distribution'][classification.priority] = (
                stats['priority_distribution'].get(classification.priority, 0) + 1
            )
        content = ' '.join(filter(None, [parsed.subject, parsed.body_plain, parsed.body_html]))
        await upsert_contract(session, thread, classification.contract_numbers, content, stage, participants)
        stats['contracts_found'] += len(classification.contract_numbers)
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
            excerpt = _build_attachment_excerpt(attachment.filename, attachment.content_type, attachment.payload)
            analysis = await ai_service.analyze_attachment(attachment.filename, excerpt)
            stats['attachments_extracted'] += 1
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
    return stats
