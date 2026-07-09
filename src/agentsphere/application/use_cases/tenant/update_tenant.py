from collections.abc import Callable
from typing import Any, cast
from uuid import UUID

from agentsphere.application.ports.repositories import TenantRepositoryProtocol
from agentsphere.common.exceptions import NotFoundError, ValidationError


class UpdateTenantUseCase:
    def __init__(
        self,
        db: Any,
        tenant_repo_factory: Callable[..., TenantRepositoryProtocol],
    ) -> None:
        self._db = db
        self._tenant_repo_factory = tenant_repo_factory

    async def execute(
        self, tenant_id: UUID, name: str | None = None, settings: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        async with await self._db.get_session() as session:
            repo = self._tenant_repo_factory(session=session)
            tenant = await repo.get(tenant_id)
            if not tenant:
                raise NotFoundError("Tenant", tenant_id)

            if name is not None:
                if not name.strip():
                    raise ValidationError("Tenant name cannot be empty")
                await repo.update(tenant_id, name=name.strip())

            if settings is not None:
                await repo.update(tenant_id, settings=settings)

            result = await repo.get(tenant_id)
            return cast(dict[str, Any], result)
