# Phase 7 — Background Workers & Caching

## Objectives

Introduce async background processing for embedding generation, document ingestion, analytics aggregation, and notifications. Implement caching layers for conversations, embeddings, and tools.

## Deliverables

| Deliverable | Description |
|-------------|-------------|
| Celery + Redis Setup | Task queue configuration; worker pool configuration |
| Embedding Generation Worker | Async embeddings for newly ingested documents; batch processing |
| Document Ingestion Worker | Parse → chunk → embed pipeline as a background task |
| Analytics Aggregation Worker | Hourly/daily aggregation of conversation metrics |
| Notification Worker | Webhook delivery, email dispatch for passive notifications |
| Periodic Job Scheduler | Celery Beat for scheduled jobs (expired session cleanup, usage rollups) |
| Conversation Cache | Redis cache for last N messages per conversation (TTL: 24h) |
| Embedding Cache | Redis cache for frequent query embeddings (TTL: 1h) |
| Tool Cache | Cache for idempotent tool results (e.g., product catalog, inventory) |
| Cache Warming | Prime cache for popular queries on deployment |
| Worker Monitoring | Prometheus metrics per queue; health check per worker type |
| Unit Tests | Worker tasks, cache operations, scheduler configuration |
| Integration Tests | End-to-end document → embed → search with async pipeline |

## Dependencies

- Phase 1 (Redis)
- Phase 3 (RAG pipeline)
- Phase 6 (observability, metrics)
- `celery`, `celery-beat`
- Redis 7+

## Risks

| Risk | Mitigation |
|------|------------|
| Queue backlog under load | Monitor queue depth (Prometheus); auto-scale workers based on depth |
| Stale cache | Appropriate TTLs; invalidation on document/tool updates |
| Worker crashes impacting DB | Use Redis as broker + result backend; retry with backoff |
| Embedding job ordering | Process documents in FIFO order within tenant; prevent concurrent tenant processing |

## Acceptance Criteria

- [ ] Uploading a document triggers an async embedding job
- [ ] Embedding job completes and chunks are searchable within 30s
- [ ] Conversation cache returns last N messages under 5ms
- [ ] Embedding cache returns cached embedding under 2ms
- [ ] Cache is invalidated when documents are updated or deleted
- [ ] Analytics worker generates daily aggregation within configured window
- [ ] Celery Beat triggers periodic cleanup of expired sessions
- [ ] Queue depth metric is exposed in Prometheus
- [ ] Worker crash does not lose tasks (tasks are retried)