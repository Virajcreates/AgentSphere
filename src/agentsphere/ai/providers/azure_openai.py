from agentsphere.ai.interfaces.providers import EmbeddingProvider, LLMProvider
from agentsphere.ai.providers.base import BaseProviderAdapter


class AzureOpenAIProvider(BaseProviderAdapter, LLMProvider, EmbeddingProvider):
    def __init__(self, error_rate: float = 0.0, simulated_latency: float = 0.05) -> None:
        super().__init__(
            provider_name="azure_openai",
            error_rate=error_rate,
            simulated_latency=simulated_latency,
        )
