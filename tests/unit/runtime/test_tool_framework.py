import pytest

from agentsphere.infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus
from agentsphere.runtime.exceptions.base import ToolValidationError
from agentsphere.runtime.schemas.runtime import RuntimeContext, ToolInvocation
from agentsphere.runtime.tools.tool_framework import ToolExecutor, ToolRegistry


@pytest.fixture
def registry() -> ToolRegistry:
    return ToolRegistry()


@pytest.fixture
def executor(registry: ToolRegistry) -> ToolExecutor:
    event_bus = InMemoryEventBus()
    return ToolExecutor(registry=registry, event_bus=event_bus)


@pytest.mark.asyncio
async def test_tool_registry_seeding(registry: ToolRegistry) -> None:
    calculator = registry.get_tool("calculator")
    assert calculator.definition.name == "calculator"
    assert calculator.definition.version == "1.0.0"

    # Listing whitelisted tools
    tools = registry.list_tools()
    assert len(tools) >= 2


@pytest.mark.asyncio
async def test_tool_executor_success(executor: ToolExecutor) -> None:
    context = RuntimeContext(request_id="req1", execution_id="exec1")
    invocation = ToolInvocation(
        tool_name="calculator",
        arguments={"expr": "10 + 20"},
    )

    res = await executor.invoke(invocation, context)
    assert res["result"] == 30.0


@pytest.mark.asyncio
async def test_tool_executor_validation_fails(executor: ToolExecutor) -> None:
    context = RuntimeContext(request_id="req1", execution_id="exec1")
    # Calculator requires parameter 'expr' inside arguments
    invocation = ToolInvocation(
        tool_name="calculator",
        arguments={},
    )

    with pytest.raises(ToolValidationError) as exc:
        await executor.invoke(invocation, context)
    assert "Missing required parameter" in str(exc.value)


@pytest.mark.asyncio
async def test_calculator_tool_unsafe_rejection(registry: ToolRegistry) -> None:
    calc = registry.get_tool("calculator")
    context = RuntimeContext(request_id="req1", execution_id="exec1")

    # Pass unsafe string containing malicious variables
    res = await calc.execute({"expr": "import os; os.system('ls')"}, context)
    assert res.success is False
    assert "Unsafe characters detected" in res.error_message
