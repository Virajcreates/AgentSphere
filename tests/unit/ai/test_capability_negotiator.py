import pytest

from agentsphere.ai.exceptions.refinement_exceptions import CapabilityNegotiationError
from agentsphere.ai.registry.capability_negotiator import CapabilityNegotiator
from agentsphere.ai.registry.model_registry import ModelRegistry


@pytest.fixture
def negotiator() -> CapabilityNegotiator:
    registry = ModelRegistry()
    # Let's customize latency for openai and gemini to verify dynamic sorting in strategies
    m_openai = registry.get_model("openai", "gpt-4o")
    m_openai.average_latency = 1.2

    m_gemini = registry.get_model("gemini", "gemini-1.5-flash")
    m_gemini.average_latency = 0.4

    return CapabilityNegotiator(model_registry=registry)


def test_negotiate_lowest_cost(negotiator: CapabilityNegotiator) -> None:
    # Both gpt-4o-mini and gemini-1.5-flash support json_mode (json_output) and streaming.
    # Cost: gpt-4o-mini is $0.15/1M, gemini-1.5-flash is $0.075/1M.
    # Therefore, lowest_cost strategy should select gemini-1.5-flash!
    required = {"json_output": True, "streaming": True}
    model_id = negotiator.negotiate_model(required, strategy="lowest_cost", provider="gemini")
    assert model_id == "gemini-1.5-flash"


def test_negotiate_lowest_latency(negotiator: CapabilityNegotiator) -> None:
    # gpt-4o (1.2s average latency) and gemini-1.5-flash (0.4s average latency) both support vision.
    # Therefore, lowest_latency strategy should select gemini-1.5-flash!
    required = {"vision": True}
    model_id = negotiator.negotiate_model(required, strategy="lowest_latency")
    assert model_id == "gemini-1.5-flash"


def test_negotiate_provider_filter(negotiator: CapabilityNegotiator) -> None:
    required = {"vision": True}
    # Specifically request 'openai' provider -> must select the cheapest matching vision model (gpt-4o-mini)
    model_id = negotiator.negotiate_model(required, provider="openai")
    assert model_id == "gpt-4o-mini"


def test_negotiate_no_satisfying_model(negotiator: CapabilityNegotiator) -> None:
    # Requesting non-existent ridiculous capabilities
    required = {"vision": True, "embeddings": True, "reasoning": True}
    with pytest.raises(CapabilityNegotiationError) as exc:
        negotiator.negotiate_model(required)
    assert "No healthy model found satisfying capabilities" in str(exc.value)
