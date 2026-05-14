from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin


class Contract(Base, TimestampMixin):
    __tablename__ = 'contracts'

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_number: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    contract_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parties: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(100), default='active', nullable=False)
    current_stage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    renewal_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    value_amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    value_currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    risk_score: Mapped[float | None] = mapped_column(nullable=True)
    cycle_time_days: Mapped[float | None] = mapped_column(nullable=True)
    sla_breached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sla_target_days: Mapped[int] = mapped_column(default=15, nullable=False)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    threads = relationship('Thread', back_populates='contract')
    stages = relationship('ContractStage', back_populates='contract', cascade='all, delete-orphan')
    clauses = relationship('NegotiationClause', back_populates='contract', cascade='all, delete-orphan')


class ContractStage(Base, TimestampMixin):
    __tablename__ = 'contract_stages'

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey('contracts.id'), nullable=False, index=True)
    stage_name: Mapped[str] = mapped_column(String(100), nullable=False)
    entered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_hours: Mapped[float | None] = mapped_column(nullable=True)
    assignee: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    contract = relationship('Contract', back_populates='stages')


class NegotiationClause(Base, TimestampMixin):
    __tablename__ = 'negotiation_clauses'

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey('contracts.id'), nullable=False, index=True)
    clause_type: Mapped[str] = mapped_column(String(100), nullable=False)
    round_count: Mapped[int] = mapped_column(default=1, nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)

    contract = relationship('Contract', back_populates='clauses')
