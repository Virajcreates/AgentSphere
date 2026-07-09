import json
from typing import Any

from agentsphere.runtime.schemas.runtime import ExecutionGraph, RuntimeContext


class RuntimeSerializer:
    def serialize_runtime(
        self, state: str, context: RuntimeContext, graph: ExecutionGraph, memory: dict[str, Any]
    ) -> str:
        """Statelessly compiles execution components into a standardized JSON string payload."""
        payload = {
            "state": state,
            "context": context.model_dump(),
            "graph": graph.model_dump(),
            "memory": memory,
        }
        return json.dumps(payload, sort_keys=True)

    def deserialize_runtime(self, payload_str: str) -> dict[str, Any]:
        """Parses the string JSON payload, re-constituting Pydantic models for execution context and graphs."""
        data = json.loads(payload_str)

        # Re-build Pydantic context model
        context_data = data.get("context", {})
        context = RuntimeContext(**context_data)

        # Re-build Pydantic graph model
        graph_data = data.get("graph", {})
        graph = ExecutionGraph(**graph_data)

        return {
            "state": data.get("state", "Created"),
            "context": context,
            "graph": graph,
            "memory": data.get("memory", {}),
        }
