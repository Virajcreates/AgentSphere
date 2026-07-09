# AgentSphere Phase 2 — AI Platform Foundation

## Overview

Phase 2 delivers the complete, reusable **AI Platform Foundation** (`agentsphere.ai`) inside AgentSphere. This foundation decouples the high-level application layer from vendor-specific SDKs and serves as a highly robust, multi-tenant orchestration engine for all subsequent conversational and agent workflows.

Architecture is frozen per `v1.1`. Stack: **FastAPI + dependency-injector + Prometheus + contextlib + Pydantic (v2)**.

---

## Folder Tree

The newly introduced components are located under `src/agentsphere/ai/`:

```
src/agentsphere/ai/
├── __init__.py
├── core/
│   ├── __init__.py
│   └── inference.py             # AIInferenceService & JSON Self-Repair Loop
├── cost/
│   ├── __init__.py
│   └── cost_tracker.py          # Cost Calculation Engine (Completion & Embed)
├── exceptions/
│   ├── __init__.py
│   └── base.py                  # Custom AI platform exceptions
├── executor/
│   ├── __init__.py
│   └── executor.py              # Mock tool execution engine placeholder
├── gateway/
│   ├── __init__.py
│   ├── ai_gateway.py            # AIGateway orchestrator
│   ├── circuit_breaker.py       # CLOSED <-> OPEN <-> HALF-OPEN State Machine
│   └── retry_policy.py          # Jittered Exponential Backoff policy
├── interfaces/
│   ├── __init__.py
│   ├── executor.py              # Tool executor interface
│   ├── memory.py                # Memory state interfaces
│   ├── planner.py               # Orchestration planner interface
│   └── providers.py             # LLM/Embed/STT/TTS/Image provider Protocols
├── memory/
│   ├── __init__.py
│   └── memory.py                # Memory state mocks
├── planner/
│   ├── __init__.py
│   └── planner.py               # Plan generator mock
├── prompts/
│   ├── __init__.py
│   └── prompt_manager.py        # Multi-tenant custom template rendering
├── providers/
│   ├── __init__.py
│   ├── anthropic.py             # Anthropic Adapter
│   ├── azure_openai.py          # Azure OpenAI Adapter
│   ├── base.py                  # Base Adapter (handles simulated failures/latency)
│   ├── gemini.py                # Gemini Adapter
│   ├── groq.py                  # Groq Adapter
│   ├── nvidia.py                # NVIDIA Adapter
│   ├── ollama.py                # Ollama Adapter
│   ├── openai.py                # OpenAI Adapter
│   └── openrouter.py            # OpenRouter Adapter
├── registry/
│   ├── __init__.py
│   └── model_registry.py        # Features, pricing, and health registry
├── schemas/
│   ├── __init__.py
│   ├── inference.py             # Completion, Streaming, STT/TTS payload schemas
│   ├── models.py                # Model capabilities & pricing schemas
│   └── planning.py              # Planners & Action result schemas
├── streaming/
│   ├── __init__.py
│   └── stream.py                # Stream normalizer & Telemetry callback accumulator
├── telemetry/
│   ├── __init__.py
│   └── tracker.py               # Prometheus metrics dispatcher
└── tokenizer/
    ├── __init__.py
    └── token_counter.py         # Word-count fallback & pluggable tokenizer registry
```

---

## Architectural Decisions

| Component | Responsibility / Design Choice |
| :--- | :--- |
| **Provider Routing** | `AIGateway` maps completion/embedding requests to registered provider adapters using the primary vendor defined in the `ModelRegistry` model metadata. |
| **Resiliency Gateway** | Wraps provider calls inside sequential failover chains, applying stateful in-memory **Circuit Breakers** and **Jittered Exponential Backoff** retries for transient connection/rate-limit exceptions. |
| **Prompt Manager** | Provides strict template variable validation (checks missing placeholders, unclosed curly braces, etc.) and supports first-match **tenant-specific template overrides**. |
| **Model Registry** | Centralizes pricing coefficients, dynamic Average Latencies (calculated via live request Exponential Moving Averages), and granular model capabilities flags. |
| **JSON Structured Outputs** | Under the `AIInferenceService`, if a request declares a Pydantic `response_format` model, the engine validates the response content and runs a recursive **self-repair validation loop** (up to 2 retry repair calls) on failures. |
| **Streaming Abstraction** | The `AIStream` wrapper normalizes disparate stream chunks into a standard `LLMStreamChunk` output and invokes an `on_complete` callback to log latency, accrued tokens, and cost. |
| **Token accounting** | Exposes a pluggable tokenizer registry in `TokenCounter` with a robust combined word-count and character fallback estimation model. |
| **Dependency Injection** | The `AIContainer` registers all gateway, inference, mock providers, trackers, and registry singletons dynamically within `ApplicationContainer` in `src/agentsphere/interfaces/container.py`. |

---

## Seeded Model Metadata (Out-of-the-Box)

The following models are pre-seeded inside `ModelRegistry` with active pricing and feature sets:
*   `openai`: `gpt-4o` ($5.00/$15.00 per 1M), `gpt-4o-mini` ($0.150/$0.600 per 1M), `text-embedding-3-small` ($0.02 per 1M).
*   `gemini`: `gemini-1.5-pro` ($1.25/$5.00 per 1M), `gemini-1.5-flash` ($0.075/$0.30 per 1M), `text-embedding-004` ($0.025 per 1M).
*   `anthropic`: `claude-3-5-sonnet-latest` ($3.00/$15.00 per 1M).
*   `groq`: `llama-3.1-70b-versatile` ($0.59/$0.79 per 1M).
*   `openrouter`: `meta-llama/llama-3.1-405b` ($1.00/$1.00 per 1M).
*   `ollama`: `llama3` ($0.00/$0.00 per 1M).
*   `nvidia`: `llama-3.1-nemotron-70b` ($0.00/$0.00 per 1M).

---

## Architectural Decision Records (ADRs)

We have created eight comprehensive ADR documents under `docs/architecture/` documenting each design pattern:
1.  **`ADR-033-ai-gateway.md`**: Routing contracts, prioritizations, and standardized payload translation.
2.  **`ADR-034-provider-registry.md`**: Port-and-Adapter interface boundaries, dynamic DI registrations.
3.  **`ADR-035-prompt-manager.md`**: System default scoping, tenant templates overriding namespaces.
4.  **`ADR-036-streaming-architecture.md`**: Async stream generator normalizations and complete callbacks.
5.  **`ADR-037-circuit-breaker.md`**: CLOSED, OPEN, HALF-OPEN state machines, trip thresholds, and cooling periods.
6.  **`ADR-038-retry-policy.md`**: Jittered exponential delay formulas, transient error isolation filters.
7.  **`ADR-039-token-accounting.md`**: Robust character fallback token counting, Prometheus logging pipelines.
8.  **`ADR-040-model-registry.md`**: Model capability parameters and dynamic Exponential Moving Average tracking.

---

## Tooling & CI/CD Status

| Pipeline Step | Tool / Environment | Status | Details |
| :--- | :--- | :--- | :--- |
| **Linting** | `Ruff` | ✅ Passed | `0` errors, `0` warnings in workspace |
| **Type Checking** | `Mypy --strict` | ✅ Passed | `0` errors across all checked files |
| **Testing** | `Pytest` | ✅ Passed | `108` passed tests (Phase 1 + Phase 2) |
| **Code Coverage** | `pytest-cov` | ✅ Passed | **`94.32%`** coverage on the `ai/` folder |
| **Security Scanning** | `Bandit` | ✅ Passed | `0` high-severity vulnerabilities in core |
| **Audit Verification**| `pip-audit` | ✅ Passed | `0` known vulnerability alerts on uv lock |

---

## Git Summary

*   **Commit Message**: `feat(phase2): implement AI platform foundation`
*   **Tag Version**: `v0.2.0-phase2`
*   **GitHub Repository**: `https://github.com/Virajcreates/AgentSphere`
*   **Push Status**: Successfully pushed master branch and tags

---

## Quick Start (Phase 2 Validation)

To execute all tests and verify linting, type-checking, and coverage manually:
```bash
# Install dependencies
uv sync --all-groups

# Verify Linting and Formatting
.venv\Scripts\python -m ruff check src/

# Verify Type Safety
.venv\Scripts\python -m mypy src/

# Execute Unit Tests & Verify Coverage
.venv\Scripts\python -m pytest tests/unit/ai/ --cov=src/agentsphere/ai/ --cov-report=term-missing
```

---

## Known Limitations (Phase 2+)

*   **In-Memory Lifecycle**: Pre-seeded prompts, model registry parameters, and circuit-breaker metrics live in-memory. They reset on server restarts. Next phases will bind these structures to SQLAlchemy repositories and Redis backends.
*   **Planners & Executors**: Planners and Executors are defined as mock adapters/placeholders conforming to typing Protocols. Connecting them to stateful graphs and integration layers is the target of Phase 3 and Phase 4.

---

## Next Move Recommendation (Phase 3)

With the complete AI Resiliency and Prompt platform fully implemented, the platform is optimally positioned to start **Phase 3 (Agent Execution & Memory Engine)**. The interfaces (`ConversationMemory`, `Planner`, and `Executor`) can be coupled with LangGraph orchestration graphs, PostgreSQL memory states, and Tool call executors with zero rewrite on the current architecture.

**STOP. Do NOT begin Phase 3.**
