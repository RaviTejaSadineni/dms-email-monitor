from __future__ import annotations

import os
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test_dms_email.db'
os.environ['SECRET_KEY'] = 'test-secret-key-with-32-bytes-minimum'

from app.database import AsyncSessionLocal, Base, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testserver') as async_client:
        yield async_client


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient):
    response = await client.post(
        '/api/auth/register',
        json={'email': 'admin@example.com', 'password': 'password123', 'full_name': 'Admin User'},
    )
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}
