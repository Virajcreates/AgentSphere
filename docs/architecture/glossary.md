# AgentSphere — Architecture Glossary

## A

**Adapter** — A software component that translates between two incompatible interfaces. In AgentSphere, business adapters implement the `IntegrationProtocol` to connect the platform to external business systems (ShoeFusion, Shopify, etc.). Each adapter maps tool calls to the specific API of the target system.

**ADR (Architecture Decision Record)** — A document that captures an important architectural decision, including its context, the decision made, and its consequences. AgentSphere maintains 32 ADRs covering every major architectural choice.

**AI Core** — See *Shared AI Core*.

**AI Evaluation Service** — A subsystem that measures conversation quality across 9 metrics: latency, prompt tokens, completion tokens, cost, hallucination score, confidence score, groundedness, safety score, and response quality. Evaluations are stored separately from conversations.

**AI Gateway** — A service between the Shared AI Core and the AI Inference Service responsible for model routing, provider failover, retry orchestration, cost optimisation, latency optimisation, and fallback strategy. The AI Core depends only on the AI Gateway, never on specific providers.

**AI Inference Service** — A service that owns prompt execution, structured output parsing, retry logic, token accounting, guardrails (PII detection, toxicity filtering, hallucination checks), and cost tracking. It sits between the AI Gateway and provider implementations.

**AI Session Recorder** — A component that captures every detail of a conversation turn (user message, intent, RAG chunks, tool calls, prompt, response, latency, errors) for debugging, replay, and evaluation. Recordings are stored in a separate `session_recording` table with a 90-day retention policy.

**API Key** — A tenant-scoped secret string used for programmatic authentication. Format: `as_live_{tenant_prefix}_{random_bytes}`. Hashed with Argon2 before storage. Supports scoped permissions, expiration, and rotation.

**API Strategy** — The routing and versioning approach for the platform's API surface: `/api/v1/` (public), `/internal/` (inter-service), `/admin/` (superadmin), `/webhooks/` (signature-verified), and `/api/v2/` (future).

## B

**Background Workers** — Asynchronous task processors (Celery workers) that handle embedding generation, document ingestion, analytics aggregation, notifications, and periodic cleanup jobs. Managed via Redis queue.

**Billing** — Subscription management, usage tracking, plan enforcement, and invoice generation. Planned for Phase 8. Includes Stripe integration (optional).

**Business Integration Layer** — The layer that communicates with external business systems through adapters. Supports multiple protocols: REST (Phase 4), MCP, GraphQL, and gRPC (future).

## C

**C4 Model** — A hierarchical modelling approach for software architecture: Context (system scope), Container (high-level technology decisions), Component (internal structure), Code (detailed implementation). AgentSphere uses Context and Container diagrams.

**Chat Transport** — The transport layer that handles web chat and WebSocket connections. Converts between WebSocket/REST messages and internal AI Core requests. Contains no business logic.

**CI/CD Quality Gates** — Automated checks enforced in the GitHub Actions pipeline: Ruff (linting), mypy --strict (typing), pytest --cov=80% (testing), pip-audit (vulnerabilities), bandit (security), gitleaks + detect-secrets (secret scanning).

**Clean Architecture** — An architectural style that separates software into concentric layers: Domain (entities, business rules), Application (use cases, ports), Infrastructure (persistence, providers, integrations), Interfaces (API, transports). Dependencies point inward — outer layers depend on inner layers, never the reverse.

**Container** — A deployable unit in the C4 model. AgentSphere containers include the Web API Gateway, Chat Transport, Voice Transport, Shared AI Core, AI Gateway, Prompt Manager, AI Inference Service, Event Bus, Integration Layer, RAG Engine, Feature Flag Service, Escalation Service, AI Evaluation Service, AI Session Recorder, Tenant Management, and Auth Service.

**Context Builder** — The third stage of the RAG pipeline. It constructs a token-budget-aware context window from reranked document chunks, including citations and separators.

**Conversation Evaluation Framework** — A future (Phase 10) capability that measures conversation quality across task completion, factual accuracy, latency, customer satisfaction, tool efficiency, and escalation quality. Uses LLM-as-judge and human raters.

## D

**Domain Events** — Significant occurrences within the platform that are published to the Event Bus for asynchronous processing. Examples: `MessageGenerated`, `ToolExecuted`, `ConversationEnded`, `DocumentIngested`, `EscalationTriggered`.

**Domain** — The innermost layer of Clean Architecture. Contains entities (Tenant, Conversation, Message, Document), value objects (TenantId, ConversationId, MessageId), and domain events. Has no dependencies on any framework or infrastructure.

## E

**Embedding** — A vector representation of a text chunk, generated by an embedding model. Used in the RAG pipeline for semantic similarity search via pgvector.

**Escalation** — The process of handing off a conversation to a human agent. AgentSphere's dedicated Escalation Service handles integrations with Slack, Email, Zendesk, Freshdesk, Webhook, and future CRMs via the Event Bus.

**Event Bus** — An asynchronous message distribution system following the `EventBus(Protocol)` port. The Shared AI Core publishes domain events; consumers handle analytics, audit logging, notifications, and background work. Implemented with Redis Streams (Phase 1), with Kafka, RabbitMQ, and NATS reserved for future.

## F

**Feature Flag Service** — A tenant-scoped capability toggle system. Flags control availability of Voice, RAG, Billing, Analytics, Knowledge Base, Evaluation, and future channels per tenant without code changes. Stored as JSONB in the `tenant` table.

**Frontend Architecture** — A feature-based React application structure with shared providers (Auth, Tenant, WebSocket, FeatureFlag). Features include chat/, voice/, knowledge/, admin/, and analytics/ — each with components, hooks, services, and types.

## G

**Guardrails** — Safety checks applied to both input (user message) and output (AI response). Include PII detection, toxicity filtering, and hallucination checks. Implemented in the AI Inference Service.

## I

**Integration Layer** — See *Business Integration Layer*.

## J

**JWT (JSON Web Token)** — The authentication mechanism. Tokens encode `user_id`, `tenant_id`, roles, and permissions. Validated by `AuthMiddleware`; the extracted `tenant_id` is propagated to downstream handlers via `request.state`.

## L

**LangGraph** — The AI workflow orchestration framework. AgentSphere defines a stateful graph with nodes for intent classification, RAG retrieval, planning, tool execution, response generation, and memory update. The graph is the single path through which all AI processing flows.

**Long-Term Memory** — User-level persistent memory stored in PostgreSQL. Retains user preferences, facts, and entity profiles indefinitely.

## M

**Memory Architecture** — A four-tier memory model: Short-Term (conversation, Redis, 24h TTL), Long-Term (user, PostgreSQL, indefinite), Conversation Summaries (PostgreSQL, hierarchical), and Semantic Memory (tenant, pgvector, indefinite).

**Multi-Tenancy** — The architectural property that each business (tenant) owns its own data in complete isolation. Enforced via: (1) all tables reference `tenant_id` as a foreign key, (2) Row-Level Security (RLS) policies, (3) application-level middleware that prevents cross-tenant access.

## P

**pgvector** — A PostgreSQL extension for vector similarity search. Used by the RAG Engine for embedding storage and retrieval and by Semantic Memory for storing learned patterns.

**Pipecat** — A Python framework for building voice AI pipelines. In AgentSphere, Pipecat handles ONLY audio pipeline orchestration (Audio Input → VAD → STT → AI Core → TTS → Audio Output). All business logic resides in the Shared AI Core — Pipecat never contains business logic.

**Prompt Manager** — A service responsible for the full prompt lifecycle: system prompts, tenant-specific overrides, Jinja2 template management, versioning, variable resolution, rendering, and caching.

**Provider Abstraction** — The use of Python `Protocol` classes to define interfaces for external services. AgentSphere defines ports for LLM, Embedding, Reranker, STT, TTS, Vector Store, Cache, and Business Adapters. The Shared AI Core never depends directly on any provider implementation.

## R

**RAG (Retrieval-Augmented Generation)** — A pipeline that augments LLM responses with retrieved context. AgentSphere implements five stages: Query → Retriever (vector + keyword hybrid) → Reranker (cross-encoder) → Context Builder (token budget, citations) → LLM.

**Redis** — Used for multiple purposes: conversation cache (TTL), embedding cache (TTL), rate limiting counters, WebSocket session storage, and Event Bus streaming (via Redis Streams).

**Reranker** — The second stage of the RAG pipeline. A cross-encoder model that re-evaluates and re-scores retrieved chunks to improve precision before context building.

**Retriever** — The first stage of the RAG pipeline. Combines vector similarity search (pgvector) with keyword search (PostgreSQL `tsvector`) using weighted fusion.

**RLS (Row-Level Security)** — A PostgreSQL feature that automatically filters rows based on the current session's `tenant_id`. Used as a defense-in-depth layer alongside application-level tenant scoping.

## S

**Semantic Memory** — A tenant-level memory store using pgvector for similarity search. Stores learned patterns, successful resolutions, and frequently asked questions for retrieval during future conversations.

**Shared AI Core** — The central orchestration layer built on LangGraph. Owns intent classification, planning, tool selection, tool execution, memory management, RAG retrieval, response generation, and escalation. Every transport (chat, voice, future) calls exactly this same AI Core — no duplicate business logic anywhere.

**Short-Term Memory** — Conversation-level memory stored in Redis with a 24-hour TTL. Stores the last N messages for immediate context.

**ShoeFusion** — A demonstration tenant for the AgentSphere platform. A fictitious e-commerce shoe brand with a REST API that provides product, order, customer, and inventory data. The platform never accesses ShoeFusion's database directly — only through its REST API.

**STT (Speech-to-Text)** — A voice provider that converts audio speech into text. Deepgram is the initial implementation, with AssemblyAI and Whisper reserved.

## T

**Tenant Identity Resolution** — A security rule: tenant identity MUST always be extracted from validated authentication middleware (JWT or API Key), never from client-supplied request payloads. The middleware order is critical: AuthMiddleware → TenantMiddleware → RateLimitMiddleware → RBACMiddleware.

**Tool** — A first-class code artifact that implements a specific capability a business system exposes. Tools are defined as versioned Python classes with Pydantic input/output schemas. Only tool execution history (parameters, results, timestamps) is persisted — tool definitions are never stored as data.

**Tool Registry** — A registry that maps tool names to versioned implementations. Supports `get_latest()` and `get_version()`. Tenants can pin specific tool versions in their configuration.

**TTS (Text-to-Speech)** — A voice provider abstraction that converts text response to audio speech. ElevenLabs is the initial implementation, with Cartesia and OpenAI TTS reserved.

**Transport Layer** — The outermost layer of the architecture. Responsible ONLY for converting between external communication protocols (HTTP, WebSocket, WebRTC, WhatsApp, Slack, Teams, Discord, Email) and internal AI Core requests. Contains zero business logic.

## V

**Vector Store** — A storage system for vector embeddings and similarity search. Implemented using pgvector within PostgreSQL for unified operational model and tenant-scoped queries.

**Voice Transport** — The Pipecat-based transport layer that handles voice call lifecycle: call initiation, WebRTC media handling, audio streaming, turn processing, and call termination.

## W

**Web API Gateway** — The entry point for all HTTP and WebSocket traffic. Handles authentication, rate limiting, tenant routing, request validation, and request forwarding to the appropriate transport layer.

**WebSocket Transport** — Real-time bidirectional communication for web chat. The WebSocket handler manages connections, heartbeats, streaming responses, and typing indicators. Uses the same Shared AI Core as all other transports.