# Phase 2 — Shared AI Core — Text Chat

## Objectives

Implement the LangGraph-based Shared AI Core with provider abstractions, WebSocket chat transport, intent classification, RAG retrieval, tool execution, memory management, and response generation. Deliver a working text chat experience with ShoeFusion integration ready in Phase 4.

## Deliverables

| Deliverable | Description |
|-------------|-------------|
| LLM Provider Port | `LLMProvider(Protocol)` — async `complete()` and `complete_structured()` |
| Gemini LLM Provider | Implementation using `google-genai` SDK |
| Embedding Provider Port | `EmbeddingProvider(Protocol)` — async `embed()` and `embed_batch()` |
| Gemini Embedding Provider | Implementation using Gemini embedding models |
| Reranker Provider Port | `Reranker(Protocol)` — async `rerank()` |
| LangGraph Workflow | State schema, nodes (intent, retrieve, plan, execute, generate, remember), edges |
| Intent Classification Node | LLM-based classification with few-shot examples; returns structured intent |
| RAG Retrieval Node | Calls RAG Engine for tenant-scoped vector search |
| Planning Node | LLM selects tools based on intent and context |
| Tool Execution Node | Executes tools via integration layer (stub until Phase 4) |
| Response Generation Node | LLM generates final response with context, tool results, history |
| Memory Update Node | Extracts facts, updates short-term and long-term memory |
| Escalation Node | Triggers `EscalationTriggered` event when confidence is low |
| WebSocket Chat Transport | `wss://` endpoint for real-time chat with session management |
| REST Chat Transport | `POST /api/v1/conversations/{id}/messages` for synchronous chat |
| Message Persistence | Store messages in PostgreSQL (role, content, metadata) |
| Conversation Management | Start, list, get, close conversations |
| Unit Tests | All nodes, state transitions, provider abstractions, transport handlers |
| Integration Tests | End-to-end chat flow with mocked providers |

## Dependencies

- Phase 1 (API scaffolding, DB, auth, middleware)
- `langgraph`, `langchain-core` (for interfaces only)
- `google-genai` SDK
- WebSocket support in FastAPI

## Risks

| Risk | Mitigation |
|------|------------|
| LangGraph API instability | Pin major version; isolate in `infrastructure/ai/graph/` |
| Gemini rate limits | Implement exponential backoff in AI Inference Service; queue under load |
| WebSocket scaling | Connection Manager stores sessions in Redis; horizontal scaling via sticky sessions |
| Token costs during development | Set per-tenant budget; use Gemini 1.5 Flash for dev |

## Acceptance Criteria

- [ ] WebSocket chat sends message, receives streamed response
- [ ] REST `POST /messages` sends message, receives full response
- [ ] Intent classification returns correct intent for test queries (order_status, product_info, return, etc.)
- [ ] RAG retrieval returns relevant document chunks (with mocked vector store)
- [ ] Tool selection is triggered for product/order queries
- [ ] Response includes citations when RAG is used
- [ ] Conversation history is persisted and retrievable
- [ ] Memory stores and retrieves user facts across turns
- [ ] Low-confidence responses trigger escalation event
- [ ] All provider abstractions are mockable and tested