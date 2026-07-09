from collections.abc import Callable
from typing import Any
from uuid import UUID

from agentsphere.application.ports.repositories import ApiKeyRepositoryProtocol
from agentsphere.common.exceptions import ValidationError
from agentsphere.common.uuid7 import uuid7


class CreateApiKeyUseCase:
    def __init__(
        self,
        db: Any,
        api_key_repo_factory: Callable[..., ApiKeyRepositoryProtocol],
        api_key_handler: Any,
    ) -> None:
        self._db = db
        self._api_key_repo_factory = api_key_repo_factory
        self._api_key_handler = api_key_handler

    async def execute(
        self, tenant_id: UUID, name: str, scopes: list[str] | None = None
    ) -> dict[str, Any]:
        if not name or not name.strip():
            raise ValidationError("API key name is required")

        api_key_id = uuid7()
        raw_key, prefix, key_hash = self._api_key_handler.generate(tenant_id, api_key_id)

        async with await self._db.get_session() as session:
            repo = self._api_key_repo_factory(session=session)
            await repo.create(
                id=api_key_id,
                tenant_id=tenant_id,
                key_prefix=prefix,
                key_hash=key_hash,
                name=name.strip(),
                scopes=scopes or [],
            )

        return {
            "id": str(api_key_id),
            "name": name.strip(),
            "key": raw_key,
            "prefix": prefix,
            "scopes": scopes or [],
        }
