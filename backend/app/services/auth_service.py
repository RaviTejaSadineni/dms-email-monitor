from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.user import User

security = HTTPBearer(auto_error=False)
settings = get_settings()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=2**14, r=8, p=1)
    return base64.b64encode(salt + digest).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    raw = base64.b64decode(password_hash.encode('utf-8'))
    salt, stored = raw[:16], raw[16:]
    calculated = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=2**14, r=8, p=1)
    return hmac.compare_digest(stored, calculated)


def create_access_token(user: User, expires_delta: timedelta | None = None) -> str:
    expire_at = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.jwt_expire_minutes))
    payload = {'sub': str(user.id), 'email': user.email, 'role': user.role, 'exp': expire_at}
    return jwt.encode(payload, settings.secret_key, algorithm='HS256')


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=['HS256'], options={'require': ['exp', 'sub']})
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid bearer token') from exc


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    session: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != 'bearer':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing bearer token')
    payload = decode_access_token(credentials.credentials)
    user = await session.get(User, int(payload['sub']))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User is not active')
    return user
