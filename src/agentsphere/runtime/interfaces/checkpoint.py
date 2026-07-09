from typing import Any, Protocol


class CheckpointStore(Protocol):
    async def save(self, checkpoint_id: str, data: dict[str, Any]) -> None:
        """Saves dynamic execution context state linked to a specific checkpoint_id."""
        ...

    async def load(self, checkpoint_id: str) -> dict[str, Any] | None:
        """Loads and returns state data for the given checkpoint_id, or None if not found."""
        ...

    async def delete(self, checkpoint_id: str) -> None:
        """Deletes checkpoint records matching the checkpoint_id."""
        ...
