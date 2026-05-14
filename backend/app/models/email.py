from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin


class Email(Base, TimestampMixin):
    __tablename__ = 'emails'

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[str] = mapped_column(String(500), unique=True, index=True, nullable=False)
    thread_id: Mapped[int | None] = mapped_column(ForeignKey('threads.id'), nullable=True)
    subject: Mapped[str] = mapped_column(String(1000), default='', nullable=False)
    sender: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    recipients_to: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    recipients_cc: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    recipients_bcc: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    body_plain: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    labels: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    priority: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    sentiment: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_spam: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    raw_headers: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    import_batch_id: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    size_bytes: Mapped[int] = mapped_column(default=0, nullable=False)
    has_attachments: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_forwarded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_auto_reply: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    language: Mapped[str | None] = mapped_column(String(20), nullable=True)
    thread_header_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    in_reply_to: Mapped[str | None] = mapped_column(String(500), nullable=True)
    references: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    thread = relationship('Thread', back_populates='emails')
    attachments = relationship('Attachment', back_populates='email', cascade='all, delete-orphan')
    classifications = relationship('Classification', back_populates='email', cascade='all, delete-orphan')
