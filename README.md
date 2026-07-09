# AgentSphere

**Enterprise-Grade Multi-Tenant Conversational AI Platform — Architecture Frozen v1.1**

AgentSphere is an enterprise conversational AI platform that powers intelligent customer support across multiple communication channels. Built with clean architecture principles, it provides AI-powered customer service through Web Chat, Voice Calls (Pipecat), and future channels while maintaining complete business-agnosticism through an adapter-based integration layer.

---

## Architecture Overview

```
Transport Layer (Chat / Voice / WhatsApp / Slack / Teams / Discord / Email)
       ↓
  Shared AI Core (LangGraph Workflow)
       ↓
  AI Gateway (Model Routing, Provider Failover, Cost Optimisation)
       ↓
  Prompt Manager (Templates, Versioning, Rendering, Caching)
       ↓
  AI Inference Service (Guardrails, Retries, Token Accounting, Cost Tracking)
       ↓
  AI Providers (Gemini, OpenAI, Anthropic, Azure OpenAI)
       ↑
  Event Bus(Protocol) → Analytics, Audit, Notifications, Workers
  AI Session Recorder → Full turn capture for replay/debug/evaluation
  Feature Flag System → Tenant-scoped capability gating
  Escalation Service → Slack, Email, Zendesk, Freshdesk, Webhook
  AI Evaluation Service → Latency, Cost, Hallucination, Groundedness, Safety
       ↓
  Business Integration Layer (Adapters)
       ↓
  Business Systems (ShoeFusion, Shopify, WooCommerce, etc.)
```

## Key Features

- **Multi-Tenant**: Each business owns its users, knowledge base, conversations, AI configuration, analytics, integrations, and feature flags
- **Channel Agnostic**: Web Chat, Voice (Pipecat), with WhatsApp, Slack, Teams, Discord, Email planned
- **Provider Independent**: LLM, Embedding, STT, TTS — all abstracted behind `Protocol` interfaces; AI Core never imports any provider directly
- **AI Gateway**: Model routing, provider failover, cost optimisation, latency management
- **Prompt Manager**: Versioned templates, tenant overrides, Jinja2 rendering, caching
- **RAG Pipeline**: Query → Retriever → Reranker → Context Builder → LLM
- **Agentic Workflows**: LangGraph-based intent classification, planning, tool execution, 4-tier memory management
- **Event-Driven**: `EventBus(Protocol)` with Redis Streams (Phase 1), Kafka/RabbitMQ/NATS (future)
- **AI Session Recorder**: Full turn capture including prompts, RAG chunks, tool calls, latency, errors — replayable timeline
- **Human Escalation**: Dedicated subsystem for Slack, Email, Zendesk, Freshdesk, Webhook integrations
- **AI Evaluation**: 9 metrics including hallucination, groundedness, safety, confidence, response quality
- **Enterprise Ready**: JWT auth, RBAC, tenant isolation, structured logging, OpenTelemetry, Prometheus, Grafana

## Architecture Documentation

| Document | Description |
|----------|-------------|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Complete architecture plan (31 sections, 32 ADRs, 3,000+ lines) |
| [`VALIDATION.md`](VALIDATION.md) | Architecture validation & readiness report |
| [`docs/INDEX.md`](docs/INDEX.md) | Full documentation index with ADR directory |
| [`docs/architecture/glossary.md`](docs/architecture/glossary.md) | Architectural glossary — definitions of every major concept |
| [`docs/roadmap/phase-1.md`](docs/roadmap/phase-1.md) | Phase 1 — Core Platform Infrastructure |
| [`docs/roadmap/phase-2.md`](docs/roadmap/phase-2.md) | Phase 2 — Shared AI Core — Text Chat |
| [`docs/roadmap/phase-3.md`](docs/roadmap/phase-3.md) | Phase 3 — RAG Engine & Knowledge Base |
| [`docs/roadmap/phase-4.md`](docs/roadmap/phase-4.md) | Phase 4 — Business Integration Layer |
| [`docs/roadmap/phase-5.md`](docs/roadmap/phase-5.md) | Phase 5 — Voice AI with Pipecat |
| [`docs/roadmap/phase-6.md`](docs/roadmap/phase-6.md) | Phase 6 — Observability & Production Hardening |
| [`docs/roadmap/phase-7.md`](docs/roadmap/phase-7.md) | Phase 7 — Background Workers & Caching |
| [`docs/roadmap/phase-8.md`](docs/roadmap/phase-8.md) | Phase 8 — Billing & Multi-Tenancy Features |
| [`docs/roadmap/phase-9.md`](docs/roadmap/phase-9.md) | Phase 9 — Additional Transports |
| [`docs/roadmap/phase-10.md`](docs/roadmap/phase-10.md) | Phase 10 — Advanced AI Features |

## Technology Stack

| Component | Technology |
|-----------|------------|
| API Framework | FastAPI (Python 3.11+) |
| AI Orchestration | LangGraph |
| Database | PostgreSQL + pgvector |
| Caching / Events | Redis Streams (with Kafka/RabbitMQ/NATS abstraction) |
| Voice Pipeline | Pipecat |
| LLM Providers | Gemini (initial), OpenAI, Anthropic, Azure OpenAI |
| STT Providers | Deepgram (initial), AssemblyAI |
| TTS Providers | ElevenLabs (initial), Cartesia |
| Observability | OpenTelemetry, Prometheus, Grafana, LangSmith |
| CI/CD | GitHub Actions, Ruff, mypy --strict, pytest, pip-audit, bandit, gitleaks, detect-secrets |
| Container | Docker, Kubernetes (Helm) |

## Project Structure

```
src/agentsphere/
├── domain/              # Entities, Value Objects, Domain Events
├── application/         # Use Cases, Ports (Protocols), Services
├── infrastructure/
│   ├── ai/              # Providers (gemini, openai, anthropic, azure)
│   ├── ai_gateway/      # Model routing, provider failover, cost optimiser
│   ├── prompt_manager/  # Templates, versioning, rendering, caching
│   ├── core/            # LangGraph workflow (intent, plan, tools, memory, rag, response)
│   ├── integrations/    # Adapters (shoefusion, shopify, woocommerce, custom)
│   ├── event_bus/       # Protocol + implementations (redis, kafka, rabbitmq, nats)
│   ├── escalation/      # Slack, Email, Zendesk, Freshdesk, Webhook handlers
│   ├── evaluation/      # 9 metric evaluators + store
│   ├── persistence/     # ORM, repositories, migrations
│   ├── vector_store/    # pgvector operations
│   ├── feature_flags/   # Tenant-scoped JSONB flags
│   ├── auth/            # JWT, RBAC, API keys
│   └── observability/   # Logging, tracing, metrics, session_recorder
├── interfaces/
│   ├── api/             # Routes, middleware, dependencies
│   ├── websocket/       # Chat WS handler, connection manager
│   └── voice/           # Pipecat pipeline, call handler, WebRTC
├── config/              # Pydantic Settings, Database, Logging
└── shared/              # Exceptions, utilities, constants

frontend/
├── app/                 # Root layout, pages
├── components/          # UI, layout, common components
├── features/            # chat/, voice/, knowledge/, admin/, analytics/
├── hooks/               # useAuth, useTenant, useWebSocket, useFeatureFlag
├── providers/           # Auth, Tenant, WebSocket, FeatureFlag providers
├── services/            # API clients
└── types/               # Shared TypeScript types
```

## Phase Roadmap

| Phase | Description | Status | Plan |
|-------|-------------|--------|------|
| 0 | Foundation & Architecture | ✅ Complete | — |
| 0.1 | Final Architecture Improvements | ✅ Complete | — |
| 0.2 | Documentation Finalization | ✅ Complete | — |
| 1 | Core Platform Infrastructure | ⏳ Next | [Plan](docs/roadmap/phase-1.md) |
| 2 | Shared AI Core - Text Chat | 📋 Planned | [Plan](docs/roadmap/phase-2.md) |
| 3 | RAG Engine & Knowledge Base | 📋 Planned | [Plan](docs/roadmap/phase-3.md) |
| 4 | Business Integration Layer | 📋 Planned | [Plan](docs/roadmap/phase-4.md) |
| 5 | Voice AI with Pipecat | 📋 Planned | [Plan](docs/roadmap/phase-5.md) |
| 6 | Observability & Production Hardening | 📋 Planned | [Plan](docs/roadmap/phase-6.md) |
| 7 | Background Workers & Caching | 📋 Planned | [Plan](docs/roadmap/phase-7.md) |
| 8 | Billing & Multi-tenancy Features | 📋 Planned | [Plan](docs/roadmap/phase-8.md) |
| 9 | Additional Transports | 📋 Planned | [Plan](docs/roadmap/phase-9.md) |
| 10 | Advanced AI Features + Evaluation | 📋 Planned | [Plan](docs/roadmap/phase-10.md) |

## Development

```bash
# Setup
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Quality Gates
ruff check src/
mypy --strict src/
pytest tests/ -v --cov=src --cov-fail-under=80

# Database
alembic upgrade head
```

## License

Proprietary — All rights reserved.