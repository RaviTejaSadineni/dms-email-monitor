from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.email import Email
from app.schemas.common import Pagination
from app.schemas.email import EmailListResponse, EmailRead
from app.services.auth_service import get_current_user

router = APIRouter(prefix='/emails', tags=['emails'])


@router.get('', response_model=EmailListResponse)
async def list_emails(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sender: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    query: str | None = None,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> EmailListResponse:
    statement = select(Email).options(selectinload(Email.attachments))
    count_statement = select(func.count()).select_from(Email)
    if sender:
        statement = statement.where(Email.sender == sender.lower())
        count_statement = count_statement.where(Email.sender == sender.lower())
    if priority:
        statement = statement.where(Email.priority == priority)
        count_statement = count_statement.where(Email.priority == priority)
    if category:
        statement = statement.where(Email.category == category)
        count_statement = count_statement.where(Email.category == category)
    if query:
        like = f'%{query.lower()}%'
        statement = statement.where(Email.subject.ilike(like) | Email.body_plain.ilike(like) | Email.body_html.ilike(like))
        count_statement = count_statement.where(Email.subject.ilike(like) | Email.body_plain.ilike(like) | Email.body_html.ilike(like))
    total = await session.scalar(count_statement) or 0
    statement = statement.order_by(Email.sent_at.desc().nullslast(), Email.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list((await session.execute(statement)).scalars().unique().all())
    return EmailListResponse(
        items=[EmailRead.model_validate(item) for item in items],
        pagination=Pagination(page=page, page_size=page_size, total=total),
    )


@router.get('/{email_id}', response_model=EmailRead)
async def get_email(email_id: int, session: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)) -> EmailRead:
    statement = select(Email).options(selectinload(Email.attachments)).where(Email.id == email_id)
    email = (await session.execute(statement)).scalar_one()
    return EmailRead.model_validate(email)
