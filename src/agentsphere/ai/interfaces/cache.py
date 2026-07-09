from typing import Protocol

from agentsphere.ai.schemas.inference import LLMCompletionResponse


class AICache(Protocol):
    async def get(self, prompt: str, tenant_id: str | None = None) -> LLMCompletionResponse | None:
        """Looks up a cached response based on the prompt text and optionally the tenant."""
        ...

    async def set(
        self, prompt: str, response: LLMCompletionResponse, tenant_id: str | None = None
    ) -> None:
        """Saves a response to cache keyed by prompt and optional tenant context."""
        ...

    async def delete(self, prompt: str, tenant_id: str | None = None) -> None:
        """Removes a prompt cached record."""
        ...

    async def clear(self) -> None:
        """Flushes the entire cache."""
        ...
