import json
from typing import Any
import pytest
from pydantic import BaseModel, Field

from agentsphere.ai.core.inference import AIInferenceService
from agentsphere.ai.cost.cost_tracker import CostTracker
from agentsphere.ai.exceptions.base import JSONParsingError
from agentsphere.ai.gateway.ai_gateway import AIGateway
from agentsphere.ai.gateway.circuit_breaker import CircuitBreaker
from agentsphere.ai.gateway.retry_policy import RetryPolicy
from agentsphere.ai.prompts.prompt_manager import PromptManager
from agentsphere.ai.providers.openai import OpenAIProvider
from agentsphere.ai.registry.model_registry import ModelRegistry
from agentsphere.ai.schemas.inference import LLMCompletionResponse, TokenUsage
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

    token_counter = TokenCounter()

    return AIInferenceService(
        prompt_manager=prompts,
        gateway=gw,
        model_registry=registry,
        token_counter=token_counter,
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
