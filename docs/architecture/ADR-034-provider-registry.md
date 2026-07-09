# ADR-034: Provider Registry

## Status
Accepted

## Context
Each AI provider exposes different APIs, parameters, and formats for completions, streaming, and metadata. We must prevent provider-specific libraries and SDK leakages from contaminating our core architecture.

## Decision
We establish a clean "Adapter and Port Pattern" for AI Providers.
* **Ports (Interfaces):** We define purely async Python Protocols (`LLMProvider`, `EmbeddingProvider`, `STTProvider`, `TTSProvider`, `ImageProvider`) under `ai/interfaces/providers.py`.
* **Adapters:** Concrete implementations (e.g. `OpenAIProvider`, `GeminiProvider`) inherit from a unified `BaseProviderAdapter` and conform to the appropriate protocol.
* **Interchangeable Bindings:** The core application layer never imports concrete providers directly. They are instantiated by the Composition Root (`interfaces/container.py`) and dynamically registered with the Gateway.

## Consequences
* **Pros:** Standardizes client contracts, simplifies mock setup for testing, and makes it incredibly straightforward to support new vendors.
* **Cons:** Requires a boilerplate translation step inside each adapter to map provider payloads to our internal schema formats.
