
from agentsphere.runtime.exceptions.base import PolicyLimitViolationError
from agentsphere.runtime.schemas.runtime import ExecutionNode, RuntimeContext


class RuntimePolicyEvaluator:
    def __init__(self) -> None:
        self.max_execution_depth: int = 10
        self.max_retries_allowed: int = 5
        self.max_tools_allowed: int = 15
        self.max_execution_time_sec: float = 120.0

        # Dynamic usage counters: execution_id -> dictionary of metric tallies
        self._execution_depths: dict[str, int] = {}
        self._execution_tool_calls: dict[str, int] = {}

    def set_limits(
        self, depth: int, retries: int, tools: int, duration_sec: float
    ) -> None:
        self.max_execution_depth = depth
        self.max_retries_allowed = retries
        self.max_tools_allowed = tools
        self.max_execution_time_sec = duration_sec

    def verify_step_policy(self, node: ExecutionNode, context: RuntimeContext) -> None:
        """Verifies step-level bounds (consecutive retries, overall depth, and tool whitelist limits)

        before allowing execution.
        """
        exec_id = context.execution_id

        # 1. Evaluate depth count
        if exec_id not in self._execution_depths:
            self._execution_depths[exec_id] = 0
        self._execution_depths[exec_id] += 1

        if self._execution_depths[exec_id] > self.max_execution_depth:
            raise PolicyLimitViolationError(
                limit_name="max_execution_depth",
                allowed=self.max_execution_depth,
                actual=self._execution_depths[exec_id],
            )

        # 2. Evaluate tool call constraints
        if node.action.startswith("tool:"):
            if exec_id not in self._execution_tool_calls:
                self._execution_tool_calls[exec_id] = 0
            self._execution_tool_calls[exec_id] += 1

            if self._execution_tool_calls[exec_id] > self.max_tools_allowed:
                raise PolicyLimitViolationError(
                    limit_name="max_tools_allowed",
                    allowed=self.max_tools_allowed,
                    actual=self._execution_tool_calls[exec_id],
                )

        # 3. Verify step-level retries boundaries of RecoveryPolicy
        policy = node.recovery_policy
        if policy.strategy == "retry" and policy.max_retries > self.max_retries_allowed:
            raise PolicyLimitViolationError(
                limit_name="max_step_retries",
                allowed=self.max_retries_allowed,
                actual=policy.max_retries,
            )

    def cleanup(self, execution_id: str) -> None:
        self._execution_depths.pop(execution_id, None)
        self._execution_tool_calls.pop(execution_id, None)
