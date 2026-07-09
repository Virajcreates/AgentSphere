import pytest

from agentsphere.ai.cost.cost_tracker import CostTracker
from agentsphere.ai.exceptions.base import CircuitBreakerOpenError, ProviderError
from agentsphere.ai.gateway.ai_gateway import AIGateway
from agentsphere.ai.gateway.circuit_breaker import CircuitBreaker
from agentsphere.ai.gateway.retry_policy import RetryPolicy
from agentsphere.ai.providers.openai import OpenAIProvider
from agentsphere.ai.registry.model_registry import ModelRegistry
from agentsphere.ai.schemas.inference import LLMCompletionRequest, PromptMessage
from agentsphere.ai.telemetry.tracker import TelemetryTracker


@pytest.fixture
def gateway() -> AIGateway:
    registry = ModelRegistry()
    cb = CircuitBreaker(failure_threshold=2, cooldown_period=5.0)
    policy = RetryPolicy(max_retries=1, base_delay=0.001)
    telemetry = TelemetryTracker()
    cost = CostTracker(model_registry=registry)

    gw = AIGateway(
        model_registry=registry,
        circuit_breaker=cb,
        retry_policy=policy,
        telemetry_tracker=telemetry,
        cost_tracker=cost,
    )

    # Register mock providers
    openai_mock = OpenAIProvider(simulated_latency=0.0)
    gw.register_llm_provider("openai", openai_mock)
    gw.register_embedding_provider("openai", openai_mock)

    return gw


@pytest.mark.asyncio
async def test_gateway_complete_routing(gateway: AIGateway) -> None:
    req = LLMCompletionRequest(
        model="gpt-4o",
        messages=[PromptMessage(role="user", content="Hello!")],
    )
    res = await gateway.complete(req)
    assert res.provider == "openai"
    assert res.model == "gpt-4o"
    assert res.usage.cost > 0.0


@pytest.mark.asyncio
async def test_gateway_circuit_breaker_trips(gateway: AIGateway) -> None:
    # Set up failing openai provider adapter
    failing_openai = OpenAIProvider(error_rate=1.0, simulated_latency=0.0)
    gateway.register_llm_provider("openai", failing_openai)

    req = LLMCompletionRequest(
        model="gpt-4o",
        messages=[PromptMessage(role="user", content="failing request")],
    )

    # First failing attempt
    with pytest.raises(ProviderError):
        await gateway.complete(req)

    # Second failing attempt (trips CB since failure_threshold=2)
    with pytest.raises(ProviderError):
        await gateway.complete(req)

    # Third attempt should fail immediately due to Circuit Breaker Open
    with pytest.raises(CircuitBreakerOpenError):
        await gateway.complete(req)


@pytest.mark.asyncio
async def test_gateway_embedding(gateway: AIGateway) -> None:
    from agentsphere.ai.schemas.inference import EmbeddingRequest

    req = EmbeddingRequest(model="text-embedding-3-small", input=["test"])
    res = await gateway.embed(req)
    assert res.provider == "openai"
    assert len(res.embeddings) == 1
    assert res.usage.cost >= 0.0


@pytest.mark.asyncio
async def test_gateway_complete_stream(gateway: AIGateway) -> None:
    req = LLMCompletionRequest(
        model="gpt-4o",
        messages=[PromptMessage(role="user", content="Hello!")],
    )
    stream = await gateway.complete_stream(req)
    assert stream.provider == "openai"
    assert stream.model == "gpt-4o"

    chunks = []
    async for chunk in stream:
        chunks.append(chunk)
    assert len(chunks) > 0


@pytest.mark.asyncio
async def test_gateway_failover(gateway: AIGateway) -> None:
    from agentsphere.ai.providers.gemini import GeminiProvider

    # First provider fails, second succeeds
    failing_openai = OpenAIProvider(error_rate=1.0, simulated_latency=0.0)
    gateway.register_llm_provider("openai", failing_openai)

    mock_gemini = GeminiProvider(simulated_latency=0.0)
    # We register it as 'gemini'
    gateway.register_llm_provider("gemini", mock_gemini)

    req = LLMCompletionRequest(
        model="gpt-4o",
        messages=[PromptMessage(role="user", content="Hello!")],
    )

    res = await gateway.complete(req, failover_providers=["gemini"])
    assert res.provider == "gemini"

