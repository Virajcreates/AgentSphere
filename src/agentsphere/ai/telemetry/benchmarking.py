from typing import Any


class ProviderBenchmarkMetrics:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.total_attempts: int = 0
        self.successes: int = 0
        self.failures: int = 0
        self.total_latency: float = 0.0
        self.total_retries: int = 0
        self.timeouts: int = 0
        self.total_cost: float = 0.0

    @property
    def success_rate(self) -> float:
        if self.total_attempts == 0:
            return 1.0
        return self.successes / self.total_attempts

    @property
    def average_latency(self) -> float:
        if self.successes == 0:
            return 0.0
        return self.total_latency / self.successes

    @property
    def timeout_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.timeouts / self.total_attempts

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "total_attempts": self.total_attempts,
            "success_rate": round(self.success_rate, 4),
            "average_latency_sec": round(self.average_latency, 4),
            "total_retries": self.total_retries,
            "timeout_rate": round(self.timeout_rate, 4),
            "total_cost_usd": round(self.total_cost, 6),
        }


class ProviderBenchmarkCollector:
    def __init__(self) -> None:
        self._provider_stats: dict[str, ProviderBenchmarkMetrics] = {}

    def record_attempt(
        self,
        provider: str,
        latency: float,
        success: bool,
        retries: int,
        timed_out: bool,
        cost: float,
    ) -> None:
        prov = provider.lower()
        if prov not in self._provider_stats:
            self._provider_stats[prov] = ProviderBenchmarkMetrics(prov)

        stats = self._provider_stats[prov]
        stats.total_attempts += 1
        stats.total_retries += retries
        stats.total_cost += cost

        if success:
            stats.successes += 1
            stats.total_latency += latency
        else:
            stats.failures += 1

        if timed_out:
            stats.timeouts += 1

    def get_provider_metrics(self, provider: str) -> dict[str, Any] | None:
        prov = provider.lower()
        if prov not in self._provider_stats:
            return None
        return self._provider_stats[prov].to_dict()

    def get_all_rankings(self) -> list[dict[str, Any]]:
        # Sorts providers by best performance (Success Rate desc, Average Latency asc)
        rankings = list(self._provider_stats.values())
        rankings.sort(
            key=lambda m: (-m.success_rate, m.average_latency if m.average_latency > 0 else 999.0)
        )
        return [r.to_dict() for r in rankings]
