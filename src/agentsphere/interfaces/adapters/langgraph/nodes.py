from typing import Any

from agentsphere.ai.core.inference import AIInferenceService
from agentsphere.application.services.retriever_service import RetrieverService
from agentsphere.runtime.memory.memory_manager import MemoryManager
from agentsphere.runtime.schemas.runtime import RuntimeContext
from agentsphere.runtime.tools.tool_framework import ToolExecutor, ToolInvocation


class LangGraphNodes:
    """Core state nodes conforming to LangGraph execution mapping design, integrated to run safely under

    the execution boundaries of AgentRuntime.
    """

    def __init__(
        self,
        inference_service: AIInferenceService,
        retriever_service: RetrieverService,
        tool_executor: ToolExecutor,
        memory_manager: MemoryManager,
    ) -> None:
        self.inference = inference_service
        self.retriever = retriever_service
        self.tool_executor = tool_executor
        self.memory = memory_manager

    async def llm_node(self, state: dict[str, Any], context: RuntimeContext) -> dict[str, Any]:
        """Runs prompt compilation, dynamic whitelisting checks, and LLM inference generation."""
        prompt = state.get("prompt", "Analyze inputs")
        model = state.get("model", "gpt-4o-mini")

        # Invoke central platform inference service
        res = await self.inference.execute(
            prompt_name="agent_welcome",
            prompt_variables={"query": prompt},
            model=model,
            tenant_id=context.tenant_id,
        )

        return {"llm_output": res.content, "last_actor": "llm"}

    async def retrieval_node(self, state: dict[str, Any], context: RuntimeContext) -> dict[str, Any]:
        """Executes a similarity search across RAG Knowledge Bases, returning relevant context."""
        kb_id = state.get("knowledge_base_id")
        query = state.get("query", "")

        if not kb_id:
            return {"retrieved_context": "", "error": "Missing knowledge_base_id"}

        # Invoke central platform Retriever service
        chunks = await self.retriever.retrieve(
            knowledge_base_id=kb_id,
            query=query,
            limit=3,
        )

        context_text = "\n\n".join([c["text_content"] for c in chunks])
        return {"retrieved_context": context_text, "last_actor": "retriever"}

    async def tool_node(self, state: dict[str, Any], context: RuntimeContext) -> dict[str, Any]:
        """Invokes a whitelisted platform tool call, validating inputs against its definition."""
        tool_name = state.get("tool_name", "")
        tool_args = state.get("tool_args", {})

        if not tool_name:
            return {"tool_output": "", "error": "Missing tool_name"}

        invocation = ToolInvocation(tool_name=tool_name, arguments=tool_args, caller="LangGraphAdapter")
        res = await self.tool_executor.invoke(invocation, context)
        return {"tool_output": res, "last_actor": "tool_executor"}

    async def memory_node(self, state: dict[str, Any], context: RuntimeContext) -> dict[str, Any]:
        """Persists short-term variable results into isolated working memories contexts."""
        working_mem = await self.memory.get_working_memory(context.execution_id)

        for k, v in state.items():
            if k not in ("prompt", "model", "query", "knowledge_base_id", "tool_name", "tool_args"):
                await working_mem.set(k, v)

        return {"memory_saved": True, "last_actor": "memory"}
