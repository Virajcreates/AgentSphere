from typing import Any

from sqlalchemy import Select, select

from agentsphere.application.ports.repositories import ApiKeyRepositoryProtocol
from agentsphere.domain.models.api_key import ApiKeyModel
from agentsphere.infrastructure.persistence.repositories.base_repository import BaseRepository


class ApiKeyRepository(BaseRepository, ApiKeyRepositoryProtocol):
    def __init__(self, session: Any) -> None:
        super().__init__(session, ApiKeyModel)

    def _to_dict(self, instance: ApiKeyModel) -> dict[str, Any]:
        return {
            "id": instance.id,
            "tenant_id": instance.tenant_id,
            "key_prefix": instance.key_prefix,
            "key_hash": instance.key_hash,
            "name": instance.name,
            "scopes": instance.scopes,
            "expires_at": instance.expires_at,
            "last_used_at": instance.last_used_at,
            "is_active": instance.is_active,
            "created_at": instance.created_at,
        }

    async def get_by_key_hash(self, key_hash: str) -> dict[str, Any] | None:
        stmt: Select[Any] = select(ApiKeyModel).where(ApiKeyModel.key_hash == key_hash)
        result = await self._session.execute(stmt)
        instance = result.scalar_one_or_none()
        return self._to_dict(instance) if instance else None
