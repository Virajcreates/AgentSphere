from collections.abc import Callable
from typing import Any

from agentsphere.application.ports.repositories import TenantRepositoryProtocol
from agentsphere.common.exceptions import ConflictError, ValidationError
from agentsphere.common.uuid7 import uuid7


class CreateTenantUseCase:
    def __init__(
        self,
        db: Any,
        tenant_repo_factory: Callable[..., TenantRepositoryProtocol],
    ) -> None:
        self._db = db
        self._tenant_repo_factory = tenant_repo_factory

    async def execute(self, name: str, slug: str) -> dict[str, Any]:
        if not name or not name.strip():
            raise ValidationError("Tenant name is required")
        if not slug or not slug.strip():
            raise ValidationError("Tenant slug is required")

        async with await self._db.get_session() as session:
            tenant_repo = self._tenant_repo_factory(session=session)
            existing = await tenant_repo.get_by_slug(slug.strip().lower())
            if existing:
                raise ConflictError(f"Tenant with slug '{slug}' already exists")

            tenant_id = uuid7()
            await tenant_repo.create(
                id=tenant_id,
                name=name.strip(),
                slug=slug.strip().lower(),
            )

        return {
            "id": str(tenant_id),
            "name": name.strip(),
            "slug": slug.strip().lower(),
        }
