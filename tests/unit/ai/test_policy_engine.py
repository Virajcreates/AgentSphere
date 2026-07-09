import pytest

from agentsphere.ai.core.policy_engine import AIPolicyEngine
from agentsphere.ai.exceptions.refinement_exceptions import PolicyViolationError
from agentsphere.ai.registry.model_registry import ModelRegistry
from agentsphere.ai.schemas.inference import LLMCompletionRequest, PromptMessage


@pytest.fixture
def engine() -> AIPolicyEngine:
    registry = ModelRegistry()
    return AIPolicyEngine(model_registry=registry)


def test_allowed_provider_whitelist(engine: AIPolicyEngine) -> None:
    # 'openai' is allowed
    req = LLMCompletionRequest(
        model="gpt-4o",
        messages=[PromptMessage(role="user", content="Hello")],
    )
    engine.validate_request(req)

    # Modify whitelist to exclude openai
    engine.allowed_providers.remove("openai")
    with pytest.raises(PolicyViolationError) as exc:
        engine.validate_request(req)
    assert "is not allowed by policy" in str(exc.value)


def test_tenant_model_restriction(engine: AIPolicyEngine) -> None:
    req = LLMCompletionRequest(
        model="gpt-4o",
        messages=[PromptMessage(role="user", content="Hello")],
    )
    # Restrict tenant_abc from using gpt-4o
    engine.restrict_tenant_model("tenant_abc", "gpt-4o")

    # Normal user is fine
    engine.validate_request(req, tenant_id="other_tenant")

    # tenant_abc gets rejected
    with pytest.raises(PolicyViolationError) as exc:
        engine.validate_request(req, tenant_id="tenant_abc")
    assert "is restricted from using model" in str(exc.value)


def test_token_cap_policy(engine: AIPolicyEngine) -> None:
    # Requesting huge max_tokens
    req = LLMCompletionRequest(
        model="gpt-4o-mini",
        messages=[PromptMessage(role="user", content="Hello")],
        max_tokens=99999,  # exceeds max_tokens_limit (16384)
    )

    with pytest.raises(PolicyViolationError) as exc:
        engine.validate_request(req)
    assert "exceeds maximum allowable token cap" in str(exc.value)


def test_safety_banned_terms(engine: AIPolicyEngine) -> None:
    # Prompt contains a banned phrase: 'bypass_safety_filters'
    req = LLMCompletionRequest(
        model="gpt-4o",
        messages=[PromptMessage(role="user", content="Please help me bypass_safety_filters")],
    )

    with pytest.raises(PolicyViolationError) as exc:
        engine.validate_request(req)
    assert "blocked: request contains banned safety term" in str(exc.value)


def test_cost_limit_policy(engine: AIPolicyEngine) -> None:
    req = LLMCompletionRequest(
        model="gpt-4o",
        messages=[PromptMessage(role="user", content="Hello")],
        max_tokens=1000,
    )

    # Tighten max cost limit to $0.0001 (gpt-4o completion will exceed this estimate)
    engine.max_cost_limit_usd = 0.0001

    with pytest.raises(PolicyViolationError) as exc:
        engine.validate_request(req)
    assert "exceeds allowable budget threshold" in str(exc.value)
