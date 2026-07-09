# ADR-052: Retrieval Architecture

## Status
Accepted

## Context
High-performance retrieval requires querying dense vector indices. Over-relying on vector distances often misses keyword-specific tokens matches, and direct exposure of database operations leaks repository interfaces.

## Decision
We implement a highly organized Hybrid Retrieval engine:
* **`RetrieverService` interface:** High-level public gateway managing multi-tenant retrieval pipelines.
* **Cosine pgvector lookups:** Queries PostgreSQL database tables using high-speed HNSW Cosine Distance (`<=>`) lookups, restricted strictly to the base KB.
* **Jaccard Lexical layer:** Layers dense vector outputs with pure-Python Token-Overlap Jaccard Similarity matching against query parameters (combined as `score = 0.7 * vector + 0.3 * text`).

## Consequences
* **Pros:** Highly accurate retrieval results, complete multi-tenant Isolation, secure database lookups, and fast HNSW lookups.
* **Cons:** Allocates moderate memory during in-memory hybrid overlaps recalculation steps.
