from typing import Any, cast

import orjson
from redis.asyncio import ConnectionPool, Redis


class RedisManager:
    _pool: ConnectionPool | None = None
    _client: Redis | None = None

    async def init(self, redis_url: str) -> None:
        self._pool = ConnectionPool.from_url(
            redis_url,
            max_connections=50,
            decode_responses=True,
        )
        self._client = Redis(connection_pool=self._pool)

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None

    @property
    def client(self) -> Redis:
        if self._client is None:
            raise RuntimeError("Redis not initialized")
        return self._client

    async def health_check(self) -> bool:
        try:
            return await self.client.ping()
        except Exception:
            return False

    async def set_json(self, key: str, value: dict[str, Any], ttl: int | None = None) -> None:
        data = orjson.dumps(value)
        if ttl:
            await self.client.setex(key, ttl, data)
        else:
            await self.client.set(key, data)

    async def get_json(self, key: str) -> dict[str, Any] | None:
        data = await self.client.get(key)
        if data is None:
            return None
        return cast(dict[str, Any], orjson.loads(data))
