from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository(ABC):
    def __init__(self, session: AsyncSession, model_class: type[Any]) -> None:
        self._session = session
        self._model_class = model_class

    @abstractmethod
    def _to_dict(self, instance: Any) -> dict[str, Any]: ...

    async def get(self, id: UUID, tenant_id: UUID | None = None) -> dict[str, Any] | None:
        stmt: Any = select(self._model_class).where(self._model_class.id == id)
        if tenant_id is not None:
            stmt = stmt.where(self._model_class.tenant_id == tenant_id)
        result = await self._session.execute(stmt)
        instance = result.scalar_one_or_none()
        return self._to_dict(instance) if instance else None

    async def get_all(self, tenant_id: UUID | None = None, **filters: Any) -> list[dict[str, Any]]:
        stmt: Any = select(self._model_class)
        if tenant_id is not None:
            stmt = stmt.where(self._model_class.tenant_id == tenant_id)
        for key, value in filters.items():
            if hasattr(self._model_class, key):
                stmt = stmt.where(getattr(self._model_class, key) == value)
        result = await self._session.execute(stmt)
        instances = result.scalars().all()
        return [self._to_dict(inst) for inst in instances]

    async def create(self, **kwargs: Any) -> dict[str, Any]:
        instance = self._model_class(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        return self._to_dict(instance)

    async def update(
        self, id: UUID, tenant_id: UUID | None = None, **kwargs: Any
    ) -> dict[str, Any] | None:
        stmt: Any = update(self._model_class).where(self._model_class.id == id)
        if tenant_id is not None:
            stmt = stmt.where(self._model_class.tenant_id == tenant_id)
        stmt = stmt.values(**kwargs).returning(self._model_class)
        result: Any = await self._session.execute(stmt)
        instance = result.scalar_one_or_none()
        return self._to_dict(instance) if instance else None

    async def delete(self, id: UUID, tenant_id: UUID | None = None) -> bool:
        stmt: Any = delete(self._model_class).where(self._model_class.id == id)
        if tenant_id is not None:
            stmt = stmt.where(self._model_class.tenant_id == tenant_id)
        result: Any = await self._session.execute(stmt)
        return bool(result.rowcount)

    async def exists(self, id: UUID, tenant_id: UUID | None = None) -> bool:
        stmt: Any = select(self._model_class).where(self._model_class.id == id)
        if tenant_id is not None:
            stmt = stmt.where(self._model_class.tenant_id == tenant_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
