from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin


class Thread(Base, TimestampMixin):
    __tablename__ = 'threads'

    id: Mapped[int] = mapped_column(primary_key=True)
    thread_key: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    subject_normalized: Mapped[str] = mapped_column(String(500), index=True, nullable=False)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey('contracts.id'), nullable=True)
    email_count: Mapped[int] = mapped_column(default=0, nullable=False)
    first_email_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_email_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    participants: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    ai_summary: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    stage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(50), nullable=True)

    emails = relationship('Email', back_populates='thread')
    contract = relationship('Contract', back_populates='threads')
