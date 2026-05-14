from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel, Pagination


class AttachmentRead(ORMModel):
    id: int
    filename: str
    content_type: str | None
    size_bytes: int
    storage_path: str
    ai_extracted_text: str | None
    ai_analysis: str | None


class EmailRead(ORMModel):
    id: int
    message_id: str
    subject: str
    sender: str
    recipients_to: list[str]
    recipients_cc: list[str]
    recipients_bcc: list[str]
    body_plain: str | None
    body_html: str | None
    sent_at: datetime | None
    received_at: datetime | None
    labels: list[str]
    priority: str | None
    category: str | None
    sentiment: str | None
    ai_summary: str | None
    is_spam: bool
    size_bytes: int
    has_attachments: bool
    is_forwarded: bool
    is_auto_reply: bool
    language: str | None
    attachments: list[AttachmentRead] = []


class EmailListResponse(BaseModel):
    items: list[EmailRead]
    pagination: Pagination
