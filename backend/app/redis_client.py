from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.config import get_settings


class InMemoryRedis:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._lists: dict[str, list[str]] = {}

    async def set(self, key: str, value: str) -> None:
        self._store[key] = value

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def lpush(self, key: str, value: str) -> None:
        self._lists.setdefault(key, []).insert(0, value)

    async def lrange(self, key: str, start: int, stop: int) -> list[str]:
        values = self._lists.get(key, [])
        end = None if stop == -1 else stop + 1
        return values[start:end]


_fallback = InMemoryRedis()
_redis: Redis | InMemoryRedis | None = None


async def get_redis() -> Redis | InMemoryRedis:
    global _redis
    if _redis is not None:
        return _redis

    settings = get_settings()
    client = Redis.from_url(settings.redis_url, encoding='utf-8', decode_responses=True)
    try:
        await client.ping()
        _redis = client
    except RedisError:
        _redis = _fallback
    return _redis


async def publish_json(key: str, payload: dict[str, Any]) -> None:
    redis = await get_redis()
    await redis.set(key, json.dumps(payload, default=str))
