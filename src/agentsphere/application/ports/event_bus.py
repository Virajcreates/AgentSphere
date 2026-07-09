from collections.abc import Callable, Coroutine
from typing import Any, Protocol


class EventBus(Protocol):
    async def publish(self, event: Any) -> None:
        """Asynchronously publishes an event to all subscribed listeners."""
        ...

    async def subscribe(
        self, event_type: type[Any], listener: Callable[[Any], Coroutine[Any, Any, None]]
    ) -> None:
        """Subscribes a listener to a specific event type."""
        ...

    async def unsubscribe(
        self, event_type: type[Any], listener: Callable[[Any], Coroutine[Any, Any, None]]
    ) -> None:
        """Unsubscribes a listener from a specific event type."""
        ...
