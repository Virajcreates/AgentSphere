from typing import Any, Literal

from pydantic import BaseModel, Field


class RuntimeContext(BaseModel):
    request_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    execution_id: str
    workflow_id: str | None = None
    plan_id: str | None = None
    step_id: str | None = None
    agent_id: str | None = None


class ToolDefinition(BaseModel):
    name: str
    version: str = "1.0.0"
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    timeout: float = 30.0
    permissions: list[str] = Field(default_factory=list)
    side_effects: bool = False
    idempotent: bool = True


class WorkflowDefinition(BaseModel):
    workflow_id: str
    name: str
    description: str
    entry_node: str
    execution_policy: dict[str, Any] = Field(default_factory=dict)
    memory_policy: dict[str, Any] = Field(default_factory=dict)
    allowed_tools: list[str] = Field(default_factory=list)


class AgentDefinition(BaseModel):
    agent_id: str
    name: str
    description: str
    prompt_ref: str
    allowed_providers: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    workflows: dict[str, WorkflowDefinition] = Field(default_factory=dict)
    memory_policy: dict[str, Any] = Field(default_factory=dict)
    execution_policy: dict[str, Any] = Field(default_factory=dict)


class RecoveryPolicy(BaseModel):
    strategy: Literal["retry", "skip", "cancel", "rollback", "continue"] = "retry"
    max_retries: int = 3
    backoff_factor: float = 1.5


class ToolInvocation(BaseModel):
    tool_name: str
    tool_version: str = "1.0.0"
    arguments: dict[str, Any] = Field(default_factory=dict)
    timeout: float | None = None
    retry_policy: RecoveryPolicy | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    caller: str | None = None


class ExecutionNode(BaseModel):
    step_id: str
    action: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)
    recovery_policy: RecoveryPolicy = Field(default_factory=RecoveryPolicy)


class ExecutionGraph(BaseModel):
    graph_id: str
    nodes: dict[str, ExecutionNode] = Field(default_factory=dict)
    edges: list[tuple[str, str]] = Field(default_factory=list)


class ExecutionHistory(BaseModel):
    execution_id: str
    workflow_id: str | None = None
    steps_history: list[dict[str, Any]] = Field(default_factory=list)
    state_transitions: list[dict[str, Any]] = Field(default_factory=list)


class RuntimeRequest(BaseModel):
    agent_id: str
    workflow_id: str | None = None
    goal: str
    variables: dict[str, Any] = Field(default_factory=dict)
    tenant_id: str | None = None


class RuntimeResponse(BaseModel):
    execution_id: str
    state: str
    history: ExecutionHistory
    output_data: dict[str, Any] = Field(default_factory=dict)
