from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.contract import Contract, ContractStage
from app.schemas.common import Pagination
from app.schemas.contract import ContractCreate, ContractListResponse, ContractRead, ContractStageCreate, ContractStageRead
from app.services.auth_service import get_current_user

router = APIRouter(prefix='/contracts', tags=['contracts'])


@router.get('', response_model=ContractListResponse)
async def list_contracts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    stage: str | None = None,
    contract_type: str | None = None,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ContractListResponse:
    statement = select(Contract).options(selectinload(Contract.stages))
    count_statement = select(func.count()).select_from(Contract)
    if stage:
        statement = statement.where(Contract.current_stage == stage)
        count_statement = count_statement.where(Contract.current_stage == stage)
    if contract_type:
        statement = statement.where(Contract.contract_type == contract_type)
        count_statement = count_statement.where(Contract.contract_type == contract_type)
    total = await session.scalar(count_statement) or 0
    items = list(
        (
            await session.execute(
                statement.order_by(Contract.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
            )
        ).scalars().unique().all()
    )
    return ContractListResponse(
        items=[ContractRead.model_validate(item) for item in items],
        pagination=Pagination(page=page, page_size=page_size, total=total),
    )


@router.post('', response_model=ContractRead, status_code=status.HTTP_201_CREATED)
async def create_contract(
    payload: ContractCreate,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ContractRead:
    contract = Contract(**payload.model_dump())
    session.add(contract)
    await session.commit()
    await session.refresh(contract)
    return ContractRead.model_validate(
        {
            **payload.model_dump(),
            'id': contract.id,
            'cycle_time_days': contract.cycle_time_days,
            'sla_breached': contract.sla_breached,
            'sla_target_days': contract.sla_target_days,
            'stages': [],
        }
    )


@router.get('/{contract_id}', response_model=ContractRead)
async def get_contract(contract_id: int, session: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)) -> ContractRead:
    contract = (
        await session.execute(select(Contract).options(selectinload(Contract.stages)).where(Contract.id == contract_id))
    ).scalar_one_or_none()
    if contract is None:
        raise HTTPException(status_code=404, detail='Contract not found')
    return ContractRead.model_validate(contract)


@router.post('/{contract_id}/stages', response_model=ContractStageRead, status_code=status.HTTP_201_CREATED)
async def add_stage(
    contract_id: int,
    payload: ContractStageCreate,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ContractStageRead:
    contract = await session.get(Contract, contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail='Contract not found')
    stage = ContractStage(contract_id=contract_id, stage_name=payload.stage_name, entered_at=payload.entered_at, exited_at=payload.exited_at, assignee=payload.assignee, notes=payload.notes, is_current=payload.exited_at is None)
    session.add(stage)
    contract.current_stage = payload.stage_name
    await session.commit()
    await session.refresh(stage)
    return ContractStageRead.model_validate(stage)
