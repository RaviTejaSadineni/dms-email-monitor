from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class Pagination(BaseModel):
    page: int
    page_size: int
    total: int


class MetricCard(BaseModel):
    title: str
    value: float | int | str
    change: float | None = None
    subtitle: str | None = None


class ChartPoint(BaseModel):
    label: str
    value: float | int


class TimestampedModel(ORMModel):
    created_at: datetime
    updated_at: datetime
