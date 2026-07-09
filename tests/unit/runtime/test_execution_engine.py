import pytest

from agentsphere.infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus
from agentsphere.runtime.executor.execution_engine import ExecutionEngine
from agentsphere.runtime.schemas.runtime import (
    ExecutionGraph,
    ExecutionHistory,
    ExecutionNode,
    RecoveryPolicy,
    RuntimeContext,
)


@pytest.fixture
def engine() -> ExecutionEngine:
    event_bus = InMemoryEventBus()
    return ExecutionEngine(event_bus=event_bus)


@pytest.mark.asyncio
async def test_topologically_sorted_execution(engine: ExecutionEngine) -> None:
    # Setup standard 3 nodes DAG
    # step_3 depends on step_2 which depends on step_1
    nodes = {
        "step_3": ExecutionNode(step_id="step_3", action="action_3", depends_on=["step_2"]),
        "step_2": ExecutionNode(step_id="step_2", action="action_2", depends_on=["step_1"]),
        "step_1": ExecutionNode(step_id="step_1", action="action_1"),
    }
    edges = [("step_1", "step_2"), ("step_2", "step_3")]
    graph = ExecutionGraph(graph_id="g1", nodes=nodes, edges=edges)

    context = RuntimeContext(request_id="req1", execution_id="exec1")
    history = ExecutionHistory(execution_id="exec1")

    execution_order = []

    async def mock_executor_func(tool_name, arguments, context):
        return {}

    def mock_policy_verifier(node, context):
        execution_order.append(node.step_id)

    # Invoke execution
    outputs = await engine.execute_graph(
        graph=graph,
        context=context,
        history=history,
        tool_executor_func=mock_executor_func,
        policy_verifier_func=mock_policy_verifier,
    )

    # 1. Verify topological sorting order: step_1 -> step_2 -> step_3
    assert execution_order == ["step_1", "step_2", "step_3"]

    # 2. Verify history steps recorded
    assert len(history.steps_history) == 3
    assert history.steps_history[0]["step_id"] == "step_1"
    assert history.steps_history[0]["status"] == "success"


@pytest.mark.asyncio
async def test_execution_engine_recovery_skip_and_continue(engine: ExecutionEngine) -> None:
    # Set up failing nodes with RecoveryPolicy (skip and continue)
    nodes = {
        "step_1": ExecutionNode(
            step_id="step_1",
            action="tool:action_1",  # must be a tool action to trigger execution failure
            recovery_policy=RecoveryPolicy(strategy="skip"),
        ),
        "step_2": ExecutionNode(
            step_id="step_2",
            action="tool:action_2",  # must be a tool action to trigger execution failure
            depends_on=["step_1"],
            recovery_policy=RecoveryPolicy(strategy="continue"),
        ),
    }
    edges = [("step_1", "step_2")]
    graph = ExecutionGraph(graph_id="g_recovery", nodes=nodes, edges=edges)

    context = RuntimeContext(request_id="req1", execution_id="exec1")
    history = ExecutionHistory(execution_id="exec1")

    # This executor always raises error to force recovery triggers
    async def mock_failing_executor(tool_name, arguments, context):
        raise ValueError("Simulated network fail")

    outputs = await engine.execute_graph(
        graph=graph,
        context=context,
        history=history,
        tool_executor_func=mock_failing_executor,
        policy_verifier_func=None,
    )

    # Both steps should run and execute successfully inside engine sequence due to skip/continue recovery overrides!
    assert "step_1" in outputs
    assert "step_2" in outputs
    assert outputs["step_1"]["skipped"] is True


@pytest.mark.asyncio
async def test_execution_engine_recovery_rollback(engine: ExecutionEngine) -> None:
    from agentsphere.runtime.exceptions.base import WorkflowRecoveryError

    nodes = {
        "step_1": ExecutionNode(
            step_id="step_1",
            action="tool:action_1",  # must be a tool action to trigger execution failure
            recovery_policy=RecoveryPolicy(strategy="rollback"),
        ),
    }
    graph = ExecutionGraph(graph_id="g_rollback", nodes=nodes, edges=[])

    context = RuntimeContext(request_id="req1", execution_id="exec1")
    history = ExecutionHistory(execution_id="exec1")

    async def mock_failing_executor(tool_name, arguments, context):
        raise ValueError("Simulated network fail")

    # Rolls back on failure and throws recovery exception
    with pytest.raises(WorkflowRecoveryError) as exc:
        await engine.execute_graph(
            graph=graph,
            context=context,
            history=history,
            tool_executor_func=mock_failing_executor,
            policy_verifier_func=None,
        )
    assert "Rollback completed during step failure" in str(exc.value)


@pytest.mark.asyncio
async def test_execution_engine_recovery_retry(engine: ExecutionEngine) -> None:
    # Test step-level retries: first run fails, second run succeeds!
    call_count = 0

    async def mock_intermittent_executor(tool_name, arguments, context):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ValueError("First attempt fails")
        return {"status": "success"}

    nodes = {
        "step_1": ExecutionNode(
            step_id="step_1",
            action="tool:calculator",
            recovery_policy=RecoveryPolicy(strategy="retry", max_retries=2),
        ),
    }
    graph = ExecutionGraph(graph_id="g_retry", nodes=nodes, edges=[])

    context = RuntimeContext(request_id="req1", execution_id="exec1")
    history = ExecutionHistory(execution_id="exec1")

    outputs = await engine.execute_graph(
        graph=graph,
        context=context,
        history=history,
        tool_executor_func=mock_intermittent_executor,
        policy_verifier_func=None,
    )

    # Succeeded after intermittent retry!
    assert outputs["step_1"]["status"] == "success"
    assert call_count == 2
    assert history.steps_history[0]["attempts"] == 2


def test_argument_resolution_logic(engine: ExecutionEngine) -> None:
    raw_args = {
        "expr": "Calculations on {{ step_1.result }}",
        "exact": "{{ step_1.result }}",
        "nested": {"key": "value"},
    }
    step_outputs = {
        "step_1": {"result": "success_data"}
    }

    resolved = engine._resolve_arguments(raw_args, step_outputs)
    # Checks that composite substitution and exact placeholder matches both resolve correctly
    assert resolved["expr"] == "Calculations on success_data"
    assert resolved["exact"] == "success_data"
    assert resolved["nested"] == {"key": "value"}
