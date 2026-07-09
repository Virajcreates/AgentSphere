import pytest

from agentsphere.ai.telemetry.benchmarking import ProviderBenchmarkCollector


@pytest.fixture
def collector() -> ProviderBenchmarkCollector:
    return ProviderBenchmarkCollector()


def test_record_attempts_and_rankings(collector: ProviderBenchmarkCollector) -> None:
    # Record some trials for openai
    collector.record_attempt(
        provider="openai", latency=0.5, success=True, retries=0, timed_out=False, cost=0.005
    )
    collector.record_attempt(
        provider="openai", latency=0.7, success=True, retries=1, timed_out=False, cost=0.005
    )

    # Record some trials for gemini (faster, zero retries!)
    collector.record_attempt(
        provider="gemini", latency=0.2, success=True, retries=0, timed_out=False, cost=0.001
    )

    # Record some trials for anthropic (one timeout, one success)
    collector.record_attempt(
        provider="anthropic", latency=0.0, success=False, retries=0, timed_out=True, cost=0.0
    )
    collector.record_attempt(
        provider="anthropic", latency=1.5, success=True, retries=0, timed_out=False, cost=0.01
    )

    # 1. Inspect openai metrics
    openai_metrics = collector.get_provider_metrics("openai")
    assert openai_metrics is not None
    assert openai_metrics["total_attempts"] == 2
    assert openai_metrics["success_rate"] == 1.0
    assert openai_metrics["average_latency_sec"] == 0.6
    assert openai_metrics["total_retries"] == 1
    assert openai_metrics["timeout_rate"] == 0.0
    assert openai_metrics["total_cost_usd"] == 0.01

    # 2. Inspect anthropic metrics
    anthropic_metrics = collector.get_provider_metrics("anthropic")
    assert anthropic_metrics is not None
    assert anthropic_metrics["total_attempts"] == 2
    assert anthropic_metrics["success_rate"] == 0.5
    assert anthropic_metrics["timeout_rate"] == 0.5
    assert anthropic_metrics["average_latency_sec"] == 1.5

    # 3. Inspect global rankings order
    # Gemini (success=1.0, latency=0.2) > OpenAI (success=1.0, latency=0.6) > Anthropic (success=0.5)
    rankings = collector.get_all_rankings()
    assert len(rankings) == 3
    assert rankings[0]["provider"] == "gemini"
    assert rankings[1]["provider"] == "openai"
    assert rankings[2]["provider"] == "anthropic"
