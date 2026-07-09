import pytest

from agentsphere.ai.exceptions.base import PromptValidationError
from agentsphere.runtime.planner.planner import RuntimePlanner
from agentsphere.runtime.schemas.runtime import AgentDefinition, ExecutionGraph, WorkflowDefinition


@pytest.fixture
def planner() -> RuntimePlanner:
    return RuntimePlanner()


@pytest.fixture
def agent_def() -> AgentDefinition:
    # Set up basic agent with at least 2 allowed tools to trigger multi-node DAG compilation
    wf = WorkflowDefinition(
        workflow_id="wf1",
        name="Test Workflow",
        description="A test workflow DAG context",
        entry_node="step_1",
        allowed_tools=["calculator", "search_web"],
    )
    return AgentDefinition(
        agent_id="agent_123",
        name="Test Agent",
        description="A test agent definition",
        prompt_ref="agent_welcome",
        allowed_tools=["calculator", "search_web"],
        workflows={"wf1": wf},
    )


@pytest.mark.asyncio
async def test_planner_constructs_valid_dag(planner: RuntimePlanner, agent_def: AgentDefinition) -> None:
    graph = await planner.create_plan(
        goal="Calculate the sum of 5 and 5 and search it on web",
        agent_def=agent_def,
        workflow_id="wf1",
    )
    assert isinstance(graph, ExecutionGraph)
    assert len(graph.nodes) == 3
    assert len(graph.edges) == 2

    # Verify standard topological sequence
    assert "step_1" in graph.nodes
    assert "step_2" in graph.nodes
    assert "step_3" in graph.nodes

    # No loop errors raised
    planner.validate_dag(graph)


def test_circular_dependency_check_raises_error(planner: RuntimePlanner) -> None:
    # Setup cyclic graph manually
    from agentsphere.runtime.schemas.runtime import ExecutionNode

    n1 = ExecutionNode(step_id="step_1", action="t1")
    n2 = ExecutionNode(step_id="step_2", action="t2", depends_on=["step_1"])
    # Circular reference: step_1 depends on step_2
    n1.depends_on.append("step_2")

    nodes = {"step_1": n1, "step_2": n2}
    edges = [("step_1", "step_2"), ("step_2", "step_1")]

    graph = ExecutionGraph(graph_id="plan_cyclic", nodes=nodes, edges=edges)

    with pytest.raises(PromptValidationError) as exc:
        planner.validate_dag(graph)
    assert "Circular edge loop detected" in str(exc.value)
