import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

import structlog

from agentsphere.application.ports.event_bus import EventBus

logger = structlog.get_logger(__name__)


class InMemoryEventBus(EventBus):
    def __init__(self) -> None:
        # Map event class type to a list of async callbacks
        self._listeners: dict[type[Any], list[Callable[[Any], Coroutine[Any, Any, None]]]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(
        self, event_type: type[Any], listener: Callable[[Any], Coroutine[Any, Any, None]]
    ) -> None:
        async with self._lock:
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            if listener not in self._listeners[event_type]:
                self._listeners[event_type].append(listener)

    async def unsubscribe(
        self, event_type: type[Any], listener: Callable[[Any], Coroutine[Any, Any, None]]
    ) -> None:
        async with self._lock:
            if event_type in self._listeners and listener in self._listeners[event_type]:
                self._listeners[event_type].remove(listener)

    async def publish(self, event: Any) -> None:
        event_type = type(event)
        callbacks = []

        async with self._lock:
            if event_type in self._listeners:
                callbacks = list(self._listeners[event_type])

        if callbacks:
            logger.info(
                "Publishing Platform Event",
                event_type=event_type.__name__,
                listeners_count=len(callbacks),
            )
            # Execute all listener callbacks concurrently
            tasks = [cb(event) for cb in callbacks]
            await asyncio.gather(*tasks, return_exceptions=True)
