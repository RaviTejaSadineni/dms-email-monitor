from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin


class Attachment(Base, TimestampMixin):
    __tablename__ = 'attachments'

    id: Mapped[int] = mapped_column(primary_key=True)
    email_id: Mapped[int] = mapped_column(ForeignKey('emails.id'), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    size_bytes: Mapped[int] = mapped_column(default=0, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    ai_extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)

    email = relationship('Email', back_populates='attachments')
