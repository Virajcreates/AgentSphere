from typing import Any

from agentsphere.ai.interfaces.planner import Planner
from agentsphere.ai.schemas.planning import ExecutionPlan, PlanStep


class MockPlanner(Planner):
    async def create_plan(self, goal: str, context: dict[str, Any]) -> ExecutionPlan:
        # Generates a standard mock execution plan based on the goal
        steps = [
            PlanStep(
                step_id="step_1",
                action="extract_intent",
                input_data={"goal": goal, "context_keys": list(context.keys())},
            ),
            PlanStep(
                step_id="step_2",
                action="retrieve_context",
                input_data={"queries": [goal]},
                depends_on=["step_1"],
            ),
            PlanStep(
                step_id="step_3",
                action="generate_response",
                input_data={"style": "helpful"},
                depends_on=["step_2"],
            ),
        ]
        return ExecutionPlan(plan_id="mock_plan_123", steps=steps, status="planned")
