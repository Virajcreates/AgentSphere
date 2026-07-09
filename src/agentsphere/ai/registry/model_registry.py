from agentsphere.ai.exceptions.base import ModelNotFoundError
from agentsphere.ai.schemas.models import ModelCapabilities, ModelCosts, ModelInfo


class ModelRegistry:
    def __init__(self) -> None:
        self._models: dict[tuple[str, str], ModelInfo] = {}
        self._seed_default_models()

    def register_model(self, model: ModelInfo) -> None:
        key = (model.provider.lower(), model.model_id.lower())
        self._models[key] = model

    def get_model(self, provider: str, model_id: str) -> ModelInfo:
        key = (provider.lower(), model_id.lower())
        if key not in self._models:
            # Fallback to searching by model_id across all providers if not found directly
            m_id = model_id.lower()
            for model in self._models.values():
                if model.model_id.lower() == m_id:
                    return model
            raise ModelNotFoundError(provider, model_id)
        return self._models[key]

    def list_models(self) -> list[ModelInfo]:
        return list(self._models.values())

    def get_models_by_provider(self, provider: str) -> list[ModelInfo]:
        prov_lower = provider.lower()
        return [m for m in self._models.values() if m.provider.lower() == prov_lower]

    def get_models_with_capabilities(self, **kwargs: bool) -> list[ModelInfo]:
        results = []
        for model in self._models.values():
            match = True
            for cap, required_val in kwargs.items():
                if getattr(model.capabilities, cap, False) != required_val:
                    match = False
                    break
            if match:
                results.append(model)
        return results

    def update_model_health(self, provider: str, model_id: str, is_healthy: bool) -> None:
        model = self.get_model(provider, model_id)
        model.is_healthy = is_healthy

    def update_model_performance(
        self, provider: str, model_id: str, latency: float, success: bool
    ) -> None:
        model = self.get_model(provider, model_id)
        # Update exponential moving average for latency
        if model.average_latency == 0.0:
            model.average_latency = latency
        else:
            model.average_latency = (model.average_latency * 0.9) + (latency * 0.1)

        # Update success rate moving average
        success_val = 1.0 if success else 0.0
        model.success_rate = (model.success_rate * 0.95) + (success_val * 0.05)

    def _seed_default_models(self) -> None:
        defaults = [
            # OpenAI
            ModelInfo(
                model_id="gpt-4o",
                provider="openai",
                display_name="GPT-4o",
                context_window=128000,
                capabilities=ModelCapabilities(
                    streaming=True, vision=True, tool_calling=True, json_mode=True
                ),
                costs=ModelCosts(input_cost_per_1m=5.00, output_cost_per_1m=15.00),
            ),
            ModelInfo(
                model_id="gpt-4o-mini",
                provider="openai",
                display_name="GPT-4o Mini",
                context_window=128000,
                capabilities=ModelCapabilities(
                    streaming=True, vision=True, tool_calling=True, json_mode=True
                ),
                costs=ModelCosts(input_cost_per_1m=0.150, output_cost_per_1m=0.600),
            ),
            ModelInfo(
                model_id="text-embedding-3-small",
                provider="openai",
                display_name="Text Embedding 3 Small",
                context_window=8191,
                capabilities=ModelCapabilities(streaming=False, embeddings=True),
                costs=ModelCosts(input_cost_per_1m=0.02, output_cost_per_1m=0.0),
            ),
            # Gemini
            ModelInfo(
                model_id="gemini-1.5-pro",
                provider="gemini",
                display_name="Gemini 1.5 Pro",
                context_window=1048576,
                capabilities=ModelCapabilities(
                    streaming=True, vision=True, tool_calling=True, json_mode=True
                ),
                costs=ModelCosts(input_cost_per_1m=1.25, output_cost_per_1m=5.00),
            ),
            ModelInfo(
                model_id="gemini-1.5-flash",
                provider="gemini",
                display_name="Gemini 1.5 Flash",
                context_window=1048576,
                capabilities=ModelCapabilities(
                    streaming=True, vision=True, tool_calling=True, json_mode=True
                ),
                costs=ModelCosts(input_cost_per_1m=0.075, output_cost_per_1m=0.30),
            ),
            ModelInfo(
                model_id="text-embedding-004",
                provider="gemini",
                display_name="Gemini Text Embedding 004",
                context_window=3072,
                capabilities=ModelCapabilities(streaming=False, embeddings=True),
                costs=ModelCosts(input_cost_per_1m=0.025, output_cost_per_1m=0.0),
            ),
            # Anthropic
            ModelInfo(
                model_id="claude-3-5-sonnet-latest",
                provider="anthropic",
                display_name="Claude 3.5 Sonnet",
                context_window=200000,
                capabilities=ModelCapabilities(
                    streaming=True, vision=True, tool_calling=True, json_mode=True
                ),
                costs=ModelCosts(input_cost_per_1m=3.00, output_cost_per_1m=15.00),
            ),
            # Groq
            ModelInfo(
                model_id="llama-3.1-70b-versatile",
                provider="groq",
                display_name="Llama 3.1 70B (Groq)",
                context_window=131072,
                capabilities=ModelCapabilities(streaming=True, tool_calling=True, json_mode=True),
                costs=ModelCosts(input_cost_per_1m=0.59, output_cost_per_1m=0.79),
            ),
            # OpenRouter
            ModelInfo(
                model_id="meta-llama/llama-3.1-405b",
                provider="openrouter",
                display_name="Llama 3.1 405B (OpenRouter)",
                context_window=131072,
                capabilities=ModelCapabilities(streaming=True, tool_calling=True, json_mode=True),
                costs=ModelCosts(input_cost_per_1m=1.00, output_cost_per_1m=1.00),
            ),
            # Ollama
            ModelInfo(
                model_id="llama3",
                provider="ollama",
                display_name="Llama 3 (Ollama Local)",
                context_window=8192,
                capabilities=ModelCapabilities(streaming=True, tool_calling=True, json_mode=True),
                costs=ModelCosts(input_cost_per_1m=0.0, output_cost_per_1m=0.0),
            ),
            # NVIDIA
            ModelInfo(
                model_id="llama-3.1-nemotron-70b",
                provider="nvidia",
                display_name="Llama 3.1 Nemotron 70B",
                context_window=4096,
                capabilities=ModelCapabilities(streaming=True, tool_calling=True),
                costs=ModelCosts(input_cost_per_1m=0.0, output_cost_per_1m=0.0),
            ),
        ]
        for m in defaults:
            self.register_model(m)
