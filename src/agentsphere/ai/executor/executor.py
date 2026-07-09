from typing import Any

from agentsphere.ai.interfaces.executor import Executor
from agentsphere.ai.schemas.planning import (
    ExecutionPlan,
    ExecutionResult,
    ToolExecutionResult,
)


class MockExecutor(Executor):
    async def execute_plan(
        self, plan: ExecutionPlan, context: dict[str, Any]
    ) -> ExecutionResult:
        results = []
        for step in plan.steps:
            results.append(
                ToolExecutionResult(
                    tool_name=step.action,
                    success=True,
                    output_data={"message": f"Successfully executed action '{step.action}'"},
                )
            )

        return ExecutionResult(
            plan_id=plan.plan_id,
            success=True,
            results=results,
            output_data={"summary": "All steps executed successfully in mock environment"},
        )
