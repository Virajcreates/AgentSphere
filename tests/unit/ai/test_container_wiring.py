import pytest

from agentsphere.ai.core.inference import AIInferenceService
from agentsphere.ai.gateway.ai_gateway import AIGateway
from agentsphere.ai.prompts.prompt_manager import PromptManager
from agentsphere.ai.registry.model_registry import ModelRegistry
from agentsphere.interfaces.container import ApplicationContainer, init_container


@pytest.fixture
def container() -> ApplicationContainer:
    return init_container()


def test_ai_container_resolves_all_components(container: ApplicationContainer) -> None:
    # 1. Core singletons
    assert isinstance(container.ai.model_registry(), ModelRegistry)
    assert isinstance(container.ai.prompt_manager(), PromptManager)

    # 2. Resiliency Gateway
    gw = container.ai.gateway()
    assert isinstance(gw, AIGateway)

    # Verify providers are wired dynamically into the gateway
    assert "openai" in gw._llm_providers
    assert "gemini" in gw._llm_providers
    assert "anthropic" in gw._llm_providers

    assert "openai" in gw._embedding_providers
    assert "gemini" in gw._embedding_providers

    # 3. High level Inference Service
    inf = container.ai.inference()
    assert isinstance(inf, AIInferenceService)
    assert inf.gateway is gw


def test_all_providers_resolve_successfully(container: ApplicationContainer) -> None:
    assert container.ai.openai_provider() is not None
    assert container.ai.gemini_provider() is not None
    assert container.ai.anthropic_provider() is not None
    assert container.ai.openrouter_provider() is not None
    assert container.ai.groq_provider() is not None
    assert container.ai.azure_openai_provider() is not None
    assert container.ai.ollama_provider() is not None
    assert container.ai.nvidia_provider() is not None
