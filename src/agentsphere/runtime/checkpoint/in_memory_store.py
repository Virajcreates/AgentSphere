import asyncio
from typing import Any

from agentsphere.runtime.interfaces.checkpoint import CheckpointStore


class InMemoryCheckpointStore(CheckpointStore):
    def __init__(self) -> None:
        # Maps checkpoint_id (str) -> dict state payload
        self._store: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def save(self, checkpoint_id: str, data: dict[str, Any]) -> None:
        async with self._lock:
            # Shallow clone to ensure isolation of snapshots
            self._store[checkpoint_id] = dict(data)

    async def load(self, checkpoint_id: str) -> dict[str, Any] | None:
        async with self._lock:
            if checkpoint_id in self._store:
                return dict(self._store[checkpoint_id])
            return None

    async def delete(self, checkpoint_id: str) -> None:
        async with self._lock:
            if checkpoint_id in self._store:
                del self._store[checkpoint_id]
