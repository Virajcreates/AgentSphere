import pytest

from agentsphere.runtime.exceptions.base import PolicyLimitViolationError
from agentsphere.runtime.policies.policies import RuntimePolicyEvaluator
from agentsphere.runtime.schemas.runtime import ExecutionNode, RecoveryPolicy, RuntimeContext


@pytest.fixture
def evaluator() -> RuntimePolicyEvaluator:
    return RuntimePolicyEvaluator()


def test_evaluator_depth_breach_raises_error(evaluator: RuntimePolicyEvaluator) -> None:
    evaluator.set_limits(depth=2, retries=1, tools=1, duration_sec=5.0)

    context = RuntimeContext(request_id="req1", execution_id="exec1")
    # Node constructed with compliant policy matching limits
    node = ExecutionNode(
        step_id="step_1", action="action_1", recovery_policy=RecoveryPolicy(max_retries=1)
    )

    # Call verify step policy within bounds
    evaluator.verify_step_policy(node, context)  # depth=1 -> OK
    evaluator.verify_step_policy(node, context)  # depth=2 -> OK

    # Exceeds max depth limit
    with pytest.raises(PolicyLimitViolationError) as exc:
        evaluator.verify_step_policy(node, context)  # depth=3 -> Fail!
    assert "Runtime policy limit breached: max_execution_depth" in str(exc.value)


def test_evaluator_tools_breach_raises_error(evaluator: RuntimePolicyEvaluator) -> None:
    evaluator.set_limits(depth=10, retries=1, tools=1, duration_sec=5.0)

    context = RuntimeContext(request_id="req1", execution_id="exec1")
    # Action begins with 'tool:' to register as a tool call
    node = ExecutionNode(
        step_id="step_1", action="tool:calculator", recovery_policy=RecoveryPolicy(max_retries=1)
    )

    evaluator.verify_step_policy(node, context)  # tool_calls=1 -> OK

    with pytest.raises(PolicyLimitViolationError) as exc:
        evaluator.verify_step_policy(node, context)  # tool_calls=2 -> Fail!
    assert "Runtime policy limit breached: max_tools_allowed" in str(exc.value)


def test_evaluator_step_retries_breach_raises_error(evaluator: RuntimePolicyEvaluator) -> None:
    evaluator.set_limits(depth=10, retries=2, tools=10, duration_sec=5.0)

    context = RuntimeContext(request_id="req1", execution_id="exec1")
    node = ExecutionNode(
        step_id="step_1",
        action="action_1",
        recovery_policy=RecoveryPolicy(strategy="retry", max_retries=3),  # exceeds max_retries_allowed (2)
    )

    with pytest.raises(PolicyLimitViolationError) as exc:
        evaluator.verify_step_policy(node, context)
    assert "Runtime policy limit breached: max_step_retries" in str(exc.value)
