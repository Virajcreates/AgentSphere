from typing import Any, Protocol

from agentsphere.ai.schemas.planning import ExecutionPlan


class Planner(Protocol):
    async def create_plan(self, goal: str, context: dict[str, Any]) -> ExecutionPlan: ...
