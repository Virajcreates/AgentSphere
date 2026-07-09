# ADR-038: Retry Policy

## Status
Accepted

## Context
Transient network resets, intermittent timeouts, and temporary rate-limiting (status 429) are common when dealing with cloud-hosted AI providers. Simple immediate retries often exacerbate server load.

## Decision
We implement a robust, highly customizable `RetryPolicy` class:
* **Transient Exception Isolation:** Retries are strictly reserved for transient errors: connection timeouts (`ProviderConnectionError`/`ProviderTimeoutError`), 429 rate limit statuses, and 5xx internal server errors.
* **Jittered Exponential Backoff:** The delay calculation implements the Full Jitter algorithm: `random.uniform(0, min(max_delay, base_delay * (2 ** attempt)))` to prevent thundering herd problems.
* **Orchestration Integration:** Integrates into the `AIGateway` completion flow. If a retry fails after the configured limit (`3` attempts), it exits or initiates a provider failover.

## Consequences
* **Pros:** Highly resilient, avoids overloading upstream providers during high traffic, and gracefully handles network hiccups.
* **Cons:** Introduces minor artificial delays between retries when recovery takes multiple attempts.
