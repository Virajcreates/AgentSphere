from typing import Any
from uuid import UUID

from sqlalchemy import Select, select

from agentsphere.application.ports.repositories import UserRepositoryProtocol
from agentsphere.domain.models.user import UserModel
from agentsphere.infrastructure.persistence.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository, UserRepositoryProtocol):
    def __init__(self, session: Any) -> None:
        super().__init__(session, UserModel)

    def _to_dict(self, instance: UserModel) -> dict[str, Any]:
        return {
            "id": instance.id,
            "tenant_id": instance.tenant_id,
            "email": instance.email,
            "password_hash": instance.password_hash,
            "display_name": instance.display_name,
            "role": instance.role,
            "is_active": instance.is_active,
            "last_login": instance.last_login,
            "created_at": instance.created_at,
        }

    async def get_by_email(self, email: str) -> dict[str, Any] | None:
        stmt: Select[Any] = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        instance = result.scalar_one_or_none()
        return self._to_dict(instance) if instance else None

    async def get_by_tenant(self, tenant_id: UUID) -> list[dict[str, Any]]:
        return await self.get_all(tenant_id=tenant_id)
