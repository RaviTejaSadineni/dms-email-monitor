from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin


class Classification(Base, TimestampMixin):
    __tablename__ = 'classifications'

    id: Mapped[int] = mapped_column(primary_key=True)
    email_id: Mapped[int] = mapped_column(ForeignKey('emails.id'), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(default=0.0, nullable=False)
    classified_by: Mapped[str] = mapped_column(String(50), default='ai', nullable=False)
    classified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    previous_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    previous_priority: Mapped[str | None] = mapped_column(String(50), nullable=True)

    email = relationship('Email', back_populates='classifications')
