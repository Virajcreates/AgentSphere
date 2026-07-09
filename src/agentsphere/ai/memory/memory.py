from typing import Any

from agentsphere.ai.interfaces.memory import ConversationMemory, MemoryStore
from agentsphere.ai.schemas.inference import PromptMessage


class MockMemoryStore(MemoryStore):
    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    async def get(self, key: str) -> Any:
        return self._store.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        self._store[key] = value

    async def delete(self, key: str) -> None:
        if key in self._store:
            del self._store[key]


class MockConversationMemory(ConversationMemory):
    def __init__(self) -> None:
        self._conversations: dict[str, list[PromptMessage]] = {}

    async def get_messages(self, conversation_id: str) -> list[PromptMessage]:
        return self._conversations.get(conversation_id, [])

    async def add_message(self, conversation_id: str, message: PromptMessage) -> None:
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []
        self._conversations[conversation_id].append(message)

    async def clear(self, conversation_id: str) -> None:
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]

    async def extract_and_store_facts(self, conversation_id: str) -> list[str]:
        # Simple static mock facts
        return ["User is testing the mock memory implementation", "Platform name is AgentSphere"]
