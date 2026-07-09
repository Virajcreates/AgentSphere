import pytest

from agentsphere.infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus
from agentsphere.runtime.conversation.conversation_manager import ConversationManager


@pytest.fixture
def manager() -> ConversationManager:
    event_bus = InMemoryEventBus()
    return ConversationManager(event_bus=event_bus)


@pytest.mark.asyncio
async def test_create_and_retrieve_conversation(manager: ConversationManager) -> None:
    conv = await manager.create_conversation(tenant_id="t1", metadata={"origin": "web"})
    assert conv["status"] == "active"
    assert conv["tenant_id"] == "t1"
    assert conv["metadata"]["origin"] == "web"

    # Retrieve
    cid = conv["conversation_id"]
    retrieved = await manager.get_conversation(cid)
    assert retrieved is not None
    assert retrieved["conversation_id"] == cid


@pytest.mark.asyncio
async def test_add_and_remove_participants(manager: ConversationManager) -> None:
    conv = await manager.create_conversation(tenant_id="t1")
    cid = conv["conversation_id"]

    await manager.add_participant(cid, "user_123")
    retrieved = await manager.get_conversation(cid)
    assert retrieved is not None
    assert "user_123" in retrieved["participants"]

    await manager.remove_participant(cid, "user_123")
    assert "user_123" not in retrieved["participants"]


@pytest.mark.asyncio
async def test_close_conversation(manager: ConversationManager) -> None:
    conv = await manager.create_conversation(tenant_id="t1")
    cid = conv["conversation_id"]

    await manager.close_conversation(cid)
    retrieved = await manager.get_conversation(cid)
    assert retrieved is not None
    assert retrieved["status"] == "closed"
    assert retrieved["closed_at"] is not None
