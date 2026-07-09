import asyncio
from typing import Any, Protocol

from agentsphere.application.ports.event_bus import EventBus


class WorkingMemory(Protocol):
    async def get(self, key: str) -> Any: ...

    async def set(self, key: str, value: Any) -> None: ...

    async def clear(self) -> None: ...

    async def get_all(self) -> dict[str, Any]: ...


class ConversationMemory(Protocol):
    async def get_messages(self) -> list[dict[str, Any]]: ...

    async def add_message(self, role: str, content: str) -> None: ...

    async def clear(self) -> None: ...


class ExecutionMemory(Protocol):
    async def log_step(self, step_id: str, summary: dict[str, Any]) -> None: ...

    async def get_steps(self) -> list[dict[str, Any]]: ...


class InMemoryWorkingMemory(WorkingMemory):
    def __init__(self, execution_id: str, event_bus: EventBus) -> None:
        self.execution_id = execution_id
        self._event_bus = event_bus
        self._store: dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any:
        async with self._lock:
            return self._store.get(key)

    async def set(self, key: str, value: Any) -> None:
        async with self._lock:
            self._store[key] = value

        # Dispatch memory updated events
        from agentsphere.runtime.events.events import MemoryUpdated

        await self._event_bus.publish(
            MemoryUpdated(
                execution_id=self.execution_id,
                memory_type="Working",
                key=key,
                value=value,
            )
        )

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()

    async def get_all(self) -> dict[str, Any]:
        async with self._lock:
            return dict(self._store)


class InMemoryConversationMemory(ConversationMemory):
    def __init__(self, execution_id: str, event_bus: EventBus) -> None:
        self.execution_id = execution_id
        self._event_bus = event_bus
        self._messages: list[dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def get_messages(self) -> list[dict[str, Any]]:
        async with self._lock:
            return list(self._messages)

    async def add_message(self, role: str, content: str) -> None:
        msg = {"role": role, "content": content}
        async with self._lock:
            self._messages.append(msg)

        from agentsphere.runtime.events.events import MemoryUpdated

        await self._event_bus.publish(
            MemoryUpdated(
                execution_id=self.execution_id,
                memory_type="Conversation",
                key=f"message_{len(self._messages)-1}",
                value=msg,
            )
        )

    async def clear(self) -> None:
        async with self._lock:
            self._messages.clear()


class InMemoryExecutionMemory(ExecutionMemory):
    def __init__(self, execution_id: str, event_bus: EventBus) -> None:
        self.execution_id = execution_id
        self._event_bus = event_bus
        self._steps: list[dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def log_step(self, step_id: str, summary: dict[str, Any]) -> None:
        entry = {"step_id": step_id, "summary": summary}
        async with self._lock:
            self._steps.append(entry)

        from agentsphere.runtime.events.events import MemoryUpdated

        await self._event_bus.publish(
            MemoryUpdated(
                execution_id=self.execution_id,
                memory_type="Execution",
                key=f"step_{step_id}",
                value=summary,
            )
        )

    async def get_steps(self) -> list[dict[str, Any]]:
        async with self._lock:
            return list(self._steps)


class MemoryManager:
    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        # Map execution_id -> dictionary of working, conversation, and execution memory stores
        self._working_stores: dict[str, InMemoryWorkingMemory] = {}
        self._conv_stores: dict[str, InMemoryConversationMemory] = {}
        self._exec_stores: dict[str, InMemoryExecutionMemory] = {}
        self._lock = asyncio.Lock()

    async def get_working_memory(self, execution_id: str) -> WorkingMemory:
        async with self._lock:
            if execution_id not in self._working_stores:
                self._working_stores[execution_id] = InMemoryWorkingMemory(
                    execution_id, self._event_bus
                )
            return self._working_stores[execution_id]

    async def get_conversation_memory(self, execution_id: str) -> ConversationMemory:
        async with self._lock:
            if execution_id not in self._conv_stores:
                self._conv_stores[execution_id] = InMemoryConversationMemory(
                    execution_id, self._event_bus
                )
            return self._conv_stores[execution_id]

    async def get_execution_memory(self, execution_id: str) -> ExecutionMemory:
        async with self._lock:
            if execution_id not in self._exec_stores:
                self._exec_stores[execution_id] = InMemoryExecutionMemory(
                    execution_id, self._event_bus
                )
            return self._exec_stores[execution_id]

    async def cleanup(self, execution_id: str) -> None:
        async with self._lock:
            self._working_stores.pop(execution_id, None)
            self._conv_stores.pop(execution_id, None)
            self._exec_stores.pop(execution_id, None)
