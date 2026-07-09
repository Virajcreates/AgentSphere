from typing import Any, Protocol

from agentsphere.ai.schemas.planning import ExecutionPlan, ExecutionResult


class Executor(Protocol):
    async def execute_plan(
        self, plan: ExecutionPlan, context: dict[str, Any]
    ) -> ExecutionResult: ...
