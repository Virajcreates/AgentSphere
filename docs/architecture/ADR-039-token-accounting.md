# ADR-039: Token Accounting

## Status
Accepted

## Context
AI Platform costs are highly variable, based on tokens processed (input, cached, output, embedding). Accurate costing is critical for tenant budgeting, rate-limiting tier compliance, and commercial viability.

## Decision
We implement a pluggable, robust token accounting workflow:
* **Pluggable Tokenizer registration:** `TokenCounter` allows registration of custom model tokenizers (e.g. tiktoken).
* **Heuristic Fallback:** If a tokenizer is unavailable or not registered, a highly robust combined character (len/3.8) and regex word-count (len * 1.3) algorithm estimates token usage safely.
* **Consolidated Metric Aggregation:** The `CostTracker` fetches costs per 1M input/output/cached tokens from the `ModelRegistry` and computes costs on completions, embeddings, and completed streams.
* **Multi-dimensional Metrics:** Dispatches events to Prometheus counters (`ai_tokens_total`, `ai_cost_total`) segmented by provider and model labels.

## Consequences
* **Pros:** Highly accurate billing foundations, real-time metrics, completely pluggable for exact model tokenizers.
* **Cons:** Character/word fallbacks remain estimates (though highly accurate on test suites) if custom tokenizers are unregistered.
