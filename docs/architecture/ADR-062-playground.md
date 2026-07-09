# ADR-062: Playground

## Status
Accepted

## Context
Developers and operators need a safe, standalone sandbox to write, iterate, and verify dynamic completions streams across multi-provider endpoints (OpenAI, Gemini, Anthropic, Groq) with full latency and billing telemetry insights.

## Decision
We implement a highly cohesive **Playground Arena**:
* **Standalone Completing Canvas:** Renders a large text canvas displaying token output streams, plotting incremental results without affecting main chat databases.
* **Granular Telemetry Panel:** Details dynamic parameters matching each completion: the routed provider/model, latency duration, token metrics counts, request Trace IDs, and the raw returned JSON string.

## Consequences
* **Pros:** Highly responsive, secure multi-model prompt testing, and complete pricing observability.
* **Cons:** Requires a mock generator framework to simulate streaming behaviors during sandboxed trials.
