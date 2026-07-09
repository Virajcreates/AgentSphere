from agentsphere.ai.exceptions.refinement_exceptions import CapabilityNegotiationError
from agentsphere.ai.registry.model_registry import ModelRegistry


class CapabilityNegotiator:
    def __init__(self, model_registry: ModelRegistry) -> None:
        self._registry = model_registry

    def negotiate_model(
        self,
        required_capabilities: dict[str, bool],
        strategy: str = "lowest_cost",
        provider: str | None = None,
    ) -> str:
        """Dynamically selects the best model ID based on required capabilities and constraints.

        :param required_capabilities: Dict of capabilities to require, e.g. {"vision": True,
            "tool_calling": True}
        :param strategy: Selection priority strategy, e.g. "lowest_cost" or "lowest_latency"
        :param provider: Optionally filter results to a specific provider
        :return: String model ID
        """
        all_models = self._registry.list_models()

        matching_models = []
        for model in all_models:
            # Check provider filter if specified
            if provider and model.provider.lower() != provider.lower():
                continue

            # Ensure model is healthy
            if not model.is_healthy:
                continue

            # Check matching capabilities
            is_match = True
            for cap, required in required_capabilities.items():
                if required:
                    # Map field names correctly to ModelCapabilities
                    field_name = cap
                    if cap == "json_output":
                        field_name = "json_mode"

                    if not getattr(model.capabilities, field_name, False):
                        is_match = False
                        break

            if is_match:
                matching_models.append(model)

        if not matching_models:
            caps_str = ", ".join(f"{k}={v}" for k, v in required_capabilities.items() if v)
            raise CapabilityNegotiationError(
                f"No healthy model found satisfying capabilities: {caps_str}"
            )

        # Apply selection strategy
        if strategy == "lowest_latency":
            # Sort by dynamic latency ascending.
            # Unprofiled models (average_latency == 0.0) are placed last.
            matching_models.sort(
                key=lambda m: m.average_latency if m.average_latency > 0.0 else 999.0
            )
        else:
            # Default: lowest_cost (sort by input cost per 1M descending)
            matching_models.sort(key=lambda m: m.costs.input_cost_per_1m)

        return matching_models[0].model_id
