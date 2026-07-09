import pytest

from agentsphere.runtime.checkpoint.in_memory_store import InMemoryCheckpointStore
from agentsphere.runtime.conversation.conversation_manager import ConversationManager
from agentsphere.runtime.exceptions.base import (
    ExecutionTimeoutError,
    WorkflowCancellationError,
    WorkflowRecoveryError,
)
from agentsphere.runtime.telemetry.tracker import RuntimeTracker


@pytest.mark.asyncio
async def test_checkpoint_store_load_save_delete() -> None:
    store = InMemoryCheckpointStore()
    checkpoint_id = "cp_123"

    assert await store.load(checkpoint_id) is None

    # Save
    data = {"state": "active", "variables": {"x": 10}}
    await store.save(checkpoint_id, data)

    # Load
    loaded = await store.load(checkpoint_id)
    assert loaded is not None
    assert loaded["state"] == "active"

    # Delete
    await store.delete(checkpoint_id)
    assert await store.load(checkpoint_id) is None


@pytest.mark.asyncio
async def test_exceptions_rendering_and_details() -> None:
    # Coverage for exceptions base formatting
    err1 = WorkflowCancellationError("exec_123")
    assert "was cancelled" in str(err1)

    err2 = ExecutionTimeoutError("exec_123", elapsed=5.5, cap=4.0)
    assert "timed out" in str(err2)

    err3 = WorkflowRecoveryError("step_1", "skip", "error detail")
    assert "Recovery strategy 'skip' failed" in str(err3)


@pytest.mark.asyncio
async def test_conversation_manager_metadata_update() -> None:
    from agentsphere.infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus

    event_bus = InMemoryEventBus()
    conv_manager = ConversationManager(event_bus=event_bus)

    conv = await conv_manager.create_conversation(tenant_id="t1", metadata={"key1": "val1"})
    cid = conv["conversation_id"]

    # Update metadata properties
    await conv_manager.update_metadata(cid, {"key2": "val2", "key1": "new_val1"})
    updated = await conv_manager.get_conversation(cid)
    assert updated is not None
    assert updated["metadata"]["key1"] == "new_val1"
    assert updated["metadata"]["key2"] == "val2"


def test_telemetry_tracker_standalone() -> None:
    # Telemetry tracker standalone coverage
    tracker = RuntimeTracker()
    tracker.track_planning(0.1)
    tracker.track_execution(0.5, success=True)
    tracker.track_tool("calculator", 0.05)
    tracker.track_memory_op("read")
    tracker.track_retry()
    tracker.track_cancellation()
