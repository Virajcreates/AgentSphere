# ADR-037: Circuit Breaker

## Status
Accepted

## Context
When an AI provider experiences rate-limiting, degradation, or complete outages, sending more requests is wasteful, slows down the user experience with long timeouts, and degrades overall application performance.

## Decision
We implement a highly reliable in-memory `CircuitBreaker` module per provider:
* **State Machine:** Governs transitions across `CLOSED` (healthy), `OPEN` (tripped/failing), and `HALF_OPEN` (cooldown testing) states.
* **Failure Threshold:** If a provider encounters `3` consecutive transient failures, its circuit trips to `OPEN`.
* **Rejection:** While `OPEN`, all requests to this provider are instantly rejected with a `CircuitBreakerOpenError` containing cooldown metrics.
* **Recovery:** After a `cooldown_period` of `10.0` seconds, the circuit enters `HALF_OPEN`. If `2` consecutive successes occur, it closes again. If any failure happens, it immediately trips back to `OPEN`.

## Consequences
* **Pros:** Fast failure, protects system resources, isolates degradations, and improves user experience by quickly falling over to alternative routes.
* **Cons:** State is in-memory; scaling horizontally might benefit from a shared Redis state in future stages.
