import pytest

from agentsphere.ai.executor.executor import MockExecutor
from agentsphere.ai.memory.memory import MockConversationMemory, MockMemoryStore
from agentsphere.ai.planner.planner import MockPlanner
from agentsphere.ai.schemas.inference import PromptMessage
from agentsphere.ai.schemas.planning import ExecutionPlan, PlanStep


@pytest.mark.asyncio
async def test_mock_planner() -> None:
    planner = MockPlanner()
    plan = await planner.create_plan("test goal", {"key": "val"})
    assert isinstance(plan, ExecutionPlan)
    assert plan.plan_id == "mock_plan_123"
    assert len(plan.steps) == 3
    assert plan.steps[0].action == "extract_intent"


@pytest.mark.asyncio
async def test_mock_executor() -> None:
    executor = MockExecutor()
    plan = ExecutionPlan(
        plan_id="p1",
        steps=[PlanStep(step_id="s1", action="action_1")],
    )
    res = await executor.execute_plan(plan, {})
    assert res.success is True
    assert len(res.results) == 1
    assert res.results[0].tool_name == "action_1"


@pytest.mark.asyncio
async def test_mock_memory_store() -> None:
    store = MockMemoryStore()
    assert await store.get("key") is None

    await store.set("key", "value")
    assert await store.get("key") == "value"

    await store.delete("key")
    assert await store.get("key") is None


@pytest.mark.asyncio
async def test_mock_conversation_memory() -> None:
    mem = MockConversationMemory()
    conv_id = "c1"
    assert await mem.get_messages(conv_id) == []

    msg = PromptMessage(role="user", content="hello")
    await mem.add_message(conv_id, msg)
    messages = await mem.get_messages(conv_id)
    assert len(messages) == 1
    assert messages[0].content == "hello"

    facts = await mem.extract_and_store_facts(conv_id)
    assert len(facts) > 0

    await mem.clear(conv_id)
    assert await mem.get_messages(conv_id) == []
