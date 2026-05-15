from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger

from app.database import Base, TimestampMixin


class AIInsight(Base, TimestampMixin):
    __tablename__ = 'ai_insights'

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[int] = mapped_column(nullable=False)
    insight_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(default=0.0, nullable=False)
    details: Mapped[dict] = mapped_column('metadata', JSON, default=dict, nullable=False)


class ImportJob(Base, TimestampMixin):
    __tablename__ = 'import_jobs'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default='pending', nullable=False)
    total_emails: Mapped[int] = mapped_column(default=0, nullable=False)
    processed_count: Mapped[int] = mapped_column(default=0, nullable=False)
    error_count: Mapped[int] = mapped_column(default=0, nullable=False)
    errors: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    started_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    completed_at: Mapped[str | None] = mapped_column(String(50), nullable=True)

    user = relationship('User', back_populates='import_jobs')


class SavedFilter(Base, TimestampMixin):
    __tablename__ = 'saved_filters'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    filters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    user = relationship('User', back_populates='saved_filters')
