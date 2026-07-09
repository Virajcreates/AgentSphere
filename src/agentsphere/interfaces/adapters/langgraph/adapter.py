from typing import Any

import structlog

from agentsphere.interfaces.adapters.langgraph.nodes import LangGraphNodes
from agentsphere.runtime.schemas.runtime import RuntimeContext

logger = structlog.get_logger(__name__)


class LangGraphAdapter:
    def __init__(self, nodes: LangGraphNodes) -> None:
        self._nodes = nodes

    async def run_workflow(
        self,
        goal: str,
        context: RuntimeContext,
        initial_variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Orchestrates an agent state-reconstitution pipeline, traversing standard LangGraph nodes

        sequentially while adhering to the core tracking rules of AgentRuntime.
        """
        logger.info("Executing LangGraph Reconstitution Pipeline", execution_id=context.execution_id)

        # 1. Initialize State variables Map
        state: dict[str, Any] = dict(initial_variables or {})
        state["prompt"] = goal

        # 2. Sequential traversal fallback through LangGraph Node adapters
        # Node A: Retrieval Node (Gather matching document contexts if requested)
        if "knowledge_base_id" in state:
            retrieval_state = await self._nodes.retrieval_node(state, context)
            state.update(retrieval_state)

        # Node B: LLM Node (Compile prompts and generate responses)
        llm_state = await self._nodes.llm_node(state, context)
        state.update(llm_state)

        # Node C: Tool Node (Execute APIs / calculations if needed)
        if "tool_name" in state:
            tool_state = await self._nodes.tool_node(state, context)
            state.update(tool_state)

        # Node D: Memory Node (Save working states)
        memory_state = await self._nodes.memory_node(state, context)
        state.update(memory_state)

        logger.info("LangGraph Pipeline Execution Completed", execution_id=context.execution_id)

        # Return standardized output payload
        return {
            "output_text": state.get("content", "Simulated output"),
            "retrieved_context": state.get("retrieved_context", {}),
            "tool_outputs": state.get("tool_outputs", {}),
            "state_snapshot": state,
        }
