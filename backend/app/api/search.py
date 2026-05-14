from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.email import AttachmentRead, EmailRead
from app.services.auth_service import get_current_user
from app.services.search_service import search_attachments, search_emails

router = APIRouter(prefix='/search', tags=['search'])


@router.get('')
async def search(query: str = Query(..., min_length=2), session: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)) -> dict:
    emails = await search_emails(session, query)
    attachments = await search_attachments(session, query)
    return {
        'emails': [EmailRead.model_validate(item) for item in emails[:25]],
        'attachments': [AttachmentRead.model_validate(item) for item in attachments[:25]],
    }
