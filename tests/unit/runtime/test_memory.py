import pytest

from agentsphere.infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus
from agentsphere.runtime.memory.memory_manager import MemoryManager


@pytest.fixture
def manager() -> MemoryManager:
    event_bus = InMemoryEventBus()
    return MemoryManager(event_bus=event_bus)


@pytest.mark.asyncio
async def test_working_memory_operations(manager: MemoryManager) -> None:
    wm = await manager.get_working_memory("exec1")
    assert await wm.get("key") is None

    await wm.set("key", "val")
    assert await wm.get("key") == "val"

    all_vars = await wm.get_all()
    assert all_vars == {"key": "val"}

    await wm.clear()
    assert await wm.get("key") is None


@pytest.mark.asyncio
async def test_conversation_memory_operations(manager: MemoryManager) -> None:
    cm = await manager.get_conversation_memory("exec1")
    assert await cm.get_messages() == []

    await cm.add_message("user", "Hello agent")
    messages = await cm.get_messages()
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello agent"

    await cm.clear()
    assert await cm.get_messages() == []


@pytest.mark.asyncio
async def test_execution_memory_operations(manager: MemoryManager) -> None:
    em = await manager.get_execution_memory("exec1")
    assert await em.get_steps() == []

    await em.log_step("step_1", {"status": "success", "latency": 0.2})
    steps = await em.get_steps()
    assert len(steps) == 1
    assert steps[0]["step_id"] == "step_1"
    assert steps[0]["summary"]["status"] == "success"
