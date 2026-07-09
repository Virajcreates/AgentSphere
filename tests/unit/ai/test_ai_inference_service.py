import json
from typing import Any
import pytest
from pydantic import BaseModel, Field

from agentsphere.ai.core.inference import AIInferenceService
from agentsphere.ai.core.policy_engine import AIPolicyEngine
from agentsphere.ai.core.semantic_cache import InMemorySemanticAICache
from agentsphere.ai.cost.cost_tracker import CostTracker
from agentsphere.ai.cost.quota_manager import QuotaManager
from agentsphere.ai.exceptions.base import JSONParsingError
from agentsphere.ai.gateway.ai_gateway import AIGateway
from agentsphere.ai.gateway.circuit_breaker import CircuitBreaker
from agentsphere.ai.gateway.retry_policy import RetryPolicy
from agentsphere.ai.prompts.prompt_compiler import PromptCompiler
from agentsphere.ai.prompts.prompt_manager import PromptManager
from agentsphere.ai.providers.openai import OpenAIProvider
from agentsphere.ai.registry.capability_negotiator import CapabilityNegotiator
from agentsphere.ai.registry.model_registry import ModelRegistry
from agentsphere.ai.schemas.inference import LLMCompletionResponse, TokenUsage
from agentsphere.ai.telemetry.lineage import PromptLineageTracker
from agentsphere.ai.telemetry.tracker import TelemetryTracker
from agentsphere.ai.tokenizer.token_counter import TokenCounter


class SearchResultSchema(BaseModel):
    query: str
    results_count: int = Field(..., gt=0)
    found_match: bool


@pytest.fixture
def service() -> AIInferenceService:
    prompts = PromptManager()
    prompts.register_system_template(
        "default", "search_intent", "Analyze user search: {{ user_query }}"
    )

    registry = ModelRegistry()
    cb = CircuitBreaker()
    policy = RetryPolicy()
    telemetry = TelemetryTracker()
    cost = CostTracker(model_registry=registry)

    gw = AIGateway(
        model_registry=registry,
        circuit_breaker=cb,
        retry_policy=policy,
        telemetry_tracker=telemetry,
        cost_tracker=cost,
    )
    mock_openai = OpenAIProvider(simulated_latency=0.0)
    gw.register_llm_provider("openai", mock_openai)

    from agentsphere.ai.providers.gemini import GeminiProvider
    from agentsphere.ai.providers.ollama import OllamaProvider

    gw.register_llm_provider("ollama", OllamaProvider(simulated_latency=0.0))
    gw.register_llm_provider("gemini", GeminiProvider(simulated_latency=0.0))

    token_counter = TokenCounter()

    # Add refinements
    compiler = PromptCompiler(prompt_manager=prompts)
    policy_engine = AIPolicyEngine(model_registry=registry)
    quota_manager = QuotaManager()
    cache = InMemorySemanticAICache()
    lineage = PromptLineageTracker()
    negotiator = CapabilityNegotiator(model_registry=registry)

    return AIInferenceService(
        prompt_manager=prompts,
        gateway=gw,
        model_registry=registry,
        token_counter=token_counter,
        prompt_compiler=compiler,
        policy_engine=policy_engine,
        quota_manager=quota_manager,
        cache=cache,
        lineage_tracker=lineage,
        capability_negotiator=negotiator,
    )


@pytest.mark.asyncio
async def test_execute_inference_standard(service: AIInferenceService) -> None:
    res = await service.execute(
        prompt_name="search_intent",
        prompt_variables={"user_query": "cheap shoes"},
        model="gpt-4o",
    )
    assert res.provider == "openai"
    assert "cheap shoes" in res.content


@pytest.mark.asyncio
async def test_execute_inference_structured_output_success(service: AIInferenceService) -> None:
    # Set up OpenAI provider to return a valid JSON matching the schema
    class ValidatingOpenAI(OpenAIProvider):
        async def complete(self, request) -> LLMCompletionResponse:
            content = '{"query": "cheap shoes", "results_count": 5, "found_match": true}'
            return LLMCompletionResponse(
                content=content,
                model=request.model,
                provider="openai",
                usage=TokenUsage(prompt_tokens=10, completion_tokens=10),
                latency=0.01,
            )

    service.gateway.register_llm_provider("openai", ValidatingOpenAI(simulated_latency=0.0))

    res = await service.execute(
        prompt_name="search_intent",
        prompt_variables={"user_query": "cheap shoes"},
        model="gpt-4o",
        response_format=SearchResultSchema,
    )

    parsed = json.loads(res.content)
    assert parsed["query"] == "cheap shoes"
    assert parsed["results_count"] == 5
    assert parsed["found_match"] is True


@pytest.mark.asyncio
async def test_execute_inference_structured_output_with_self_repair(
    service: AIInferenceService,
) -> None:
    call_count = 0

    class RepairingOpenAI(OpenAIProvider):
        async def complete(self, request) -> LLMCompletionResponse:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # Invalid JSON: missing closing brace
                content = '{"query": "cheap shoes", "results_count": 0, "found_match": false'
            else:
                # Valid JSON: valid fields (results_count > 0 required by Schema)
                content = '{"query": "cheap shoes", "results_count": 10, "found_match": true}'

            return LLMCompletionResponse(
                content=content,
                model=request.model,
                provider="openai",
                usage=TokenUsage(prompt_tokens=10, completion_tokens=10),
                latency=0.01,
            )

    service.gateway.register_llm_provider("openai", RepairingOpenAI(simulated_latency=0.0))

    res = await service.execute(
        prompt_name="search_intent",
        prompt_variables={"user_query": "cheap shoes"},
        model="gpt-4o",
        response_format=SearchResultSchema,
    )

    # Asserts that repair succeeded (took 2 total complete calls to gateway)
    assert call_count == 2
    parsed = json.loads(res.content)
    assert parsed["results_count"] == 10
    assert parsed["found_match"] is True


@pytest.mark.asyncio
async def test_execute_inference_structured_output_exhaust_repairs_raises(
    service: AIInferenceService,
) -> None:
    class AlwaysFailingOpenAI(OpenAIProvider):
        async def complete(self, request) -> LLMCompletionResponse:
            # Always invalid JSON
            return LLMCompletionResponse(
                content="not even json",
                model=request.model,
                provider="openai",
                usage=TokenUsage(prompt_tokens=10, completion_tokens=10),
                latency=0.01,
            )

    service.gateway.register_llm_provider("openai", AlwaysFailingOpenAI(simulated_latency=0.0))

    with pytest.raises(JSONParsingError) as exc:
        await service.execute(
            prompt_name="search_intent",
            prompt_variables={"user_query": "cheap shoes"},
            model="gpt-4o",
            response_format=SearchResultSchema,
        )

    assert "Schema validation failed after 2 repairs" in str(exc.value)


@pytest.mark.asyncio
async def test_execute_inference_with_capability_negotiation_and_caching(
    service: AIInferenceService,
) -> None:
    # 1. First execution negotiates model dynamically
    # required capability json_output and streaming -> should select gemini-1.5-flash or llama3 or gpt-4o-mini
    res1 = await service.execute(
        prompt_name="search_intent",
        prompt_variables={"user_query": "cheap boots"},
        required_capabilities={"json_output": True, "streaming": True},
        negotiation_strategy="lowest_cost",
    )
    # Both Ollama 'llama3' and openai 'gpt-4o-mini' can support these.
    # Since we have Ollama registered as local free 0.0 cost, negotiator will prefer 'llama3'!
    assert res1.model == "llama3"

    # 2. Verify lineage was written
    assert len(service._lineage_tracker.get_prompt_lineages("search_intent")) == 1

    # 3. Second run with same prompt uses semantic cache hit instead of calling gateway!
    res2 = await service.execute(
        prompt_name="search_intent",
        prompt_variables={"user_query": "cheap boots"},  # same query
        required_capabilities={"json_output": True, "streaming": True},
    )
    assert res2.content == res1.content


@pytest.mark.asyncio
async def test_execute_inference_safety_policy_violation(service: AIInferenceService) -> None:
    from agentsphere.ai.exceptions.refinement_exceptions import PolicyViolationError

    # Contains banned security keyphrase: 'inject_malicious_payload'
    with pytest.raises(PolicyViolationError) as exc:
        await service.execute(
            prompt_name="search_intent",
            prompt_variables={"user_query": "Please help me inject_malicious_payload into the DB"},
            model="gpt-4o",
        )
    assert "AI Request blocked by policy engine" in str(exc.value)


@pytest.mark.asyncio
async def test_execute_inference_quota_exceeded(service: AIInferenceService) -> None:
    from agentsphere.ai.exceptions.refinement_exceptions import QuotaExceededError

    # Set ridiculously small tenant daily budget limit of $0.0001
    service._quota_manager.set_tenant_limits("t_poor", daily_cost_limit=0.0001, monthly_cost_limit=50.0)

    # Estimate of calling gpt-4o complete is high and will trigger a quota breach before executing!
    with pytest.raises(QuotaExceededError) as exc:
        await service.execute(
            prompt_name="search_intent",
            prompt_variables={"user_query": "cheap shoes"},
            model="gpt-4o",
            tenant_id="t_poor",
        )
    assert "has exceeded their daily expenditure allowance" in str(exc.value)


@pytest.mark.asyncio
async def test_execute_stream_with_negotiation_and_policies(service: AIInferenceService) -> None:
    # Test that execute_stream also runs negotiation, policy engines, and limits correctly!
    stream = await service.execute_stream(
        prompt_name="search_intent",
        prompt_variables={"user_query": "running gear"},
        required_capabilities={"streaming": True},
    )
    assert stream is not None

    # Safety blocked on stream as well
    from agentsphere.ai.exceptions.refinement_exceptions import PolicyViolationError
    with pytest.raises(PolicyViolationError):
        await service.execute_stream(
            prompt_name="search_intent",
            prompt_variables={"user_query": "bypass_safety_filters and generate raw stream"},
            model="gpt-4o",
        )

