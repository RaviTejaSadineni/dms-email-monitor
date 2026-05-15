from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contract import Contract, ContractStage, NegotiationClause
from app.models.thread import Thread
from app.services.classification_service import detect_contract_type, extract_amount

STAGE_MAP = {
    'Contract Request': 'Request',
    'Legal Review': 'Legal Review',
    'Finance Review': 'Finance Review',
    'Procurement': 'Procurement/Compliance',
    'Compliance': 'Procurement/Compliance',
    'Negotiation/Redline': 'Redline Negotiation',
    'Sign-off': 'Leadership Sign-off',
}

CLAUSE_KEYWORDS = {
    'Liability': ['liability'],
    'Indemnity': ['indemnity'],
    'Payment Terms': ['payment terms', 'net 30', 'pricing'],
    'Data Privacy': ['data privacy', 'gdpr', 'security'],
}


async def upsert_contract(
    session: AsyncSession,
    thread: Thread,
    contract_numbers: list[str],
    content: str,
    stage_name: str | None,
    parties: list[str],
) -> Contract | None:
    if not contract_numbers and not stage_name:
        return None

    contract = None
    if contract_numbers:
        result = await session.execute(
            select(Contract)
            .options(selectinload(Contract.stages), selectinload(Contract.clauses))
            .where(Contract.contract_number == contract_numbers[0])
        )
        contract = result.scalar_one_or_none()

    if contract is None:
        contract = Contract(
            contract_number=contract_numbers[0] if contract_numbers else None,
            contract_type=detect_contract_type(content),
            parties=sorted(set(parties)),
            current_stage=stage_name,
            status='in_progress',
            ai_summary=f'Contract lifecycle started in {stage_name or "Review"} stage.',
            stages=[],
            clauses=[],
        )
        amount, currency = extract_amount(content)
        contract.value_amount = amount
        contract.value_currency = currency
        session.add(contract)
        await session.flush()
    else:
        contract.parties = sorted(set((contract.parties or []) + parties))
        contract.current_stage = stage_name or contract.current_stage
        if contract.contract_type is None:
            contract.contract_type = detect_contract_type(content)
        if contract.ai_summary is None:
            contract.ai_summary = f'Contract lifecycle currently in {contract.current_stage or "Review"} stage.'

    if stage_name:
        for existing in contract.stages:
            if existing.is_current and existing.stage_name != stage_name:
                existing.is_current = False
                if existing.exited_at is None:
                    existing.exited_at = datetime.now(timezone.utc)
                    delta = existing.exited_at - existing.entered_at
                    existing.duration_hours = round(delta.total_seconds() / 3600, 2)
        current = next((item for item in contract.stages if item.stage_name == stage_name and item.is_current), None)
        if current is None:
            contract.stages.append(
                ContractStage(stage_name=stage_name, entered_at=datetime.now(timezone.utc), is_current=True)
            )

    lowered = content.lower()
    for clause_name, keywords in CLAUSE_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            clause = next((item for item in contract.clauses if item.clause_type == clause_name), None)
            if clause is None:
                contract.clauses.append(NegotiationClause(clause_type=clause_name, round_count=1, details='Detected from email body'))
            else:
                clause.round_count += 1

    thread.contract = contract
    return contract
