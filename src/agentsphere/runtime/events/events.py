from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ConversationStarted:
    conversation_id: str
    tenant_id: str | None
    participants: list[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ConversationCompleted:
    conversation_id: str
    tenant_id: str | None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ExecutionStarted:
    execution_id: str
    workflow_id: str | None
    goal: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ExecutionCompleted:
    execution_id: str
    workflow_id: str | None
    output_data: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ExecutionFailed:
    execution_id: str
    workflow_id: str | None
    error_message: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ToolExecuted:
    execution_id: str
    tool_name: str
    arguments: dict[str, Any]
    success: bool
    result: Any
    latency: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class MemoryUpdated:
    execution_id: str
    memory_type: str  # Working, Conversation, Execution
    key: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ExecutionStateChangedEvent:
    execution_id: str
    workflow_id: str | None
    from_state: str | None
    to_state: str
    reason: str | None
    timestamp: datetime = field(default_factory=datetime.now)
