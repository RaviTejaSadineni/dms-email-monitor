from __future__ import annotations

from pathlib import Path

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attachment import Attachment


async def list_attachments(session: AsyncSession, query: str | None = None) -> list[Attachment]:
    statement = select(Attachment).order_by(Attachment.created_at.desc())
    if query:
        like = f'%{query.lower()}%'
        statement = statement.where(
            or_(Attachment.filename.ilike(like), Attachment.ai_extracted_text.ilike(like), Attachment.ai_analysis.ilike(like))
        )
    result = await session.execute(statement)
    return list(result.scalars().all())


def read_attachment_excerpt(storage_path: str, limit: int = 1200) -> str:
    path = Path(storage_path)
    if not path.exists() or not path.is_file():
        return ''
    data = path.read_bytes()[:limit]
    try:
        return data.decode('utf-8', errors='replace')
    except Exception:  # pragma: no cover
        return ''
