from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default='analyst', nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    import_jobs = relationship('ImportJob', back_populates='user')
    audit_logs = relationship('AuditLog', back_populates='user')
    saved_filters = relationship('SavedFilter', back_populates='user')
