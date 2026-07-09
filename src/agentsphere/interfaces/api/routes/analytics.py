import random
from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("")
async def get_dashboard_analytics() -> dict[str, Any]:
    """Generates structured time-series and provider logs for analytical charting."""
    # Build complete charts statistics mock payload representing live telemetry stats
    providers = ["openai", "gemini", "anthropic", "groq"]

    # 1. Timeline series (last 7 days)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    series_logs = []
    for day in days:
        series_logs.append({
            "name": day,
            "tokens": random.randint(15000, 85000),  # nosec B311
            "cost_usd": round(random.uniform(0.12, 1.85), 4),  # nosec B311
            "conversations": random.randint(5, 55),  # nosec B311
            "errors": random.randint(0, 3),  # nosec B311
        })

    # 2. Segmented provider shares
    segmented_shares = []
    for prov in providers:
        segmented_shares.append({
            "provider": prov,
            "requests": random.randint(50, 450),  # nosec B311
            "tokens": random.randint(100000, 950000),  # nosec B311
            "cost_usd": round(random.uniform(1.50, 22.45), 2),  # nosec B311
        })

    return {
        "daily_series": series_logs,
        "provider_shares": segmented_shares,
        "summary": {
            "total_tokens_processed": sum(s["tokens"] for s in series_logs),
            "total_expenses_usd": round(sum(s["cost_usd"] for s in series_logs), 4),
            "total_threads_count": sum(s["conversations"] for s in series_logs),
            "average_processing_latency_sec": 0.42,
        }
    }
