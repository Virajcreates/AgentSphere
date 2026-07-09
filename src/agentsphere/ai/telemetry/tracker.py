import structlog
from prometheus_client import Counter, Histogram

logger = structlog.get_logger(__name__)

# Define Prometheus metrics (avoid re-defining if already defined)
LATENCY_HIST = Histogram(
    "ai_request_latency_seconds",
    "Latency of AI provider requests in seconds",
    ["provider", "model", "operation"],
)
TOKENS_COUNTER = Counter(
    "ai_tokens_total",
    "Total tokens consumed by AI requests",
    ["provider", "model", "type"],
)
COST_COUNTER = Counter(
    "ai_cost_total",
    "Total accumulated cost of AI requests in USD",
    ["provider", "model"],
)
ERRORS_COUNTER = Counter(
    "ai_request_errors_total",
    "Total failed AI provider requests",
    ["provider", "model", "error_type"],
)


class TelemetryTracker:
    def track_request(
        self,
        provider: str,
        model: str,
        operation: str,
        latency: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cached_tokens: int = 0,
        cost: float = 0.0,
    ) -> None:
        LATENCY_HIST.labels(
            provider=provider.lower(), model=model.lower(), operation=operation
        ).observe(latency)

        if prompt_tokens > 0:
            TOKENS_COUNTER.labels(
                provider=provider.lower(), model=model.lower(), type="prompt"
            ).inc(prompt_tokens)
        if completion_tokens > 0:
            TOKENS_COUNTER.labels(
                provider=provider.lower(), model=model.lower(), type="completion"
            ).inc(completion_tokens)
        if cached_tokens > 0:
            TOKENS_COUNTER.labels(
                provider=provider.lower(), model=model.lower(), type="cached"
            ).inc(cached_tokens)

        if cost > 0.0:
            COST_COUNTER.labels(provider=provider.lower(), model=model.lower()).inc(cost)

        logger.info(
            "AI Request Completed",
            provider=provider,
            model=model,
            operation=operation,
            latency=latency,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
        )

    def track_error(
        self, provider: str, model: str, operation: str, error_type: str, latency: float = 0.0
    ) -> None:
        ERRORS_COUNTER.labels(
            provider=provider.lower(), model=model.lower(), error_type=error_type
        ).inc()

        logger.error(
            "AI Request Failed",
            provider=provider,
            model=model,
            operation=operation,
            error_type=error_type,
            latency=latency,
        )
