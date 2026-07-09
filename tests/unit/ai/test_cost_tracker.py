import pytest

from agentsphere.ai.cost.cost_tracker import CostTracker
from agentsphere.ai.registry.model_registry import ModelRegistry


@pytest.fixture
def cost_tracker() -> CostTracker:
    registry = ModelRegistry()
    return CostTracker(model_registry=registry)


def test_completion_cost_calculation(cost_tracker: CostTracker) -> None:
    # GPT-4o input cost: $5.00/1M, output cost: $15.00/1M
    cost = cost_tracker.calculate_completion_cost("openai", "gpt-4o", 100_000, 200_000)
    # 0.1 * 5.0 + 0.2 * 15.0 = 0.5 + 3.0 = 3.5
    assert cost == 3.5

    # Returns 0.0 on error / unknown model
    assert cost_tracker.calculate_completion_cost("unknown", "invalid", 1000, 1000) == 0.0


def test_embedding_cost_calculation(cost_tracker: CostTracker) -> None:
    # text-embedding-3-small input cost: $0.02/1M
    cost = cost_tracker.calculate_embedding_cost("openai", "text-embedding-3-small", 10_000_000)
    # 10 * 0.02 = 0.2
    assert cost == 0.2

    assert cost_tracker.calculate_embedding_cost("unknown", "invalid", 1000) == 0.0
