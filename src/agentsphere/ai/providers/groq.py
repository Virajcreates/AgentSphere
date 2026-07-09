from agentsphere.ai.interfaces.providers import LLMProvider
from agentsphere.ai.providers.base import BaseProviderAdapter


class GroqProvider(BaseProviderAdapter, LLMProvider):
    def __init__(self, error_rate: float = 0.0, simulated_latency: float = 0.05) -> None:
        super().__init__(
            provider_name="groq",
            error_rate=error_rate,
            simulated_latency=simulated_latency,
        )
