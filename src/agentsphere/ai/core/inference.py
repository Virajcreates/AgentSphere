import json
from typing import Any

import structlog
from pydantic import BaseModel, ValidationError

from agentsphere.ai.core.policy_engine import AIPolicyEngine
from agentsphere.ai.cost.quota_manager import QuotaManager
from agentsphere.ai.exceptions.base import JSONParsingError
from agentsphere.ai.gateway.ai_gateway import AIGateway
from agentsphere.ai.interfaces.cache import AICache
from agentsphere.ai.prompts.prompt_compiler import PromptCompiler
from agentsphere.ai.prompts.prompt_manager import PromptManager
from agentsphere.ai.registry.capability_negotiator import CapabilityNegotiator
from agentsphere.ai.registry.model_registry import ModelRegistry
from agentsphere.ai.schemas.inference import (
    LLMCompletionRequest,
    LLMCompletionResponse,
    PromptMessage,
)
from agentsphere.ai.streaming.stream import AIStream
from agentsphere.ai.telemetry.lineage import PromptLineageTracker
from agentsphere.ai.tokenizer.token_counter import TokenCounter

logger = structlog.get_logger(__name__)


class AIInferenceService:
    def __init__(
        self,
        prompt_manager: PromptManager,
        gateway: AIGateway,
        model_registry: ModelRegistry,
        token_counter: TokenCounter,
        prompt_compiler: PromptCompiler | None = None,
        policy_engine: AIPolicyEngine | None = None,
        quota_manager: QuotaManager | None = None,
        cache: AICache | None = None,
        lineage_tracker: PromptLineageTracker | None = None,
        capability_negotiator: CapabilityNegotiator | None = None,
    ) -> None:
        self.prompts = prompt_manager
        self.gateway = gateway
        self.registry = model_registry
        self.token_counter = token_counter

        # Refinements
        self._compiler = prompt_compiler
        self._policy_engine = policy_engine
        self._quota_manager = quota_manager
        self._cache = cache
        self._lineage_tracker = lineage_tracker
        self._negotiator = capability_negotiator

    async def execute(
        self,
        prompt_name: str,
        prompt_variables: dict[str, Any],
        model: str | None = None,
        prompt_namespace: str = "default",
        tenant_id: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        response_format: type[BaseModel] | None = None,
        failover_providers: list[str] | None = None,
        required_capabilities: dict[str, bool] | None = None,
        negotiation_strategy: str = "lowest_cost",
        bypass_cache: bool = False,
    ) -> LLMCompletionResponse:
        # 1. Negotiate model if requested
        target_model = model
        if required_capabilities and self._negotiator:
            target_model = self._negotiator.negotiate_model(
                required_capabilities=required_capabilities,
                strategy=negotiation_strategy,
            )

        if not target_model:
            raise ValueError(
                "Either 'model' must be supplied or 'required_capabilities' must be enabled"
            )

        # 2. Compile or Render prompt
        if self._compiler:
            rendered_prompt = self._compiler.compile(
                namespace=prompt_namespace,
                name=prompt_name,
                variables=prompt_variables,
                tenant_id=tenant_id,
                bypass_cache=bypass_cache,
            )
        else:
            rendered_prompt = self.prompts.render(
                namespace=prompt_namespace,
                name=prompt_name,
                variables=prompt_variables,
                tenant_id=tenant_id,
            )

        # 3. Check Semantic / Exact Cache
        if self._cache and not bypass_cache:
            cached_res = await self._cache.get(rendered_prompt, tenant_id=tenant_id)
            if cached_res:
                logger.info("Semantic AI Cache Hit", prompt_name=prompt_name, tenant_id=tenant_id)
                # Ensure correct model metadata in cached response matching negotiated model
                cached_res.model = target_model
                return cached_res

        # 4. Construct messages
        messages = [PromptMessage(role="user", content=rendered_prompt)]
        json_mode = response_format is not None

        request = LLMCompletionRequest(
            model=target_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=json_mode,
        )

        # 5. Enforce Security Policies
        if self._policy_engine:
            self._policy_engine.validate_request(request, tenant_id=tenant_id)

        # 6. Enforce Tenant and Provider Quota caps (pre-check)
        if self._quota_manager:
            # Estimate max potential transaction expense
            model_info = self.registry.get_model(target_model, target_model)
            prompt_tokens_est = max(5, int(len(rendered_prompt) / 4))
            max_output_tokens = request.max_tokens or 4096

            input_cost = (prompt_tokens_est / 1_000_000.0) * model_info.costs.input_cost_per_1m
            output_cost = (max_output_tokens / 1_000_000.0) * model_info.costs.output_cost_per_1m
            est_cost = input_cost + output_cost

            self._quota_manager.check_quota(tenant_id, model_info.provider, est_cost)

        # 7. Invoke gateway execution
        response = await self.gateway.complete(request, failover_providers=failover_providers)

        # 8. Structured outputs validation and self-repair loop
        if response_format is not None:
            response = await self._validate_and_repair_json(
                response_format=response_format,
                original_request=request,
                response=response,
                failover_providers=failover_providers,
                attempt=1,
                max_repair_attempts=2,
            )

        # 9. Commit stats inside QuotaManager on successful transactions
        if self._quota_manager:
            model_info = self.registry.get_model(target_model, target_model)
            self._quota_manager.record_usage(
                tenant_id, model_info.provider, response.usage.cost, response.usage.total_tokens
            )

        # 10. Persist Response in semantic cache
        if self._cache:
            await self._cache.set(rendered_prompt, response, tenant_id=tenant_id)

        # 11. Record execution lineage
        if self._lineage_tracker:
            self._lineage_tracker.record_lineage(
                prompt_name=prompt_name,
                prompt_version="latest",
                rendered_prompt=rendered_prompt,
                input_variables=prompt_variables,
                provider=response.provider,
                model=response.model,
                response_metadata={
                    "latency": response.latency,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "cost": response.usage.cost,
                },
            )

        return response

    async def execute_stream(
        self,
        prompt_name: str,
        prompt_variables: dict[str, Any],
        model: str | None = None,
        prompt_namespace: str = "default",
        tenant_id: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        required_capabilities: dict[str, bool] | None = None,
        negotiation_strategy: str = "lowest_cost",
    ) -> AIStream:
        target_model = model
        if required_capabilities and self._negotiator:
            target_model = self._negotiator.negotiate_model(
                required_capabilities=required_capabilities,
                strategy=negotiation_strategy,
            )

        if not target_model:
            raise ValueError(
                "Either 'model' must be supplied or 'required_capabilities' must be enabled"
            )

        if self._compiler:
            rendered_prompt = self._compiler.compile(
                namespace=prompt_namespace,
                name=prompt_name,
                variables=prompt_variables,
                tenant_id=tenant_id,
            )
        else:
            rendered_prompt = self.prompts.render(
                namespace=prompt_namespace,
                name=prompt_name,
                variables=prompt_variables,
                tenant_id=tenant_id,
            )

        messages = [PromptMessage(role="user", content=rendered_prompt)]

        request = LLMCompletionRequest(
            model=target_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=False,
        )

        if self._policy_engine:
            self._policy_engine.validate_request(request, tenant_id=tenant_id)

        if self._quota_manager:
            model_info = self.registry.get_model(target_model, target_model)
            prompt_tokens_est = max(5, int(len(rendered_prompt) / 4))
            max_output_tokens = request.max_tokens or 4096
            input_cost = (prompt_tokens_est / 1_000_000.0) * model_info.costs.input_cost_per_1m
            output_cost = (max_output_tokens / 1_000_000.0) * model_info.costs.output_cost_per_1m
            est_cost = input_cost + output_cost
            self._quota_manager.check_quota(tenant_id, model_info.provider, est_cost)

        return await self.gateway.complete_stream(request)

    async def _validate_and_repair_json(
        self,
        response_format: type[BaseModel],
        original_request: LLMCompletionRequest,
        response: LLMCompletionResponse,
        failover_providers: list[str] | None,
        attempt: int,
        max_repair_attempts: int = 2,
    ) -> LLMCompletionResponse:
        try:
            parsed_json = json.loads(response.content)
            response_format.model_validate(parsed_json)
            return response
        except (ValueError, ValidationError) as err:
            if attempt > max_repair_attempts:
                raise JSONParsingError(
                    detail=(
                        f"Schema validation failed after {max_repair_attempts} repairs: "
                        f"{err!s}"
                    ),
                    raw_output=response.content,
                ) from err

            logger.warn(
                "JSON Schema validation failed. Initiating self-repair",
                model=original_request.model,
                attempt=attempt,
                error=str(err),
            )

            repair_prompt = (
                "Your previous response failed validation against the required JSON schema.\n"
                f"Error: {err!s}\n"
                f"Original Output was: {response.content}\n"
                "Please reply with ONLY the corrected, valid JSON object that strictly "
                "adheres to the schema."
            )

            repair_messages = list(original_request.messages)
            repair_messages.append(PromptMessage(role="assistant", content=response.content))
            repair_messages.append(PromptMessage(role="user", content=repair_prompt))

            repair_request = LLMCompletionRequest(
                model=original_request.model,
                messages=repair_messages,
                temperature=0.1,
                max_tokens=original_request.max_tokens,
                json_mode=True,
            )

            repair_response = await self.gateway.complete(
                repair_request, failover_providers=failover_providers
            )

            return await self._validate_and_repair_json(
                response_format=response_format,
                original_request=original_request,
                response=repair_response,
                failover_providers=failover_providers,
                attempt=attempt + 1,
                max_repair_attempts=max_repair_attempts,
            )
