from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.thread import Thread


async def get_or_create_thread(
    session: AsyncSession,
    thread_key: str,
    subject_normalized: str,
    participants: list[str],
    sent_at: datetime | None,
    stage: str | None,
    priority: str | None,
) -> Thread:
    result = await session.execute(select(Thread).where(Thread.thread_key == thread_key))
    thread = result.scalar_one_or_none()
    if thread is None:
        thread = Thread(
            thread_key=thread_key,
            subject_normalized=subject_normalized or 'untitled-thread',
            participants=sorted(set(participants)),
            first_email_at=sent_at,
            last_email_at=sent_at,
            email_count=0,
            stage=stage,
            priority=priority,
        )
        session.add(thread)
        await session.flush()
        return thread
    if sent_at and (thread.first_email_at is None or sent_at < thread.first_email_at):
        thread.first_email_at = sent_at
    if sent_at and (thread.last_email_at is None or sent_at > thread.last_email_at):
        thread.last_email_at = sent_at
    thread.participants = sorted(set((thread.participants or []) + participants))
    thread.stage = stage or thread.stage
    thread.priority = priority or thread.priority
    return thread
