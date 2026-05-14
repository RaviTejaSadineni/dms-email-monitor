from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.email import AttachmentRead
from app.services.attachment_service import list_attachments, read_attachment_excerpt
from app.services.auth_service import get_current_user

router = APIRouter(prefix='/attachments', tags=['attachments'])


@router.get('')
async def attachments(query: str | None = Query(None), session: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)) -> dict:
    items = await list_attachments(session, query)
    return {'items': [AttachmentRead.model_validate(item) for item in items]}


@router.get('/{attachment_id}')
async def attachment_detail(attachment_id: int, session: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)) -> dict:
    from app.models.attachment import Attachment
    attachment = await session.get(Attachment, attachment_id)
    return {'item': AttachmentRead.model_validate(attachment), 'preview': read_attachment_excerpt(attachment.storage_path)}
