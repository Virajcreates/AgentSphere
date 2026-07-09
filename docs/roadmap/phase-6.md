# Phase 6 — Observability & Production Hardening

## Objectives

Production-harden the platform with comprehensive observability: structured logging, distributed tracing, performance metrics, dashboards, audit trails, and rate limiting. Ensure the platform is deployable, monitorable, and debuggable in production.

## Deliverables

| Deliverable | Description |
|-------------|-------------|
| OpenTelemetry Integration | Automatic instrumentation for FastAPI, PostgreSQL, Redis, httpx |
| Span Attributes | `tenant_id`, `conversation_id`, `user_id`, `model`, `tokens` on all spans |
| Span Exporters | OTLP exporter to Jaeger (dev) and Grafana Tempo (prod) |
| Prometheus Metrics Endpoint | `/metrics` with counters, histograms, gauges |
| Key Metrics | `requests_total`, `tokens_consumed_total`, `tool_calls_total` (counters); `request_duration_seconds`, `ai_latency_seconds`, `db_query_duration_seconds` (histograms); `active_conversations`, `queue_depth`, `cache_hit_rate` (gauges) |
| Structured Audit Logging | Immutable JSON log per mutation (conversation created, tool executed, tenant updated) |
| Rate Limiting | Token bucket per tenant per endpoint; configurable limits; Redis-backed |
| Health Checks | Liveness (`/health`), Readiness (`/ready`, checks DB + Redis), Dependency (`/healthz`, detail) |
| Graceful Shutdown | SIGTERM handling: drain connections, complete in-flight requests, flush logs |
| LangSmith Tracing | Optional LangSmith integration for LLM call debugging |
| Log Aggregation Config | Example `docker-compose` with Loki + Promtail or Vector |
| Grafana Dashboards | Dashboard JSON exports: API Health, AI Performance, Tenant Usage, System Health |
| Load Testing | `locustfile.py` for chat conversation load testing |
| Unit Tests | Metrics collection, health check logic, rate limiter |

## Dependencies

- Phase 1 (API, DB, middleware)
- `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`
- `prometheus-client`
- `locust` (dev dependency for load testing)
- Loki/Grafana or equivalent (deployment dependency)

## Risks

| Risk | Mitigation |
|------|------------|
| OpenTelemetry overhead | Sample traces in production (1/10 requests); ERROR traces always captured |
| Prometheus metrics cardinality explosion | Limit label cardinality; use `buckets` not unique label values |
| Rate limiting false positives | Use sliding window, not fixed window; emit headers for remaining quota |
| Log volume | Structured JSON with sampling; INFO for normal, DEBUG incrementally |

## Acceptance Criteria

- [ ] `/metrics` returns Prometheus-formatted metrics
- [ ] Spans are exported to Jaeger with correct attributes
- [ ] Rate limiter allows requests within limit and blocks when exceeded
- [ ] Rate limiter emits `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers
- [ ] Graceful shutdown completes active requests within timeout (30s)
- [ ] All mutations produce an audit log entry
- [ ] Grafana dashboards display real-time metrics
- [ ] Load test handles 100 concurrent chat sessions without errors