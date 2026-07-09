# ADR-056: Source Attribution

## Status
Accepted

## Context
RAG pipelines are prone to hallucinations. Lacking exact references to the specific documents, collections, and original page locations makes it difficult for end-users to verify facts, leading to low system trust.

## Decision
We enforce dynamic **Source Attribution** on all retrieved segments:
* **Attribution Metadata Contract:** Every chunk returned by `RetrieverService` must populates a standard source contract including:
  * `knowledge_base_id`: Unique KB partition.
  * `document_id`: Parent indexed source file.
  * `chunk_id`: Exact database chunk PK.
  * `page_index`: Standardized original sheet index (1-indexed).
  * `similarity_score`: The calculated blended hybrid score.
* **Traceable Auditing:** These links are saved directly within the lineage logging trace of `AIInferenceService` to enable end-to-end verifiability.

## Consequences
* **Pros:** Complete traceability, prevents hallucinations, elevates system trust, and simplifies auditing.
* **Cons:** Requires preserving page numbers throughout parsing and slicing layers.
