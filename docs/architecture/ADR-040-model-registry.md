# ADR-040: Model Registry

## Status
Accepted

## Context
Each AI model has specific context windows, input/output costs, capability configurations (Streaming, Vision, JSON structured outputs, Tool calling), and health rates. Hardcoding this metadata across the app leads to high maintenance overhead.

## Decision
We introduce a centralized `ModelRegistry` class:
* **Rich Pydantic Schemas:** Defines `ModelCapabilities`, `ModelCosts`, and `ModelInfo` schemas.
* **Capabilities Filtering:** High level code can dynamically query the registry, e.g. "Find all available models with streaming and tool calling capability".
* **Dynamically Track performance:** The registry tracks the Exponential Moving Average (EMA) of latencies and dynamic success rates for every model based on live requests flowing through the `AIGateway`.
* **Out-of-the-Box Defaults:** Pre-seeds standard models for OpenAI, Gemini, Anthropic, Groq, OpenRouter, Azure OpenAI, Ollama, and NVIDIA.

## Consequences
* **Pros:** Dynamically tracks system performance, isolates model configurations, and simplifies dynamic model routing based on runtime features.
* **Cons:** The pre-seeded configurations are in-memory; dynamic updates reset on process restarts in Phase 2.
