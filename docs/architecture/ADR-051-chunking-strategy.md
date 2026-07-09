# ADR-051: Chunking Strategy

## Status
Accepted

## Context
Standard text models are constrained by prompt context window sizes. Slicing long documents into random strings breaks lexical boundaries, losing headings structure, semantic contexts, and sentence flows.

## Decision
We establish a pluggable chunking strategy pattern inside the `application` layer:
* **`ChunkingStrategy` Port Protocol:** Declares standard string split parameters (`text`, `chunk_size`, `chunk_overlap`) under `application/services/chunking/base.py`.
* **Four Pluggable Strategies:**
  * `RecursiveChunkingStrategy`: Recursively divides text by structural splits (newlines, spaces).
  * `MarkdownChunkingStrategy`: Headings-aware splitter preserving outline sections boundaries.
  * `SemanticChunkingStrategy`: Sentence-aware splitter analyzing Jaccard distances between adjacent lines to group semantic sections.
  * `FixedChunkingStrategy`: Fixed character offset slides fallback.

## Consequences
* **Pros:** Highly flexible document chunking strategies, completely self-contained pure Python implementations, and 100% compliance with Clean Architecture rules (strategies reside in `application` rather than `infrastructure`).
* **Cons:** Slicing highly formatted tables may require specialized column split rules in later stages.
