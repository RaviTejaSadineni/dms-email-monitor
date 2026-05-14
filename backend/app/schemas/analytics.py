from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ChartPoint, MetricCard, ORMModel


class StageMetric(BaseModel):
    stage: str
    count: int
    average_hours: float
    breach_rate: float


class AnalyticsSummaryResponse(BaseModel):
    metrics: list[MetricCard]
    priority_distribution: list[ChartPoint]
    category_distribution: list[ChartPoint]
    lifecycle_pipeline: list[StageMetric]
    email_volume: list[ChartPoint]
    response_time_distribution: list[ChartPoint]
    stakeholder_activity: list[ChartPoint]


class ImportJobCreate(BaseModel):
    mbox_path: str
    batch_size: int = 500


class ImportJobRead(ORMModel):
    id: int
    filename: str
    file_size_bytes: int
    status: str
    total_emails: int
    processed_count: int
    error_count: int
    errors: list[dict]
    started_at: str | None
    completed_at: str | None


class AIInsightRead(ORMModel):
    id: int
    entity_type: str
    entity_id: int
    insight_type: str
    title: str
    content: str
    confidence: float
    metadata: dict = Field(alias='details')
