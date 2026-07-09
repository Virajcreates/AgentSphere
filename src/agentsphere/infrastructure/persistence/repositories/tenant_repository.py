from typing import Any

from sqlalchemy import Select, select

from agentsphere.application.ports.repositories import TenantRepositoryProtocol
from agentsphere.domain.models.tenant import TenantModel
from agentsphere.infrastructure.persistence.repositories.base_repository import BaseRepository


class TenantRepository(BaseRepository, TenantRepositoryProtocol):
    def __init__(self, session: Any) -> None:
        super().__init__(session, TenantModel)

    def _to_dict(self, instance: TenantModel) -> dict[str, Any]:
        return {
            "id": instance.id,
            "name": instance.name,
            "slug": instance.slug,
            "settings": instance.settings,
            "feature_flags": instance.feature_flags,
            "is_active": instance.is_active,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }

    async def get_by_slug(self, slug: str) -> dict[str, Any] | None:
        stmt: Select[Any] = select(TenantModel).where(TenantModel.slug == slug)
        result = await self._session.execute(stmt)
        instance = result.scalar_one_or_none()
        return self._to_dict(instance) if instance else None
