from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.attachment import Attachment
from app.models.email import Email


async def search_emails(session: AsyncSession, query: str) -> list[Email]:
    like = f'%{query.lower()}%'
    statement = (
        select(Email)
        .options(selectinload(Email.attachments))
        .where(
            or_(
                Email.subject.ilike(like),
                Email.body_plain.ilike(like),
                Email.body_html.ilike(like),
                Email.sender.ilike(like),
            )
        )
        .order_by(Email.sent_at.desc().nullslast(), Email.created_at.desc())
    )
    result = await session.execute(statement)
    return list(result.scalars().unique().all())


async def search_attachments(session: AsyncSession, query: str) -> list[Attachment]:
    like = f'%{query.lower()}%'
    statement = select(Attachment).where(
        or_(Attachment.filename.ilike(like), Attachment.ai_extracted_text.ilike(like), Attachment.ai_analysis.ilike(like))
    )
    result = await session.execute(statement)
    return list(result.scalars().all())
