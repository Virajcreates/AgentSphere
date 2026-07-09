import time
from collections.abc import AsyncIterator
from typing import Any

from agentsphere.ai.schemas.inference import LLMStreamChunk


class AIStream:
    """Standardized async stream wrapper for AI responses."""

    def __init__(
        self,
        stream_generator: AsyncIterator[LLMStreamChunk],
        provider: str,
        model: str,
        on_complete: Any | None = None,
    ) -> None:
        self._generator = stream_generator
        self.provider = provider
        self.model = model
        self._on_complete = on_complete
        self.start_time = time.perf_counter()
        self.accumulated_text = ""
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_cost = 0.0

    async def __aiter__(self) -> AsyncIterator[LLMStreamChunk]:
        try:
            async for chunk in self._generator:
                self.accumulated_text += chunk.delta
                if chunk.usage:
                    self.prompt_tokens = chunk.usage.prompt_tokens
                    self.completion_tokens = chunk.usage.completion_tokens
                    self.total_cost = chunk.usage.cost
                yield chunk
        finally:
            # When the stream is completed or aborted, trigger on_complete callback
            duration = time.perf_counter() - self.start_time
            if self._on_complete:
                from contextlib import suppress

                with suppress(Exception):
                    await self._on_complete(
                        provider=self.provider,
                        model=self.model,
                        latency=duration,
                        prompt_tokens=self.prompt_tokens,
                        completion_tokens=self.completion_tokens,
                        text=self.accumulated_text,
                        cost=self.total_cost,
                    )
