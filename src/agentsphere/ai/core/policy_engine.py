
from agentsphere.ai.exceptions.refinement_exceptions import PolicyViolationError
from agentsphere.ai.registry.model_registry import ModelRegistry
from agentsphere.ai.schemas.inference import LLMCompletionRequest


class AIPolicyEngine:
    def __init__(self, model_registry: ModelRegistry) -> None:
        self._registry = model_registry

        # Base Global constraints (can be configured dynamically)
        self.allowed_providers: set[str] = {
            "openai",
            "gemini",
            "anthropic",
            "groq",
            "openrouter",
            "ollama",
            "nvidia",
            "azure_openai",
        }
        self.max_tokens_limit: int = 16384  # Max combined token request overhead
        self.max_cost_limit_usd: float = 10.0  # Max potential transaction expense

        # Tenant-scoped forbidden models: tenant_id -> list of disallowed models/providers
        self._tenant_disallowed_models: dict[str, set[str]] = {}

        # Global safety keyphrase regexes (basic moderation layer)
        self.banned_terms: list[str] = [
            "inject_malicious_payload",
            "bypass_safety_filters",
            "destroy_database_records",
        ]

    def restrict_tenant_model(self, tenant_id: str, model_id: str) -> None:
        tid = tenant_id.lower()
        if tid not in self._tenant_disallowed_models:
            self._tenant_disallowed_models[tid] = set()
        self._tenant_disallowed_models[tid].add(model_id.lower())

    def validate_request(self, request: LLMCompletionRequest, tenant_id: str | None = None) -> None:
        """Validates an incoming request against system-level safety policies, token constraints,

        whitelists, budgets, and tenant boundaries.
        """
        model_id = request.model.lower()

        # 1. Look up model info
        model_info = self._registry.get_model(request.model, request.model)
        provider = model_info.provider.lower()

        # 2. Check Provider Whitelist
        if provider not in self.allowed_providers:
            raise PolicyViolationError(f"AI Provider '{provider}' is not allowed by policy")

        # 3. Check Tenant restrictions
        if tenant_id:
            tid = tenant_id.lower()
            disallowed = self._tenant_disallowed_models.get(tid, set())
            if model_id in disallowed or provider in disallowed:
                raise PolicyViolationError(
                    f"Tenant '{tenant_id}' is restricted from using model '{request.model}'"
                )

        # 4. Check Token Limits (Request Max Tokens)
        if request.max_tokens and request.max_tokens > self.max_tokens_limit:
            raise PolicyViolationError(
                f"Requested max_tokens ({request.max_tokens}) exceeds maximum allowable token cap "
                f"of {self.max_tokens_limit} tokens"
            )

        # 5. Check Safety Policies (Banned Content scanning)
        prompt_content = " ".join(m.content for m in request.messages).lower()
        for term in self.banned_terms:
            if term in prompt_content:
                raise PolicyViolationError(
                    f"Content blocked: request contains banned safety term: '{term}'"
                )

        # 6. Check Cost Limits (Estimate maximum potential cost of transaction)
        # Potential maximum cost = (est_prompt_tokens * input) + (max_tokens * output)
        prompt_tokens_est = max(5, int(len(prompt_content) / 4))
        max_output_tokens = request.max_tokens or 4096

        input_cost = (prompt_tokens_est / 1_000_000.0) * model_info.costs.input_cost_per_1m
        output_cost = (max_output_tokens / 1_000_000.0) * model_info.costs.output_cost_per_1m
        max_estimated_cost = input_cost + output_cost

        if max_estimated_cost > self.max_cost_limit_usd:
            raise PolicyViolationError(
                f"Maximum estimated transaction cost (${max_estimated_cost:.4f}) exceeds allowable "
                f"budget threshold of ${self.max_cost_limit_usd:.2f} USD"
            )
