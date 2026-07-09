import pytest

from agentsphere.ai.exceptions.base import ModelNotFoundError
from agentsphere.ai.registry.model_registry import ModelRegistry
from agentsphere.ai.schemas.models import ModelCapabilities, ModelCosts, ModelInfo


@pytest.fixture
def registry() -> ModelRegistry:
    return ModelRegistry()


def test_seed_models_exist(registry: ModelRegistry) -> None:
    models = registry.list_models()
    assert len(models) > 0

    # Verify key seeded models are present
    gpt4 = registry.get_model("openai", "gpt-4o")
    assert gpt4.display_name == "GPT-4o"
    assert gpt4.context_window == 128000
    assert gpt4.capabilities.streaming is True
    assert gpt4.capabilities.tool_calling is True

    gemini = registry.get_model("gemini", "gemini-1.5-flash")
    assert gemini.display_name == "Gemini 1.5 Flash"
    assert gemini.costs.input_cost_per_1m == 0.075


def test_register_and_retrieve_custom_model(registry: ModelRegistry) -> None:
    custom = ModelInfo(
        model_id="custom-v1",
        provider="custom_prov",
        display_name="Custom Model V1",
        context_window=2048,
        capabilities=ModelCapabilities(streaming=False, vision=False),
        costs=ModelCosts(input_cost_per_1m=1.0, output_cost_per_1m=2.0),
    )
    registry.register_model(custom)

    retrieved = registry.get_model("custom_prov", "custom-v1")
    assert retrieved.display_name == "Custom Model V1"
    assert retrieved.context_window == 2048


def test_get_model_not_found(registry: ModelRegistry) -> None:
    with pytest.raises(ModelNotFoundError):
        registry.get_model("openai", "gpt-99")


def test_get_models_by_provider(registry: ModelRegistry) -> None:
    openai_models = registry.get_models_by_provider("openai")
    assert len(openai_models) >= 2
    for m in openai_models:
        assert m.provider == "openai"


def test_get_models_with_capabilities(registry: ModelRegistry) -> None:
    vision_models = registry.get_models_with_capabilities(vision=True)
    assert len(vision_models) > 0
    for m in vision_models:
        assert m.capabilities.vision is True

    embedding_models = registry.get_models_with_capabilities(embeddings=True)
    assert len(embedding_models) > 0
    for m in embedding_models:
        assert m.capabilities.embeddings is True


def test_update_model_health_and_performance(registry: ModelRegistry) -> None:
    registry.update_model_health("openai", "gpt-4o", False)
    m = registry.get_model("openai", "gpt-4o")
    assert m.is_healthy is False

    # Perform multiple performance updates to check EMA moving average
    registry.update_model_performance("openai", "gpt-4o", 1.5, True)
    assert m.average_latency == 1.5

    registry.update_model_performance("openai", "gpt-4o", 1.0, True)
    assert m.average_latency == (1.5 * 0.9) + (1.0 * 0.1)

    # Success rate
    registry.update_model_performance("openai", "gpt-4o", 1.0, False)
    assert m.success_rate < 1.0
