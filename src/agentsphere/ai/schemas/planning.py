from typing import Any

from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    step_id: str
    action: str
    input_data: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)


class ExecutionPlan(BaseModel):
    plan_id: str
    steps: list[PlanStep] = Field(default_factory=list)
    status: str = "pending"


class ToolExecutionResult(BaseModel):
    tool_name: str
    success: bool
    output_data: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None


class ExecutionResult(BaseModel):
    plan_id: str
    success: bool
    results: list[ToolExecutionResult] = Field(default_factory=list)
    output_data: dict[str, Any] = Field(default_factory=dict)
