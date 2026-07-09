import pytest

from agentsphere.ai.prompts.prompt_manager import PromptManager
from agentsphere.interfaces.container import init_container
from agentsphere.runtime.agent.agent_runtime import AgentRuntime
from agentsphere.runtime.checkpoint.in_memory_store import InMemoryCheckpointStore
from agentsphere.runtime.schemas.runtime import (
    AgentDefinition,
    RuntimeRequest,
    RuntimeResponse,
    WorkflowDefinition,
)


@pytest.fixture
def agent_runtime() -> AgentRuntime:
    # Initialize container to register all runtime DI singletons
    container = init_container()
    return container.runtime.agent_runtime()


@pytest.fixture
def agent_def() -> AgentDefinition:
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
async def test_runtime_end_to_end_success(agent_runtime: AgentRuntime, agent_def: AgentDefinition) -> None:
    # Set up basic welcome prompt inside prompt manager to make rendering succeed
    ai_container = init_container().ai
    ai_container.prompt_manager().register_system_template(
        "default", "agent_welcome", "Goal Statement: {{ query }}"
    )

    request = RuntimeRequest(
        agent_id="agent_123",
        workflow_id="wf1",
        goal="Perform calculations on the query inputs",
        variables={"query": "Perform calculations"},
        tenant_id="tenant_abc",
    )

    hook_execution_log = []

    # Dynamic registry for Runtime Lifecycle Hooks to verify execution timing
    async def log_hook(payload) -> None:
        # captures the context keys or metadata
        hook_execution_log.append("hook_executed")

    agent_runtime.register_hook("BeforePlanning", log_hook)
    agent_runtime.register_hook("AfterPlanning", log_hook)
    agent_runtime.register_hook("BeforeExecution", log_hook)
    agent_runtime.register_hook("AfterExecution", log_hook)
    agent_runtime.register_hook("BeforeTool", log_hook)
    agent_runtime.register_hook("AfterTool", log_hook)
    agent_runtime.register_hook("BeforeResponse", log_hook)
    agent_runtime.register_hook("AfterResponse", log_hook)

    # 1. Execute runtime lifecycle
    response = await agent_runtime.execute(request, agent_def)

    assert isinstance(response, RuntimeResponse)
    assert response.state == "Completed"
    assert len(response.history.state_transitions) > 1

    # 2. Verify all 8 lifecycle hooks were triggered successfully
    # (Since there are 2 tools in the workflow, BeforeTool/AfterTool are called twice!)
    # Total hooks called: BeforePlanning(1) + AfterPlanning(1) + BeforeExecution(1) + BeforeTool(2) + AfterTool(2) + AfterExecution(1) + BeforeResponse(1) + AfterResponse(1) = 10 calls!
    assert len(hook_execution_log) == 10

    # 3. Verify Checkpoint saving was executed successfully
    exec_id = response.execution_id
    checkpoint = await agent_runtime.checkpoint_store.load(exec_id)
    assert checkpoint is not None
    assert "payload" in checkpoint

    # 4. Verify serializer deserialized matches original context
    serialized_payload = checkpoint["payload"]
    restored = agent_runtime.serializer.deserialize_runtime(serialized_payload)
    assert restored["state"] == "Completed"
    assert restored["context"].execution_id == exec_id
