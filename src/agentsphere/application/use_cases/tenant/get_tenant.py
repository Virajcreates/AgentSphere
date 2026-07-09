from collections.abc import Callable
from typing import Any
from uuid import UUID

from agentsphere.application.ports.repositories import TenantRepositoryProtocol
from agentsphere.common.exceptions import NotFoundError


class GetTenantUseCase:
    def __init__(
        self,
        db: Any,
        tenant_repo_factory: Callable[..., TenantRepositoryProtocol],
    ) -> None:
        self._db = db
        self._tenant_repo_factory = tenant_repo_factory

    async def execute(self, tenant_id: UUID) -> dict[str, Any]:
        async with await self._db.get_session() as session:
            repo = self._tenant_repo_factory(session=session)
            tenant = await repo.get(tenant_id)
            if not tenant:
                raise NotFoundError("Tenant", tenant_id)
            return tenant
