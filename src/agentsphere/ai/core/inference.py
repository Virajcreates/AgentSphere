import json
from typing import Any

import structlog
from pydantic import BaseModel, ValidationError

from agentsphere.ai.exceptions.base import JSONParsingError
from agentsphere.ai.gateway.ai_gateway import AIGateway
from agentsphere.ai.prompts.prompt_manager import PromptManager
from agentsphere.ai.registry.model_registry import ModelRegistry
from agentsphere.ai.schemas.inference import (
    LLMCompletionRequest,
    LLMCompletionResponse,
    PromptMessage,
)
from agentsphere.ai.streaming.stream import AIStream
from agentsphere.ai.tokenizer.token_counter import TokenCounter

logger = structlog.get_logger(__name__)


class AIInferenceService:
    def __init__(
        self,
        prompt_manager: PromptManager,
        gateway: AIGateway,
        model_registry: ModelRegistry,
        token_counter: TokenCounter,
    ) -> None:
        self.prompts = prompt_manager
        self.gateway = gateway
        self.registry = model_registry
        self.token_counter = token_counter

    async def execute(
        self,
        prompt_name: str,
        prompt_variables: dict[str, Any],
        model: str,
        prompt_namespace: str = "default",
        tenant_id: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        response_format: type[BaseModel] | None = None,
        failover_providers: list[str] | None = None,
    ) -> LLMCompletionResponse:
        # 1. Render prompt from templates
        rendered_prompt = self.prompts.render(
            namespace=prompt_namespace,
            name=prompt_name,
            variables=prompt_variables,
            tenant_id=tenant_id,
        )

        # 2. Construct messages
        messages = [PromptMessage(role="user", content=rendered_prompt)]

        # 3. Handle json mode setting if schema is provided
        json_mode = response_format is not None

        request = LLMCompletionRequest(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=json_mode,
        )

        # 4. Invoke gateway complete
        response = await self.gateway.complete(request, failover_providers=failover_providers)

        # 5. Schema validation and self-repair loop
        if response_format is not None:
            response = await self._validate_and_repair_json(
                response_format=response_format,
                original_request=request,
                response=response,
                failover_providers=failover_providers,
                attempt=1,
                max_repair_attempts=2,
            )

        return response

    async def execute_stream(
        self,
        prompt_name: str,
        prompt_variables: dict[str, Any],
        model: str,
        prompt_namespace: str = "default",
        tenant_id: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AIStream:
        rendered_prompt = self.prompts.render(
            namespace=prompt_namespace,
            name=prompt_name,
            variables=prompt_variables,
            tenant_id=tenant_id,
        )

        messages = [PromptMessage(role="user", content=rendered_prompt)]

        request = LLMCompletionRequest(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=False,
        )

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
            # Parse response text as JSON and validate against model
            parsed_json = json.loads(response.content)
            response_format.model_validate(parsed_json)
            return response
        except (ValueError, ValidationError) as err:
            if attempt > max_repair_attempts:
                # Max repair attempts exhausted, raise JSONParsingError
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

            # Construct self-repair instructions for the model
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
                temperature=0.1,  # Lower temperature for strict schema adherence during repair
                max_tokens=original_request.max_tokens,
                json_mode=True,
            )

            # Invoke gateway with repair request
            repair_response = await self.gateway.complete(
                repair_request, failover_providers=failover_providers
            )

            # Recurse to validate the repaired response
            return await self._validate_and_repair_json(
                response_format=response_format,
                original_request=original_request,
                response=repair_response,
                failover_providers=failover_providers,
                attempt=attempt + 1,
                max_repair_attempts=max_repair_attempts,
            )
