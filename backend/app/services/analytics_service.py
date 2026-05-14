from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attachment import Attachment
from app.models.contract import Contract, ContractStage
from app.models.email import Email
from app.models.thread import Thread
from app.schemas.analytics import AnalyticsSummaryResponse, StageMetric
from app.schemas.common import ChartPoint, MetricCard

PIPELINE_STAGES = [
    'Request',
    'Legal Review',
    'Finance Review',
    'Procurement/Compliance',
    'Redline Negotiation',
    'Leadership Sign-off',
    'Repository & Obligation Tracking',
]


async def build_summary(session: AsyncSession) -> AnalyticsSummaryResponse:
    total_emails = await session.scalar(select(func.count()).select_from(Email)) or 0
    total_contracts = await session.scalar(select(func.count()).select_from(Contract)) or 0
    total_threads = await session.scalar(select(func.count()).select_from(Thread)) or 0
    total_attachments = await session.scalar(select(func.count()).select_from(Attachment)) or 0
    breached = await session.scalar(select(func.count()).select_from(Contract).where(Contract.sla_breached.is_(True))) or 0
    avg_cycle = await session.scalar(select(func.avg(Contract.cycle_time_days)).select_from(Contract)) or 0

    email_rows = (await session.execute(select(Email.priority, func.count()).group_by(Email.priority))).all()
    category_rows = (await session.execute(select(Email.category, func.count()).group_by(Email.category))).all()

    stage_counts = defaultdict(lambda: {'count': 0, 'durations': []})
    for stage_name, avg_hours, count in (
        await session.execute(
            select(ContractStage.stage_name, func.avg(ContractStage.duration_hours), func.count()).group_by(ContractStage.stage_name)
        )
    ).all():
        stage_counts[stage_name]['count'] = count
        if avg_hours is not None:
            stage_counts[stage_name]['durations'].append(float(avg_hours))

    email_dates = Counter()
    stakeholder_counts = Counter()
    response_buckets = Counter({'<4h': 0, '4-8h': 0, '8-24h': 0, '>24h': 0})
    emails = (await session.execute(select(Email))).scalars().all()
    sorted_emails = sorted((email for email in emails if email.sent_at), key=lambda item: item.sent_at)
    previous_by_thread: dict[int, object] = {}
    for email in emails:
        if email.sent_at:
            email_dates[email.sent_at.date().isoformat()] += 1
        stakeholder_counts[email.sender] += 1
        if email.thread_id and email.sent_at and email.thread_id in previous_by_thread:
            delta = email.sent_at - previous_by_thread[email.thread_id]
            hours = delta.total_seconds() / 3600
            if hours < 4:
                response_buckets['<4h'] += 1
            elif hours < 8:
                response_buckets['4-8h'] += 1
            elif hours < 24:
                response_buckets['8-24h'] += 1
            else:
                response_buckets['>24h'] += 1
        if email.thread_id and email.sent_at:
            previous_by_thread[email.thread_id] = email.sent_at

    lifecycle = []
    for stage in PIPELINE_STAGES:
        info = stage_counts[stage]
        avg_hours = mean(info['durations']) if info['durations'] else 0.0
        breach_rate = round((breached / total_contracts) * 100, 2) if total_contracts else 0.0
        lifecycle.append(StageMetric(stage=stage, count=info['count'], average_hours=round(avg_hours, 2), breach_rate=breach_rate))

    metrics = [
        MetricCard(title='Emails Processed', value=total_emails, subtitle='Imported Gmail Takeout emails'),
        MetricCard(title='Contracts Tracked', value=total_contracts, subtitle='Active contract lifecycles'),
        MetricCard(title='Conversation Threads', value=total_threads, subtitle='Merged email conversations'),
        MetricCard(title='SLA Breach Rate', value=f'{round((breached / total_contracts) * 100, 2) if total_contracts else 0}%'),
        MetricCard(title='Average Cycle Time', value=round(float(avg_cycle or 0), 2), subtitle='Days end-to-end'),
        MetricCard(title='Attachments Indexed', value=total_attachments, subtitle='AI-ready attachment records'),
    ]

    return AnalyticsSummaryResponse(
        metrics=metrics,
        priority_distribution=[ChartPoint(label=label or 'Unassigned', value=count) for label, count in email_rows],
        category_distribution=[ChartPoint(label=label or 'Unclassified', value=count) for label, count in category_rows],
        lifecycle_pipeline=lifecycle,
        email_volume=[ChartPoint(label=label, value=value) for label, value in sorted(email_dates.items())[-14:]],
        response_time_distribution=[ChartPoint(label=label, value=value) for label, value in response_buckets.items()],
        stakeholder_activity=[ChartPoint(label=label, value=value) for label, value in stakeholder_counts.most_common(8)],
    )


async def build_ai_insights(session: AsyncSession) -> list[dict]:
    summary = await build_summary(session)
    insight_cards = [
        {
            'title': 'Negotiation Loop Focus',
            'content': 'Track liability, indemnity, and payment terms to reduce redline churn and accelerate approvals.',
            'confidence': 0.81,
        },
        {
            'title': 'SLA Risk',
            'content': f"{next((metric.value for metric in summary.metrics if metric.title == 'SLA Breach Rate'), '0%')} of tracked contracts are currently breaching SLA.",
            'confidence': 0.76,
        },
        {
            'title': 'Early Engagement',
            'content': 'Trigger customer follow-ups during request and procurement stages to reduce inactivity-related delays.',
            'confidence': 0.72,
        },
    ]
    return insight_cards
