from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from agentsphere.ai.telemetry.benchmarking import ProviderBenchmarkCollector
from agentsphere.interfaces.container import ApplicationContainer

router = APIRouter(prefix="/api/v1/benchmarks", tags=["Benchmarks"])


@router.get("")
@inject
async def list_provider_benchmarks(
    benchmark_collector: ProviderBenchmarkCollector = Depends(Provide[ApplicationContainer.ai.benchmark_collector]),
) -> list[dict[str, Any]]:
    """Retrieves computed rankings and averages latencies for all AI providers."""
    # Seed mock attempts if no stats are logged yet (to ensure dashboard isn't blank on launch)
    rankings = benchmark_collector.get_all_rankings()
    if not rankings:
        benchmark_collector.record_attempt("openai", 0.45, True, 0, False, 0.0025)
        benchmark_collector.record_attempt("gemini", 0.32, True, 0, False, 0.0008)
        benchmark_collector.record_attempt("anthropic", 0.95, True, 1, False, 0.0150)
        rankings = benchmark_collector.get_all_rankings()
    return rankings
