# ADR-033: AI Gateway Implementation

## Status
Accepted

## Context
AgentSphere needs to orchestrate requests to multiple independent AI providers (e.g. OpenAI, Anthropic, Gemini, etc.). Decoupling the high-level application layer from vendor-specific clients is critical for vendor independence, rate-limiting isolation, and system reliability.

## Decision
We implement a robust, centralized `AIGateway` that sits between the `AIInferenceService` and individual pluggable LLM/Embedding provider adapters. 

Key architectural components:
* **Decoupled Registration:** Adapters are dynamically bound via dependency injection using `dependency-injector` mapping `llm_providers` and `embedding_providers` dictionaries.
* **Failover Chains:** Requests can define a prioritized sequence of fallback providers (`failover_providers`). If the primary vendor fails, the gateway transparently tries the next alternative.
* **Standardized Payload Contract:** Translates multi-vendor completions and embeddings to standard models (`LLMCompletionResponse`, `EmbeddingResponse`).

## Consequences
* **Pros:** Highly resilient, simple replacement of vendors, unified location for telemetry, latency monitoring, and billing.
* **Cons:** Introduces a thin intermediary routing layer in-memory.
