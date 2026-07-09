# AgentSphere — Documentation Index

## Core Documents

| Document | Description | Location |
|----------|-------------|----------|
| **Architecture Plan** | Complete architecture: 31 sections, 32 ADRs, C4 diagrams, sequence diagrams, ER diagram, folder structure | [`ARCHITECTURE.md`](../ARCHITECTURE.md) |
| **Architecture Validation Report** | Validation of all 30 components, 7 architectural rules, 32 ADRs | [`VALIDATION.md`](../VALIDATION.md) |
| **README** | Project overview, architecture flow, tech stack, quick start | [`README.md`](../README.md) |
| **Glossary** | Definitions of every major architectural concept | [`docs/architecture/glossary.md`](../docs/architecture/glossary.md) |

## Roadmap

| Document | Description |
|----------|-------------|
| Phase 1 — Core Platform Infrastructure | [`docs/roadmap/phase-1.md`](roadmap/phase-1.md) |
| Phase 2 — Shared AI Core — Text Chat | [`docs/roadmap/phase-2.md`](roadmap/phase-2.md) |
| Phase 3 — RAG Engine & Knowledge Base | [`docs/roadmap/phase-3.md`](roadmap/phase-3.md) |
| Phase 4 — Business Integration Layer | [`docs/roadmap/phase-4.md`](roadmap/phase-4.md) |
| Phase 5 — Voice AI with Pipecat | [`docs/roadmap/phase-5.md`](roadmap/phase-5.md) |
| Phase 6 — Observability & Production Hardening | [`docs/roadmap/phase-6.md`](roadmap/phase-6.md) |
| Phase 7 — Background Workers & Caching | [`docs/roadmap/phase-7.md`](roadmap/phase-7.md) |
| Phase 8 — Billing & Multi-Tenancy Features | [`docs/roadmap/phase-8.md`](roadmap/phase-8.md) |
| Phase 9 — Additional Transports | [`docs/roadmap/phase-9.md`](roadmap/phase-9.md) |
| Phase 10 — Advanced AI Features | [`docs/roadmap/phase-10.md`](roadmap/phase-10.md) |

## Architecture Diagrams

| Diagram | Description | Section |
|---------|-------------|---------|
| C4 Context Diagram | System boundary, actors, external systems | [`ARCHITECTURE.md §1`](../ARCHITECTURE.md#1-c4-context-diagram) |
| C4 Container Diagram | Containers, relationships, technology choices | [`ARCHITECTURE.md §2`](../ARCHITECTURE.md#2-c4-container-diagram) |
| C4 Container Descriptions | 19 containers with technology and responsibility | [`ARCHITECTURE.md §2`](../ARCHITECTURE.md#2-c4-container-diagram) |
| Sequence Diagram — Chat | Web chat message flow (AI Gateway, Prompt Manager, Session Recorder) | [`ARCHITECTURE.md §3.1`](../ARCHITECTURE.md#31-web-chat-message-flow) |
| Sequence Diagram — Voice | Pipecat voice call flow | [`ARCHITECTURE.md §3.2`](../ARCHITECTURE.md#32-voice-call-flow-pipecat-integration) |
| Sequence Diagram — Document Ingestion | RAG document pipeline | [`ARCHITECTURE.md §3.3`](../ARCHITECTURE.md#33-document-ingestion-flow-rag) |
| Sequence Diagram — Tool Execution | Tool call through adapter to business system | [`ARCHITECTURE.md §3.4`](../ARCHITECTURE.md#34-tool-execution-flow) |
| Sequence Diagram — Event Bus | Async event processing flow | [`ARCHITECTURE.md §3.5`](../ARCHITECTURE.md#35-event-bus-flow-domain-events) |
| ER Diagram | 11 tables with relationships and fields | [`ARCHITECTURE.md §4`](../ARCHITECTURE.md#4-er-diagram) |
| LangGraph Workflow | State schema, graph nodes, routing edges | [`ARCHITECTURE.md §8`](../ARCHITECTURE.md#8-ai-workflow-langgraph) |
| Pipecat Integration | Voice pipeline architecture | [`ARCHITECTURE.md §9`](../ARCHITECTURE.md#9-pipecat-integration-diagram) |
| ShoeFusion Integration | Adapter pattern, API contract, tools | [`ARCHITECTURE.md §10`](../ARCHITECTURE.md#10-shoefusion-integration-diagram) |
| Memory Flow | 4-tier memory in LangGraph | [`ARCHITECTURE.md §14.3`](../ARCHITECTURE.md#143-memory-flow-in-langgraph) |
| RAG Pipeline Stages | Query → Retriever → Reranker → Context Builder → LLM | [`ARCHITECTURE.md §15.1`](../ARCHITECTURE.md#151-pipeline-stages) |
| Event Bus Flow | Domain events through Redis Streams | [`ARCHITECTURE.md §13.4`](../ARCHITECTURE.md#134-event-flow) |
| Escalation Flow | Escalation via Slack, Zendesk | [`ARCHITECTURE.md §19.2`](../ARCHITECTURE.md#192-flow) |
| Deployment Architecture | Load balancer, API/voice/worker tiers, data tier | [`ARCHITECTURE.md §29`](../ARCHITECTURE.md#29-deployment-architecture) |

## ADR Index

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Clean Architecture | ✅ |
| ADR-002 | FastAPI | ✅ |
| ADR-003 | PostgreSQL + pgvector | ✅ |
| ADR-004 | Pipecat Voice Architecture | ✅ |
| ADR-005 | Provider Abstractions | ✅ |
| ADR-006 | Multi-Tenancy | ✅ |
| ADR-007 | LangGraph | ✅ |
| ADR-008 | Redis Strategy | ✅ |
| ADR-009 | Event Bus | ✅ |
| ADR-010 | AI Inference Service | ✅ |
| ADR-011 | AI Provider Independence | ✅ |
| ADR-012 | Async-First Architecture | ✅ |
| ADR-013 | Structured Logging with Correlation IDs | ✅ |
| ADR-014 | Configuration via Pydantic Settings | ✅ |
| ADR-015 | Tool Definitions as Code | ✅ |
| ADR-016 | Four-Tier Memory Architecture | ✅ |
| ADR-017 | RAG Pipeline as Discrete Stages | ✅ |
| ADR-018 | Trusted Tenant Resolution Only | ✅ |
| ADR-019 | Versioned Tool Definitions | ✅ |
| ADR-020 | Structured Tool Errors with Idempotency | ✅ |
| ADR-021 | Comprehensive CI/CD Quality Gates | ✅ |
| ADR-022 | Prompt Manager | ✅ |
| ADR-023 | AI Gateway | ✅ |
| ADR-024 | EventBus Abstraction | ✅ |
| ADR-025 | Versioned Tool Registry | ✅ |
| ADR-026 | AI Evaluation | ✅ |
| ADR-027 | Feature Flags | ✅ |
| ADR-028 | Human Escalation | ✅ |
| ADR-029 | API Strategy | ✅ |
| ADR-030 | Frontend Architecture | ✅ |
| ADR-031 | AI Session Recorder | ✅ |
| ADR-032 | API First Development | ✅ |

## Directory Structure

```
docs/
├── INDEX.md                          ← This file
├── architecture/
│   └── glossary.md                   ← Architectural glossary
└── roadmap/
    ├── phase-1.md                    Core Platform Infrastructure
    ├── phase-2.md                    Shared AI Core — Text Chat
    ├── phase-3.md                    RAG Engine & Knowledge Base
    ├── phase-4.md                    Business Integration Layer
    ├── phase-5.md                    Voice AI with Pipecat
    ├── phase-6.md                    Observability & Production Hardening
    ├── phase-7.md                    Background Workers & Caching
    ├── phase-8.md                    Billing & Multi-Tenancy Features
    ├── phase-9.md                    Additional Transports
    └── phase-10.md                   Advanced AI Features
```