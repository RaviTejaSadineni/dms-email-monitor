from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
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
    created_new_contract = False
    if contract_numbers:
        result = await session.execute(select(Contract).where(Contract.contract_number == contract_numbers[0]))
        contract = result.scalar_one_or_none()

    if contract is None:
        created_new_contract = True
        contract = Contract(
            contract_number=contract_numbers[0] if contract_numbers else None,
            contract_type=detect_contract_type(content),
            parties=sorted(set(parties)),
            current_stage=stage_name,
            status='in_progress',
            ai_summary=f'Contract lifecycle started in {stage_name or "Review"} stage.',
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
        if created_new_contract:
            session.add(ContractStage(contract_id=contract.id, stage_name=stage_name, entered_at=datetime.now(timezone.utc), is_current=True))
        else:
            stage_result = await session.execute(select(ContractStage).where(ContractStage.contract_id == contract.id))
            stages = list(stage_result.scalars().all())
            for existing in stages:
                if existing.is_current and existing.stage_name != stage_name:
                    existing.is_current = False
                    if existing.exited_at is None:
                        existing.exited_at = datetime.now(timezone.utc)
                        delta = existing.exited_at - existing.entered_at
                        existing.duration_hours = round(delta.total_seconds() / 3600, 2)
            current = next((item for item in stages if item.stage_name == stage_name and item.is_current), None)
            if current is None:
                session.add(
                    ContractStage(contract_id=contract.id, stage_name=stage_name, entered_at=datetime.now(timezone.utc), is_current=True)
                )

    lowered = content.lower()
    existing_clauses_by_type: dict[str, NegotiationClause] = {}
    if not created_new_contract:
        clause_result = await session.execute(select(NegotiationClause).where(NegotiationClause.contract_id == contract.id))
        existing_clauses_by_type = {item.clause_type: item for item in clause_result.scalars().all()}
    for clause_name, keywords in CLAUSE_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            if created_new_contract:
                session.add(
                    NegotiationClause(contract_id=contract.id, clause_type=clause_name, round_count=1, details='Detected from email body')
                )
            else:
                clause = existing_clauses_by_type.get(clause_name)
                if clause is None:
                    session.add(
                        NegotiationClause(
                            contract_id=contract.id,
                            clause_type=clause_name,
                            round_count=1,
                            details='Detected from email body',
                        )
                    )
                else:
                    clause.round_count += 1

    thread.contract = contract
    return contract
