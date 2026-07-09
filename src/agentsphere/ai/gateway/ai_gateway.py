import time
from typing import cast

import structlog

from agentsphere.ai.cost.cost_tracker import CostTracker
from agentsphere.ai.exceptions.base import AIError, ModelNotFoundError, ProviderError
from agentsphere.ai.gateway.circuit_breaker import CircuitBreaker
from agentsphere.ai.gateway.retry_policy import RetryPolicy
from agentsphere.ai.interfaces.providers import EmbeddingProvider, LLMProvider
from agentsphere.ai.registry.model_registry import ModelRegistry
from agentsphere.ai.schemas.inference import (
    EmbeddingRequest,
    EmbeddingResponse,
    LLMCompletionRequest,
    LLMCompletionResponse,
)
from agentsphere.ai.streaming.stream import AIStream
from agentsphere.ai.telemetry.benchmarking import ProviderBenchmarkCollector
from agentsphere.ai.telemetry.tracker import TelemetryTracker

logger = structlog.get_logger(__name__)


class AIGateway:
    def __init__(
        self,
        model_registry: ModelRegistry,
        circuit_breaker: CircuitBreaker,
        retry_policy: RetryPolicy,
        telemetry_tracker: TelemetryTracker,
        cost_tracker: CostTracker,
        llm_providers: dict[str, LLMProvider] | None = None,
        embedding_providers: dict[str, EmbeddingProvider] | None = None,
        benchmark_collector: ProviderBenchmarkCollector | None = None,
    ) -> None:
        self.registry = model_registry
        self.circuit_breaker = circuit_breaker
        self.retry_policy = retry_policy
        self.telemetry = telemetry_tracker
        self.cost_tracker = cost_tracker
        self.benchmark = benchmark_collector

        self._llm_providers = llm_providers or {}
        self._embedding_providers = embedding_providers or {}

    def register_llm_provider(self, name: str, provider: LLMProvider) -> None:
        self._llm_providers[name.lower()] = provider

    def register_embedding_provider(self, name: str, provider: EmbeddingProvider) -> None:
        self._embedding_providers[name.lower()] = provider

    def _get_llm_provider(self, provider_name: str) -> LLMProvider:
        name = provider_name.lower()
        if name not in self._llm_providers:
            raise ProviderError(provider_name, "LLM provider adapter not registered", 501)
        return self._llm_providers[name]

    def _get_embedding_provider(self, provider_name: str) -> EmbeddingProvider:
        name = provider_name.lower()
        if name not in self._embedding_providers:
            raise ProviderError(provider_name, "Embedding provider adapter not registered", 501)
        return self._embedding_providers[name]

    async def complete(
        self, request: LLMCompletionRequest, failover_providers: list[str] | None = None
    ) -> LLMCompletionResponse:
        # Resolve model to find primary provider
        try:
            model_info = self.registry.get_model(request.model, request.model)
            primary_provider = model_info.provider
        except ModelNotFoundError:
            # Fallback to direct naming format or throw
            if "/" in request.model:
                primary_provider, _ = request.model.split("/", 1)
            else:
                raise

        providers_to_try = [primary_provider]
        if failover_providers:
            for p in failover_providers:
                if p.lower() != primary_provider.lower():
                    providers_to_try.append(p)

        last_error = None
        for current_provider in providers_to_try:
            retry_count = 0
            try:
                # 1. Circuit Breaker Check
                self.circuit_breaker.allow_request(current_provider)

                # 2. Resolve adapter
                adapter = self._get_llm_provider(current_provider)

                # 3. Define the actual execution closure for retry policy
                async def execute_call(a: LLMProvider = adapter) -> LLMCompletionResponse:
                    return await a.complete(request)

                # 4. Handle logging retry hooks
                async def on_retry(
                    exc: Exception, attempt: int, delay: float, prov: str = current_provider
                ) -> None:
                    nonlocal retry_count
                    retry_count += 1
                    logger.warn(
                        "Retrying AI complete request",
                        provider=prov,
                        model=request.model,
                        attempt=attempt,
                        delay=delay,
                        error=str(exc),
                    )

                # 5. Execute with retry policy
                start_time = time.perf_counter()
                response = cast(
                    LLMCompletionResponse,
                    await self.retry_policy.execute(execute_call, on_retry=on_retry),
                )
                duration = time.perf_counter() - start_time

                # 6. Record Success in Circuit Breaker
                self.circuit_breaker.record_success(current_provider)

                # 7. Cost calculation and performance stats
                cost = self.cost_tracker.calculate_completion_cost(
                    current_provider,
                    request.model,
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens,
                )
                response.usage.cost = cost

                self.registry.update_model_performance(
                    current_provider, request.model, duration, True
                )

                # 8. Record Benchmarking Stats
                if self.benchmark:
                    self.benchmark.record_attempt(
                        provider=current_provider,
                        latency=duration,
                        success=True,
                        retries=retry_count,
                        timed_out=False,
                        cost=cost,
                    )

                # 9. Track Telemetry
                self.telemetry.track_request(
                    provider=current_provider,
                    model=request.model,
                    operation="complete",
                    latency=duration,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    cost=cost,
                )

                return response

            except Exception as e:
                # Record Failure in Circuit Breaker
                self.circuit_breaker.record_failure(current_provider)

                # Update registry stats
                from contextlib import suppress

                with suppress(Exception):
                    self.registry.update_model_performance(
                        current_provider, request.model, 0.0, False
                    )

                # Record Benchmarking Failure
                if self.benchmark:
                    from agentsphere.ai.exceptions.base import ProviderTimeoutError

                    timed_out = isinstance(e, ProviderTimeoutError)
                    self.benchmark.record_attempt(
                        provider=current_provider,
                        latency=0.0,
                        success=False,
                        retries=retry_count,
                        timed_out=timed_out,
                        cost=0.0,
                    )

                # Track failure telemetry
                self.telemetry.track_error(
                    provider=current_provider,
                    model=request.model,
                    operation="complete",
                    error_type=e.__class__.__name__,
                )

                last_error = e
                logger.error(
                    "AI Gateway request failed",
                    provider=current_provider,
                    model=request.model,
                    error=str(e),
                )
                # Keep looping to try failover provider if available
                continue

        # If all providers failed, raise the final error
        raise last_error or AIError("AI Request failed with zero routes successfully traversed")

    async def complete_stream(self, request: LLMCompletionRequest) -> AIStream:
        try:
            model_info = self.registry.get_model(request.model, request.model)
            primary_provider = model_info.provider
        except ModelNotFoundError:
            if "/" in request.model:
                primary_provider, _ = request.model.split("/", 1)
            else:
                raise

        # Check circuit breaker
        self.circuit_breaker.allow_request(primary_provider)
        adapter = self._get_llm_provider(primary_provider)

        # Call adapter complete_stream
        generator = await adapter.complete_stream(request)

        # Telemetry completion callback inside AIStream
        async def on_stream_complete(
            provider: str,
            model: str,
            latency: float,
            prompt_tokens: int,
            completion_tokens: int,
            text: str,
            cost: float,
        ) -> None:
            # Record success in circuit breaker on successful completion
            self.circuit_breaker.record_success(provider)

            # Recalculate cost if not updated by stream chunks
            stream_cost = self.cost_tracker.calculate_completion_cost(
                provider, model, prompt_tokens, completion_tokens
            )

            self.registry.update_model_performance(provider, model, latency, True)

            if self.benchmark:
                self.benchmark.record_attempt(
                    provider=provider,
                    latency=latency,
                    success=True,
                    retries=0,
                    timed_out=False,
                    cost=stream_cost,
                )

            self.telemetry.track_request(
                provider=provider,
                model=model,
                operation="complete_stream",
                latency=latency,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost=stream_cost,
            )

        # Create standard stream
        return AIStream(
            stream_generator=generator,
            provider=primary_provider,
            model=request.model,
            on_complete=on_stream_complete,
        )

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        try:
            model_info = self.registry.get_model(request.model, request.model)
            provider_name = model_info.provider
        except ModelNotFoundError:
            if "/" in request.model:
                provider_name, _ = request.model.split("/", 1)
            else:
                raise

        self.circuit_breaker.allow_request(provider_name)
        adapter = self._get_embedding_provider(provider_name)

        start_time = time.perf_counter()
        try:
            response = await adapter.embed(request)
            duration = time.perf_counter() - start_time

            self.circuit_breaker.record_success(provider_name)

            cost = self.cost_tracker.calculate_embedding_cost(
                provider_name, request.model, response.usage.embedding_tokens
            )
            response.usage.cost = cost

            if self.benchmark:
                self.benchmark.record_attempt(
                    provider=provider_name,
                    latency=duration,
                    success=True,
                    retries=0,
                    timed_out=False,
                    cost=cost,
                )

            self.telemetry.track_request(
                provider=provider_name,
                model=request.model,
                operation="embed",
                latency=duration,
                prompt_tokens=response.usage.prompt_tokens,
                cost=cost,
            )
            return response
        except Exception as e:
            self.circuit_breaker.record_failure(provider_name)

            if self.benchmark:
                from agentsphere.ai.exceptions.base import ProviderTimeoutError

                self.benchmark.record_attempt(
                    provider=provider_name,
                    latency=0.0,
                    success=False,
                    retries=0,
                    timed_out=isinstance(e, ProviderTimeoutError),
                    cost=0.0,
                )

            self.telemetry.track_error(
                provider=provider_name,
                model=request.model,
                operation="embed",
                error_type=e.__class__.__name__,
            )
            raise
