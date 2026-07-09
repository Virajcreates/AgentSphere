# Phase 4 — Conversation & Knowledge Platform: Implementation Plan

This implementation plan outlines the architectural structure, database migrations, exposed APIs, logic refinements, and dependencies to deliver the **Conversation & Knowledge Platform** inside AgentSphere, conforming to Frozen Architecture `v1.1`.

---

## 1. Executive Summary & Design Logic
Phase 4 introduces enterprise-grade stateful conversation management and tenant-scoped Knowledge Base retrieval (RAG). 

Adhering to the new permanent design rule, all major subsystems in Phase 4 are isolated behind unified, high-level **Public Service Interfaces**:
*   `ConversationService`
*   `KnowledgeService`
*   `EmbeddingService`
*   `RetrieverService`
*   `SummarizationService`

All platform components interact strictly with these services rather than low-level repositories or individual providers. This guarantees highly cohesive boundaries, prevents direct repository exposure, and facilitates easy architectural evolutions.

Additionally, we implement:
1.  **Directed acyclic doc pipeline**: Async parsers extracting text from `PDF`, `DOCX`, `TXT`, `Markdown`, `HTML`, and `URLs`, running cleaning filters, extracting metadata, and splitting contents via pluggable strategies (`Recursive`, `Markdown`, `Semantic`, `Fixed`).
2.  **Cosine Similarity pgvector lookups**: Vector stores querying pgvector tables using Cosine Distance (`vector_cosine_ops`), supporting hybrid retrievals, similarity threshold bounds, and exact source attributions.
3.  **Autonomous LangGraph adapters**: Reconstitutes agent states inside unified LangGraph execution adapter nodes (`MemoryNode`, `RetrievalNode`, `ToolNode`, `LLMNode`) running inside our core `AgentRuntime`.
4.  **Automatic summaries & budget policies**: Automatically compiles chat summarizations when hitting retention thresholds while retaining raw chat histories, validating token expenditures against active budget limits.

---

## 2. Proposed Folder Tree
The elements are woven into the existing codebase cleanly:
```
src/agentsphere/
├── application/
│   └── services/                 # Major Public Service Interfaces & Orchestrations
│       ├── conversation_service.py
│       ├── knowledge_service.py
│       ├── embedding_service.py
│       ├── retriever_service.py
│       └── summarization_service.py
├── domain/
│   ├── models/                   # Updated SQLAlchemy ORM Models
│   │   ├── conversation.py       #   Conversation, ConversationMessage, ConversationSummary
│   │   └── knowledge.py          #   KnowledgeBase, Collection, Document, DocumentChunk
│   └── value_objects/
├── infrastructure/
│   ├── persistence/
│   │   ├── migrations/
│   │   │   └── versions/
│   │   │       └── 002_conversation_and_knowledge.py # Alembic Migration Script
│   │   └── repositories/
│   │       ├── conversation_repository.py
│   │       └── knowledge_repository.py
│   └── rAG/                      # Low-Level Document Pipeline & Chunkers
│       ├── chunking/             #   Recursive, Markdown, Semantic, Fixed Strategies
│       └── parsing/              #   PDF, DOCX, TXT, HTML, URL parsed text extractors
├── interfaces/
│   ├── api/
│   │   └── routes/               # Exposed Web REST Endpoints
│   │       ├── conversations.py  #   POST/GET /api/v1/conversations
│   │       └── knowledge.py      #   POST/GET/DELETE /api/v1/knowledge-bases
│   └── adapters/
│       └── langgraph/            # LangGraph Adapter implementation and execution nodes
```

---

## 3. Files to Create (28 Files)

### Public Services & Logic Boundaries (5 Files)
*   **`src/agentsphere/application/services/conversation_service.py`**: Public orchestration interface for conversations. Handles creations, active chat loops, appends user/assistant turns, checks policies (`Maximum Turns`, `Idle Timeout`, `Summary Threshold`, `Retention`), and saves lineages.
*   **`src/agentsphere/application/services/knowledge_service.py`**: Public interface managing knowledge documents. Runs the parsing pipeline, executes chunking, resolves vector embeddings, and writes tables.
*   **`src/agentsphere/application/services/embedding_service.py`**: Standardizes embedding generation. Routes text batches to configured AI providers via the existing `AIGateway` and validates output dimensions.
*   **`src/agentsphere/application/services/retriever_service.py`**: Handles hybrid retrieval. Executes vector lookup, runs token Jaccard overlapping strings queries, filters metadata, and returns source attributions linking back to chunks, pages, and documents.
*   **`src/agentsphere/application/services/summarization_service.py`**: Triggers async LLM summarizing of chat histories on threshold breaches, returning concise conversation summaries.

### SQLAlchemy Database Models (2 Files)
*   **`src/agentsphere/domain/models/conversation.py`**: Declarative models for `Conversation` (status, active users, metadata), `ConversationMessage` (raw thread messages history), and `ConversationSummary` (compiled chat snapshots).
*   **`src/agentsphere/domain/models/knowledge.py`**: Declarative models for `KnowledgeBase` (name, status), `Collection` (tenant scopes), `Document` (source formats, URLs, parsing metadatas), and `DocumentChunk` (sliced strings, page indices, and vector embeddings utilizing SQLAlchemy pgvector `Vector` columns).

### Repository Database Interfaces (2 Files)
*   **`src/agentsphere/infrastructure/persistence/repositories/conversation_repository.py`**: Concrete queries retrieving chat histories, appending messages, and querying summaries.
*   **`src/agentsphere/infrastructure/persistence/repositories/knowledge_repository.py`**: Cosine distance similarity search operator queries. Enforces tenant scope parameters inside all chunk lookups.

### Document Pipeline & Pluggable Chunkers (6 Files)
*   **`src/agentsphere/infrastructure/rag/parsing/document_parser.py`**: Extractors parsing strings from standard formats (`PDF`, `DOCX`, `TXT`, `Markdown`, `HTML`, `URL`).
*   **`src/agentsphere/infrastructure/rag/chunking/base.py`**: Port protocol `ChunkingStrategy` declaring `split_text(text, chunk_size, chunk_overlap)` parameters.
*   **`src/agentsphere/infrastructure/rag/chunking/recursive.py`**: Pluggable splitter recursively dividing paragraphs, sentences, and words to preserve boundaries.
*   **`src/agentsphere/infrastructure/rag/chunking/markdown.py`**: Headings-aware splitter slicing by Markdown sections (`#`, `##`, `###`).
*   **`src/agentsphere/infrastructure/rag/chunking/fixed.py`**: Slides raw content strictly by fixed character caps.
*   **`src/agentsphere/infrastructure/rag/chunking/semantic.py`**: Splits sentences, dynamically calculating cosine distances between consecutive sentences to identify breakpoint boundaries.

### LangGraph Adapter & Nodes (2 Files)
*   **`src/agentsphere/interfaces/adapters/langgraph/adapter.py`**: Main `LangGraphAdapter` compiling execution graphs and state variables, feeding them sequentially through executing nodes inside our `AgentRuntime`.
*   **`src/agentsphere/interfaces/adapters/langgraph/nodes.py`**: Defines isolated operational graph steps conforming to LangGraph node schemas: `MemoryNode`, `RetrievalNode`, `ToolNode`, and `LLMNode`.

### Web REST API Interfaces (2 Files)
*   **`src/agentsphere/interfaces/api/routes/conversations.py`**: REST Endpoints for creating chat threads, appending message turns, querying histories, and loading conversation summaries.
*   **`src/agentsphere/interfaces/api/routes/knowledge.py`**: REST Endpoints for creating knowledge bases, uploading source files, indexing URLs, and conducting similarity queries.

### Detailed Architectural Decision Records (ADRs) (8 Files)
*   `docs/architecture/ADR-049-conversation-engine.md`
*   `docs/architecture/ADR-050-knowledge-platform.md`
*   `docs/architecture/ADR-051-chunking-strategy.md`
*   `docs/architecture/ADR-052-retrieval-architecture.md`
*   `docs/architecture/ADR-053-langgraph-integration.md`
*   `docs/architecture/ADR-054-conversation-policies.md`
*   `docs/architecture/ADR-055-summarization.md`
*   `docs/architecture/ADR-056-source-attribution.md`

### Database Migrations Script (1 File)
*   `src/agentsphere/infrastructure/persistence/migrations/versions/002_conversation_and_knowledge.py`

---

## 4. Files to Modify (3 Files)

### 1. `src/agentsphere/interfaces/container.py`
*   *Why*: We must wire all 5 new public service singletons, 2 repositories, parser/chunker engines, and LangGraph adapters in our Dependency Injection container.
*   *Modifications*: Register singletons for `ConversationRepository`, `KnowledgeRepository`, `EmbeddingService`, `SummarizationService`, `RetrieverService`, `ConversationService`, `KnowledgeService`, and `LangGraphAdapter` mapped declaratively under a new sub-container.

### 2. `src/agentsphere/interfaces/api/app.py`
*   *Why*: Register the newly created endpoint route controllers.
*   *Modifications*: Import and mount `/api/v1/conversations` and `/api/v1/knowledge-bases` routers.

### 3. `src/agentsphere/infrastructure/persistence/migrations/env.py`
*   *Why*: Let Alembic detect our new models dynamically.
*   *Modifications*: Import models from `conversation.py` and `knowledge.py` to populate Alembic's Metadata target.

---

## 5. Database Migrations Schema (`002_conversation_and_knowledge.py`)

We write standard SQL Alembic tables with foreign keys and index mappings:
1.  `knowledge_base`: PK `id` (UUIDv7), tenant isolation, string `name`, `status`, tracking.
2.  `collection`: PK `id` (UUIDv7), FK `knowledge_base_id`.
3.  `document`: PK `id` (UUIDv7), FK `collection_id`, string `name`, `source_type`, `meta_info` (JSONB).
4.  `document_chunk`: PK `id` (UUIDv7), FK `document_id`, `text_content` (TEXT), page index, `embedding` (`Vector(1536)` utilizing Cosine HNSW indexes for high-speed cos matches).
5.  `conversation`: PK `id` (UUIDv7), tenant isolation, `status` string, tracking variables, metadata (JSONB).
6.  `conversation_message`: PK `id` (UUIDv7), FK `conversation_id`, role, content, metrics cost.
7.  `conversation_summary`: PK `id` (UUIDv7), FK `conversation_id`, context window string.

---

## 6. Web REST APIs Exposed

| Method | Path | Authentication | Description |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/v1/conversations` | None / Tenant | Start a stateful conversational context. |
| **GET** | `/api/v1/conversations/{id}` | JWT / Tenant | Fetch raw messages history and parameters context. |
| **POST** | `/api/v1/conversations/{id}/messages` | JWT / Tenant | Send a message turn, trigger Summarizing if policy limits are hit. |
| **POST** | `/api/v1/knowledge-bases` | JWT / Tenant | Setup a new Document Knowledge Base. |
| **POST** | `/api/v1/knowledge-bases/{id}/documents` | JWT / Tenant | Upload TXT/Markdown documents, parses and index text. |
| **POST** | `/api/v1/knowledge-bases/{id}/query` | JWT / Tenant | Conduct Vector and Hybrid searches with Source Attribution links. |

---

## 7. Dependencies
*   `pgvector` standard PostgreSQL integration.
*   `langgraph` and `langchain-core` (strictly imported within LangGraph execution nodes and interfaces - never leaking).

---

## 8. Risks & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| **Heavy Parse / Index Bloat** | Isolate document parsing to happen asynchronously, keeping memory variables scoped locally. |
| **Cosine Distance Index Limits** | Configure the pgvector database HNSW index utilizing Cosine Distance parameters specifically matching embedding dimensions (1536) for fast traversals. |
| **Token Cost Overruns** | Calculate token expenditures against active tenant budgets before triggering expensive summarizations. |

---

## 9. Acceptance Criteria

- [ ] **Major Services Encapsulation**: Low-level repository commands or ai providers are never accessed directly; the system orchestrates solely through Service interfaces.
- [ ] **Accurate RAG Retrieval & Source Attribution**: Conducting similarities queries returns whitelisted document references with correct score indicators and segment values.
- [ ] **Automatic Summarization on Threshold**: Conversations hitting turn policy limits execute LLM Summarizing while preserving complete raw histories.
- [ ] **Polished Document Chunking**: Slicing functions divide textual inputs without missing boundary sentences.
- [ ] **LangGraph Execution Safety**: State values correctly transition across LangGraph Adapter execution nodes under the orchestrating scope of `AgentRuntime`.
- [ ] **Complete Test Coverage**: Combined code coverage across all new major systems beats **`90%+`**.
- [ ] **Flawless Compiles**: Type annotations compile under strict mypy and ruff check constraints with `0` errors.
