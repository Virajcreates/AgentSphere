import asyncio
import random
from collections.abc import Callable, Coroutine
from typing import Any


class RetryPolicy:
    def __init__(
        self, max_retries: int = 3, base_delay: float = 0.5, max_delay: float = 5.0
    ) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def get_delay(self, attempt: int) -> float:
        # Exponential backoff with full jitter
        temp = self.base_delay * (2**attempt)
        temp = min(self.max_delay, temp)
        return random.uniform(0, temp)

    async def execute(
        self,
        func: Callable[[], Coroutine[Any, Any, Any]],
        on_retry: Callable[[Exception, int, float], Coroutine[Any, Any, None]] | None = None,
    ) -> Any:
        attempt = 0
        while True:
            try:
                return await func()
            except Exception as e:
                # Check if exception is transient and retry is permitted
                from agentsphere.ai.exceptions.base import (
                    ProviderConnectionError,
                    ProviderError,
                    ProviderTimeoutError,
                )

                is_transient = isinstance(
                    e, (ProviderConnectionError, ProviderTimeoutError)
                ) or (
                    isinstance(e, ProviderError)
                    and e.status in (429, 500, 502, 503, 504)
                )

                if not is_transient or attempt >= self.max_retries:
                    raise e

                delay = self.get_delay(attempt)
                if on_retry:
                    await on_retry(e, attempt, delay)

                await asyncio.sleep(delay)
                attempt += 1
