from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel, Pagination


class ContractStageCreate(BaseModel):
    stage_name: str = Field(min_length=1, max_length=100)
    entered_at: datetime
    exited_at: datetime | None = None
    assignee: str | None = None
    notes: str | None = None


class ContractStageRead(ORMModel):
    id: int
    stage_name: str
    entered_at: datetime
    exited_at: datetime | None
    duration_hours: float | None
    assignee: str | None
    notes: str | None
    is_current: bool


class ContractCreate(BaseModel):
    contract_number: str | None = None
    contract_type: str | None = None
    parties: list[str] = []
    status: str = 'active'
    current_stage: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    renewal_date: date | None = None
    value_amount: float | None = None
    value_currency: str | None = None
    risk_score: float | None = None
    ai_summary: str | None = None


class ContractRead(ORMModel):
    id: int
    contract_number: str | None
    contract_type: str | None
    parties: list[str]
    status: str
    current_stage: str | None
    start_date: date | None
    end_date: date | None
    renewal_date: date | None
    value_amount: float | None
    value_currency: str | None
    risk_score: float | None
    cycle_time_days: float | None
    sla_breached: bool
    sla_target_days: int
    ai_summary: str | None
    stages: list[ContractStageRead] = []


class ContractListResponse(BaseModel):
    items: list[ContractRead]
    pagination: Pagination
