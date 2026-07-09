# Phase 3 — RAG Engine & Knowledge Base

## Objectives

Build a complete document ingestion pipeline and vector search engine. Support multiple document formats, configurable chunking strategies, tenant-scoped embeddings, and hybrid search with reranking.

## Deliverables

| Deliverable | Description |
|-------------|-------------|
| Document Parser | Parse PDF (PyMuPDF), Markdown, TXT, HTML, and web page content |
| Chunking Strategies | Recursive character split, semantic split, fixed-size with overlap |
| Document Management API | Upload, list, get, delete, reprocess documents |
| Embedding Generation Pipeline | Async batch embedding via background task or Celery worker |
| Vector Store (pgvector) | `store`, `search`, `delete` operations with tenant scoping |
| Hybrid Search | Vector similarity (cosine) + keyword (PostgreSQL `tsvector`) with weighted fusion |
| Reranker Integration | Cross-encoder reranking of top-k results |
| Context Builder | Token-budget-aware context window with citation tracking |
| Document Processing Status | `pending`, `processing`, `completed`, `failed` with error messages |
| Tenant Configuration | Per-tenant chunking strategy, top-k, score threshold, model selection |
| Unit Tests | Parser, chunker, searcher, context builder for each format |
| Integration Tests | Full pipeline: upload → parse → chunk → embed → search → rerank |

## Dependencies

- Phase 1 (DB, auth, middleware)
- Phase 2 (embedding provider abstraction)
- `PyMuPDF`, `markdown`, `beautifulsoup4`, `httpx` (web scraping)
- pgvector extension in PostgreSQL

## Risks

| Risk | Mitigation |
|------|------------|
| Large PDF documents (1000+ pages) | Stream processing; page-level chunking before full parsing |
| Embedding API rate limits | Batch embeddings with configurable concurrency (default 5) |
| Storage growth from embeddings | Retention policy; archive unused tenant documents after 90 days |
| Poor chunk quality | Provide multiple chunking strategies; default to recursive 512 with 50 overlap |

## Acceptance Criteria

- [ ] PDF (text + scanned via OCR fallback) is parsed correctly
- [ ] Large documents are chunked with configurable strategy
- [ ] Chunks are embedded and stored in pgvector with tenant isolation
- [ ] Query returns top-k chunks with similarity scores
- [ ] Reranking improves top-k precision (validated with test queries)
- [ ] Context builder respects token budget and includes citations
- [ ] Document processing status is tracked end-to-end
- [ ] Tenant A's documents are invisible to Tenant B's search
- [ ] Deleting a document removes all associated embeddings