from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshResponse, RegisterRequest, TokenResponse, UserRead
from app.services.auth_service import authenticate_user, create_access_token, get_current_user, hash_password

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_db)) -> TokenResponse:
    existing = await session.execute(select(User).where(User.email == payload.email.lower()))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail='User already exists')
    user = User(email=payload.email.lower(), password_hash=hash_password(payload.password), full_name=payload.full_name)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return TokenResponse(access_token=create_access_token(user), user=UserRead.model_validate(user))


@router.post('/login', response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await authenticate_user(session, payload.email.lower(), payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail='Invalid email or password')
    return TokenResponse(access_token=create_access_token(user), user=UserRead.model_validate(user))


@router.post('/refresh', response_model=RefreshResponse)
async def refresh(current_user: User = Depends(get_current_user)) -> RefreshResponse:
    token = create_access_token(current_user, expires_delta=timedelta(minutes=60))
    return RefreshResponse(access_token=token)


@router.get('/me', response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
