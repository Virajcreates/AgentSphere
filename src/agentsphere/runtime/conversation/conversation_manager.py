import asyncio
from datetime import datetime
from typing import Any

from agentsphere.application.ports.event_bus import EventBus
from agentsphere.runtime.events.events import ConversationCompleted, ConversationStarted


class ConversationManager:
    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        # Map conversation_id (str) -> dict of properties
        self._conversations: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def create_conversation(
        self, tenant_id: str | None, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Creates and indexes a new active conversation, firing the ConversationStarted event."""
        import uuid

        conversation_id = str(uuid.uuid4())
        conv: dict[str, Any] = {
            "conversation_id": conversation_id,
            "tenant_id": tenant_id,
            "status": "active",
            "participants": [],
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "closed_at": None,
        }

        async with self._lock:
            self._conversations[conversation_id] = conv

        # Dispatch standard start event
        await self._event_bus.publish(
            ConversationStarted(
                conversation_id=conversation_id,
                tenant_id=tenant_id,
                participants=[],
                timestamp=datetime.now(),
            )
        )
        return conv

    async def get_conversation(self, conversation_id: str) -> dict[str, Any] | None:
        async with self._lock:
            return self._conversations.get(conversation_id)

    async def update_metadata(self, conversation_id: str, metadata: dict[str, Any]) -> None:
        async with self._lock:
            if conversation_id in self._conversations:
                self._conversations[conversation_id]["metadata"].update(metadata)

    async def add_participant(self, conversation_id: str, participant_id: str) -> None:
        async with self._lock:
            if conversation_id in self._conversations:
                participants = self._conversations[conversation_id]["participants"]
                if participant_id not in participants:
                    participants.append(participant_id)

    async def remove_participant(self, conversation_id: str, participant_id: str) -> None:
        async with self._lock:
            if conversation_id in self._conversations:
                participants = self._conversations[conversation_id]["participants"]
                if participant_id in participants:
                    participants.remove(participant_id)

    async def close_conversation(self, conversation_id: str) -> None:
        """Closes an active conversation context, updating metadata and firing completion events."""
        async with self._lock:
            if conversation_id in self._conversations:
                conv = self._conversations[conversation_id]
                if conv["status"] != "closed":
                    conv["status"] = "closed"
                    conv["closed_at"] = datetime.now().isoformat()

                    await self._event_bus.publish(
                        ConversationCompleted(
                            conversation_id=conversation_id,
                            tenant_id=conv.get("tenant_id"),
                            timestamp=datetime.now(),
                        )
                    )
