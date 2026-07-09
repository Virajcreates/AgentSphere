import time
from typing import Any, Protocol

import structlog

from agentsphere.application.ports.event_bus import EventBus
from agentsphere.runtime.exceptions.base import ToolValidationError
from agentsphere.runtime.schemas.runtime import RuntimeContext, ToolDefinition, ToolInvocation

logger = structlog.get_logger(__name__)


class ToolResult(Protocol):
    @property
    def success(self) -> bool: ...

    @property
    def data(self) -> dict[str, Any]: ...

    @property
    def error_message(self) -> str | None: ...


class SimpleToolResult:
    def __init__(self, success: bool, data: dict[str, Any], error_message: str | None = None) -> None:
        self._success = success
        self._data = data
        self._error_message = error_message

    @property
    def success(self) -> bool:
        return self._success

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    @property
    def error_message(self) -> str | None:
        return self._error_message


class Tool(Protocol):
    @property
    def definition(self) -> ToolDefinition: ...

    async def execute(self, arguments: dict[str, Any], context: RuntimeContext) -> ToolResult: ...


class ToolRegistry:
    def __init__(self) -> None:
        # Maps tool_name (str) -> Tool object
        self._tools: dict[str, Tool] = {}
        self._seed_mock_tools()

    def register_tool(self, tool: Tool) -> None:
        name = tool.definition.name.lower()
        self._tools[name] = tool

    def get_tool(self, name: str) -> Tool:
        tname = name.lower()
        if tname not in self._tools:
            raise ToolValidationError(name, f"Tool '{name}' not found in registry")
        return self._tools[tname]

    def list_tools(self) -> list[ToolDefinition]:
        return [t.definition for t in self._tools.values()]

    def _seed_mock_tools(self) -> None:
        # Register a basic mock calculator tool and a web search tool
        class CalculatorTool(Tool):
            @property
            def definition(self) -> ToolDefinition:
                return ToolDefinition(
                    name="calculator",
                    description="Performs simple math formulas on numbers.",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "expr": {"type": "string", "description": "Math expression, e.g. '2+2'"}
                        },
                        "required": ["expr"],
                    },
                )

            async def execute(self, arguments: dict[str, Any], context: RuntimeContext) -> ToolResult:
                expr = arguments.get("expr", "")
                if not expr:
                    return SimpleToolResult(False, {}, "Math expression expression is required")
                try:
                    # simplistic safe evaluator
                    cleaned = expr.replace(" ", "")
                    if not all(c in "0123456789+-*/()." for c in cleaned):
                        raise ValueError("Unsafe characters detected")
                    val = eval(cleaned, {"__builtins__": None}, {})  # nosec B307 eval is safe here
                    return SimpleToolResult(True, {"result": float(val)})
                except Exception as e:
                    return SimpleToolResult(False, {}, f"Calculation failed: {e!s}")

        class SearchTool(Tool):
            @property
            def definition(self) -> ToolDefinition:
                return ToolDefinition(
                    name="search_web",
                    description="Queries web documents for search matches.",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search keyword query"}
                        },
                        "required": ["query"],
                    },
                )

            async def execute(self, arguments: dict[str, Any], context: RuntimeContext) -> ToolResult:
                q = arguments.get("query", "")
                return SimpleToolResult(
                    True,
                    {
                        "query": q,
                        "results": [
                            {"title": "AgentSphere Platform documentation", "snippet": f"Found results for {q}"}
                        ],
                    },
                )

        self.register_tool(CalculatorTool())
        self.register_tool(SearchTool())


class ToolExecutor:
    def __init__(self, registry: ToolRegistry, event_bus: EventBus) -> None:
        self._registry = registry
        self._event_bus = event_bus

    async def invoke(self, invocation: ToolInvocation, context: RuntimeContext) -> dict[str, Any]:
        """Validates the input parameters, executes the target tool, and dispatches dynamic execution

        events onto our EventBus.
        """
        tool = self._registry.get_tool(invocation.tool_name)
        definition = tool.definition

        # 1. Parameter Validation against JSON Schema definitions
        # Verify required parameters exist
        required_fields = definition.input_schema.get("required", [])
        for field in required_fields:
            if field not in invocation.arguments:
                raise ToolValidationError(
                    definition.name, f"Missing required parameter '{field}' under input_schema"
                )

        # 2. Execute target tool and measure operational latency
        start_time = time.perf_counter()
        success = False
        result_data: dict[str, Any] = {}
        error_msg = None

        try:
            res = await tool.execute(invocation.arguments, context)
            success = res.success
            result_data = res.data
            error_msg = res.error_message
        except Exception as e:
            error_msg = str(e)
            logger.error("Exception during tool execution", tool_name=definition.name, error=error_msg)

        latency = time.perf_counter() - start_time

        # 3. Publish ToolExecuted domain events
        from datetime import datetime

        from agentsphere.runtime.events.events import ToolExecuted

        event = ToolExecuted(
            execution_id=context.execution_id,
            tool_name=definition.name,
            arguments=invocation.arguments,
            success=success,
            result=result_data if success else {"error": error_msg},
            latency=latency,
            timestamp=datetime.now(),
        )
        await self._event_bus.publish(event)

        if not success:
            raise ToolValidationError(
                definition.name, f"Tool execution failed: {error_msg or 'Unknown error'}"
            )

        return result_data
