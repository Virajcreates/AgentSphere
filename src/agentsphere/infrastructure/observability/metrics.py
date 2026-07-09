from fastapi import FastAPI
from prometheus_client import Counter, Gauge, Histogram, make_asgi_app

HTTP_REQUESTS_TOTAL = Counter(
    "agentsphere_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

HTTP_REQUEST_DURATION = Histogram(
    "agentsphere_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
)

ACTIVE_CONVERSATIONS = Gauge(
    "agentsphere_active_conversations",
    "Currently active conversations",
)


def mount_metrics_endpoint(app: FastAPI) -> None:
    app.mount("/metrics", make_asgi_app())
