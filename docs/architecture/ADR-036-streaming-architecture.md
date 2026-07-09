# ADR-036: Streaming Architecture

## Status
Accepted

## Context
Streaming token completions directly to users reduces perceived latency and is the core UX pattern of conversational interfaces. Each vendor client returns their own iterator and payload structure.

## Decision
We implement a unified, standard stream wrapper named `AIStream`.
*   **Encapsulated Generator:** Takes a provider-specific async generator of chunks and normalizes them into unified `LLMStreamChunk` schemas.
*   **On-Complete Callback Hooks:** Since streaming happens asynchronously and finishes at a later time, `AIStream` supports a callback `on_complete` that passes aggregated metrics (total streaming text, cumulative tokens, latency, cost) to the telemetry and gateway modules once the iterator exits or is cancelled.
*   **Decoupled Consumption:** The upper API layers consume the `AIStream` generator directly without needing to know which provider produced it.

## Consequences
* **Pros:** Highly polished streaming experience, zero vendor leakage, and guaranteed token/latency telemetry tracking.
* **Cons:** Allocates moderate memory for string accumulation during the lifecycle of the stream in order to log the final completed completion.
