from agentsphere.ai.registry.model_registry import ModelRegistry


class CostTracker:
    def __init__(self, model_registry: ModelRegistry) -> None:
        self._registry = model_registry

    def calculate_completion_cost(
        self, provider: str, model_id: str, prompt_tokens: int, completion_tokens: int
    ) -> float:
        try:
            model_info = self._registry.get_model(provider, model_id)
            input_cost = (prompt_tokens / 1_000_000.0) * model_info.costs.input_cost_per_1m
            output_cost = (
                completion_tokens / 1_000_000.0
            ) * model_info.costs.output_cost_per_1m
            return round(input_cost + output_cost, 6)
        except Exception:
            return 0.0

    def calculate_embedding_cost(self, provider: str, model_id: str, tokens: int) -> float:
        try:
            model_info = self._registry.get_model(provider, model_id)
            cost = (tokens / 1_000_000.0) * model_info.costs.input_cost_per_1m
            return round(cost, 6)
        except Exception:
            return 0.0
