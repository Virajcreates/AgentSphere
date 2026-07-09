from collections.abc import Callable
from typing import Any
from uuid import UUID

from agentsphere.application.ports.repositories import ApiKeyRepositoryProtocol
from agentsphere.common.exceptions import NotFoundError


class RevokeApiKeyUseCase:
    def __init__(
        self,
        db: Any,
        api_key_repo_factory: Callable[..., ApiKeyRepositoryProtocol],
    ) -> None:
        self._db = db
        self._api_key_repo_factory = api_key_repo_factory

    async def execute(self, api_key_id: UUID, tenant_id: UUID) -> None:
        async with await self._db.get_session() as session:
            repo = self._api_key_repo_factory(session=session)
            api_key = await repo.get(api_key_id, tenant_id)
            if not api_key:
                raise NotFoundError("API key", api_key_id)
            await repo.delete(api_key_id, tenant_id)
