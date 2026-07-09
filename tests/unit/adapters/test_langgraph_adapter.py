import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from agentsphere.ai.core.inference import AIInferenceService
from agentsphere.ai.schemas.inference import LLMCompletionResponse, TokenUsage
from agentsphere.application.services.retriever_service import RetrieverService
from agentsphere.interfaces.adapters.langgraph.adapter import LangGraphAdapter
from agentsphere.interfaces.adapters.langgraph.nodes import LangGraphNodes
from agentsphere.runtime.memory.memory_manager import MemoryManager, WorkingMemory
from agentsphere.runtime.schemas.runtime import RuntimeContext
from agentsphere.runtime.tools.tool_framework import ToolExecutor


@pytest.fixture
def mock_inference() -> AIInferenceService:
    service = MagicMock(spec=AIInferenceService)
    # mock execution res
    mock_res = LLMCompletionResponse(
        content="This is generated text by LLM Node.",
        model="gpt-4o-mini",
        provider="openai",
        usage=TokenUsage(),
        latency=0.2,
    )
    service.execute = AsyncMock(return_value=mock_res)
    return service


@pytest.fixture
def mock_retriever() -> RetrieverService:
    service = MagicMock(spec=RetrieverService)
    mock_chunks = [{"chunk_id": "c1", "text_content": "Extracted document block."}]
    service.retrieve = AsyncMock(return_value=mock_chunks)
    return service


@pytest.fixture
def mock_tool_executor() -> ToolExecutor:
    executor = MagicMock(spec=ToolExecutor)
    executor.invoke = AsyncMock(return_value={"result": "Successful tool execution"})
    return executor


@pytest.fixture
def mock_memory() -> MemoryManager:
    manager = MagicMock(spec=MemoryManager)
    working = MagicMock(spec=WorkingMemory)
    working.set = AsyncMock()
    manager.get_working_memory = AsyncMock(return_value=working)
    return manager


@pytest.mark.asyncio
async def test_langgraph_adapter_runs_nodes_pipeline(
    mock_inference: AIInferenceService,
    mock_retriever: RetrieverService,
    mock_tool_executor: ToolExecutor,
    mock_memory: MemoryManager,
) -> None:
    nodes = LangGraphNodes(
        inference_service=mock_inference,
        retriever_service=mock_retriever,
        tool_executor=mock_tool_executor,
        memory_manager=mock_memory,
    )
    adapter = LangGraphAdapter(nodes=nodes)

    context = RuntimeContext(
        request_id="req_123",
        execution_id="exec_123",
        tenant_id="tenant_123",
    )

    initial_variables = {
        "knowledge_base_id": uuid.uuid4(),
        "query": "Who is AgentSphere?",
        "tool_name": "calculator",
        "tool_args": {"expr": "2+2"},
        "custom_user_var": "save me",
    }

    # Execute workflow loop
    result = await adapter.run_workflow(
        goal="Traverse all LangGraph nodes",
        context=context,
        initial_variables=initial_variables,
    )

    assert result is not None
    assert "state_snapshot" in result
    snapshot = result["state_snapshot"]

    # 1. Verify retrieval node fetched chunk content
    assert snapshot["retrieved_context"] == "Extracted document block."
    mock_retriever.retrieve.assert_called_once()

    # 2. Verify LLM node generated content
    assert snapshot["llm_output"] == "This is generated text by LLM Node."
    mock_inference.execute.assert_called_once()

    # 3. Verify tool node executed calculators
    assert snapshot["tool_output"] == {"result": "Successful tool execution"}
    mock_tool_executor.invoke.assert_called_once()

    # 4. Verify memory node persisted variable
    mock_memory.get_working_memory.assert_called_once_with("exec_123")
