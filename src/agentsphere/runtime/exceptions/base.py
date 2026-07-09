from agentsphere.ai.exceptions.base import AIError


class InvalidStateTransitionError(AIError):
    def __init__(self, from_state: str, to_state: str, instance: str = "") -> None:
        super().__init__(
            title="Invalid State Transition",
            status=400,
            detail=f"Cannot transition execution state from '{from_state}' to '{to_state}'",
            instance=instance,
        )


class PolicyLimitViolationError(AIError):
    def __init__(
        self, limit_name: str, allowed: int | float, actual: int | float, instance: str = ""
    ) -> None:
        super().__init__(
            title="Policy Limit Violation",
            status=403,
            detail=(
                f"Runtime policy limit breached: {limit_name} "
                f"(Allowed: {allowed}, Actual: {actual})"
            ),
            instance=instance,
        )


class ToolValidationError(AIError):
    def __init__(self, tool_name: str, detail: str, instance: str = "") -> None:
        super().__init__(
            title="Tool Validation Error",
            status=422,
            detail=f"Validation failed for tool '{tool_name}': {detail}",
            instance=instance,
        )


class WorkflowCancellationError(AIError):
    def __init__(self, execution_id: str, instance: str = "") -> None:
        super().__init__(
            title="Workflow Execution Cancelled",
            status=499,  # Client Closed Request equivalent
            detail=f"Execution '{execution_id}' was cancelled by system/client signal",
            instance=instance,
        )


class ExecutionTimeoutError(AIError):
    def __init__(
        self, execution_id: str, elapsed: float, cap: float, instance: str = ""
    ) -> None:
        super().__init__(
            title="Execution Timeout Error",
            status=408,  # Request Timeout
            detail=(
                f"Execution '{execution_id}' timed out after {elapsed:.1f}s "
                f"(Allowed cap: {cap:.1f}s)"
            ),
            instance=instance,
        )


class WorkflowRecoveryError(AIError):
    def __init__(
        self, step_id: str, strategy: str, detail: str, instance: str = ""
    ) -> None:
        super().__init__(
            title="Workflow Recovery Failed",
            status=500,
            detail=(
                f"Recovery strategy '{strategy}' failed for step '{step_id}': "
                f"{detail}"
            ),
            instance=instance,
        )
