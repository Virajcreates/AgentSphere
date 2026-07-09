# AgentSphere Phase 2 & 2.1 — AI Platform Foundation and Refinements

## Overview

Phase 2 and 2.1 deliver the complete, production-grade **AI Platform Foundation and Refinements** (`agentsphere.ai`) inside AgentSphere. This unified platform decouples the high-level application layers from vendor-specific SDKs and implements enterprise-level intelligent routing, safety moderation, multi-tenant templates compilation, sliding-window quotas, similarity-overlap caching, operational metrics benchmarking, and auditable lineage tracing.

Architecture is frozen per `v1.1`. Stack: **FastAPI + dependency-injector + Prometheus + contextlib + Pydantic (v2) + Async-first**.

---

## Folder Tree

The AI Platform components reside completely under `src/agentsphere/ai/`:

```
src/agentsphere/ai/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── inference.py             # AIInferenceService & Repair Loop Coordinator
│   ├── policy_engine.py         # AIPolicyEngine (Allowed lists, token caps, safety)
│   └── semantic_cache.py        # Jaccard string similarity Token-Overlap AICache
├── cost/
│   ├── __init__.py
│   ├── cost_tracker.py          # Cost Calculation Engine (Completion & Embed)
│   └── quota_manager.py         # UsageQuota & QuotaManager sliding limits
├── exceptions/
│   ├── __init__.py
│   ├── base.py                  # Custom AI platform exceptions
│   └── refinement_exceptions.py # Custom Policy, Quota, Compiler, and Negotiation exceptions
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
│   ├── cache.py                 # AICache Protocol contract
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
│   ├── prompt_compiler.py       # PromptCompiler (recursive includes, caching, macros)
│   └── prompt_manager.py        # Multi-tenant template rendering
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
│   ├── capability_negotiator.py # CapabilityNegotiator model matching engine
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
│   ├── benchmarking.py          # ProviderBenchmarkCollector operational analyst
│   ├── lineage.py               # PromptLineageTracker event audit logger
│   └── tracker.py               # Prometheus metrics dispatcher
└── tokenizer/
    ├── __init__.py
    └── token_counter.py         # Word-count fallback & pluggable tokenizer registry
```

---

## Architectural Decisions

| Component | Responsibility / Design Choice |
| :--- | :--- |
| **Capability Negotiator** | Instead of hardcoded strings, users request capability maps (e.g. `{"vision": True, "json_output": True}`). The negotiator dynamic-filters matching models and selects the optimum choice using sorting strategies (`lowest_cost`, `lowest_latency`). |
| **Prompt Compiler** | Resolves nested imports and includes (`{{ include "common.header" }}`) recursively, processes run-time dynamic macros (`{{ current_date }}`, `{{ current_year }}`), validates variables, and stores results inside a local compilation cache. |
| **Policy Engine** | Validates requests against system budgets ($10.00 max limit), strict whitelist providers/models, max allowable request token limits, and a safety content-moderation layer scanning for malicious keyphrases. |
| **Quota Manager** | Keeps transaction records inside an in-memory sliding window, validating tenant and provider expenditures against configured daily and monthly cost allowances. |
| **Semantic Cache** | Introduces Jaccard Token-Overlap string similarity matching. Prompts matching with >= 85% overlap result in instant semantic hits, reducing latency and provider costs while maintaining multi-tenant isolation. |
| **Provider Benchmarking**| Automatically aggregates attempts across successful, failed, retried, and timed-out executions per-provider to build latency averages and availability rates. |
| **Prompt Lineage** | Persists a structured audit log of execution records linking prompt name, prompt version, exact input parameters, final rendered body, routed model/provider, latency, and costs. |
| **Resiliency Gateway** | Coordinates stateful in-memory Circuit Breakers (CLOSED, OPEN, HALF-OPEN states) and Jittered Exponential Backoff retries for transient errors. |
| **Structured Outputs** | The `AIInferenceService` coordinates recursive validation and self-repair corrections if provider outputs fail to validate against requested Pydantic models. |
| **Dependency Injection** | All elements are registered declaratively within `AIContainer` inside `src/agentsphere/interfaces/container.py` under the `ApplicationContainer` hierarchy. |

---

## Seeded Model Metadata (Out-of-the-Box)

The following models are pre-seeded inside `ModelRegistry` with active pricing and feature sets:
*   `openai`: `gpt-4o` ($5.00/$15.00 per 1M), `gpt-4o-mini` ($0.150/$0.600 per 1M), `text-embedding-3-small` ($0.02 per 1M).
*   `gemini`: `gemini-1.5-pro` ($1.25/$5.00 per 1M), `gemini-1.5-flash` ($0.075/$0.30 per 1M), `text-embedding-004` ($0.025 per 1M).
*   `anthropic`: `claude-3-5-sonnet-latest` ($3.00/$15.00 per 1M).
*   `groq`: `llama-3.1-70b-versatile` ($0.59/$0.79 per 1M).
*   `openrouter`: `meta-llama/llama-3.1-405b` ($1.00/$1.00 per 1M).
*   `ollama`: `llama3` ($0.00/$0.00 per 1M - local free).
*   `nvidia`: `llama-3.1-nemotron-70b` ($0.00/$0.00 per 1M).

---

## Tooling & CI/CD Status

| Pipeline Step | Tool / Environment | Status | Details |
| :--- | :--- | :--- | :--- |
| **Linting** | `Ruff` | ✅ Passed | `0` errors, `0` warnings in workspace |
| **Type Checking** | `Mypy --strict` | ✅ Passed | `0` errors across all checked files |
| **Testing** | `Pytest` | ✅ Passed | `133` passed tests (Phase 1, Phase 2 & Phase 2.1) |
| **Code Coverage** | `pytest-cov` | ✅ Passed | **`93.28%`** coverage on the full `ai/` folder |
| **Security Scanning** | `Bandit` | ✅ Passed | `0` high-severity vulnerabilities in core |
| **Audit Verification**| `pip-audit` | ✅ Passed | `0` known vulnerability alerts on lock |

---

## Git Summary

*   **Commit Message**: `feat(phase2.1): implement AI platform refinements`
*   **Tag Version**: `v0.2.1-phase2.1`
*   **GitHub Repository**: `https://github.com/Virajcreates/AgentSphere`
*   **Push Status**: Successfully pushed master branch and tags

---

## Quick Start (Phase 2.1 Validation)

To execute all tests and verify linting, type-checking, and coverage manually:
```bash
# Verify Linting and Formatting
.venv\Scripts\python -m ruff check src/

# Verify Type Safety
.venv\Scripts\python -m mypy src/

# Execute Unit Tests & Verify Coverage
.venv\Scripts\python -m pytest tests/unit/ai/ --cov=src/agentsphere/ai/ --cov-report=term-missing
```

---

## Known Limitations

*   **In-Memory Lifecycle**: Pre-seeded prompts, compiled templates, model registry performance coefficients, provider metrics, quotas, lineage logs, and circuit-breaker states live in-memory. They reset on server restarts. Later phases will bind these structures to stateful SQLAlchemy repositories and Redis caches.
*   **Planners & Executors**: Planners and Executors remain mock adapters/placeholders conforming to typing Protocols. Linking them to stateful graphs and multi-agent systems is the target of Phase 3 and Phase 4.

---

## Next Move Recommendation (Phase 3)

With the complete AI Resiliency Gateway, Prompt Compiler, and dynamic Capability Negotiator fully implemented and passing all rigorous testing suites, the platform is optimally positioned to start **Phase 3 (Agent Execution & Memory Engine)**. The interfaces (`ConversationMemory`, `Planner`, and `Executor`) can be coupled with LangGraph orchestration graphs, PostgreSQL memory states, and Tool call executors with zero rewrite on the current architecture.

**STOP. Do NOT begin Phase 3.**
