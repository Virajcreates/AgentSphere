# ADR-050: Knowledge Platform

## Status
Accepted

## Context
AI agents are empowered by domain-specific document contexts. Integrating a flexible Document Pipeline requiring parsed, cleaned, chunked, and embedded strings inside a multi-tenant vector base needs clean logic boundaries to prevent direct model pollution.

## Decision
We implement a highly organized Knowledge Base (RAG) platform:
* **`KnowledgeService` Interface:** The centralized public gateway for knowledge bases, managing upload pipelines, HTML parsers, chunking strategies, and repository writes.
* **Acyclic Document Pipeline:** Runs parsed text extraction asynchronously from raw bytes (`PDF`, `DOCX`, `TXT`, `Markdown`, `HTML`, or `URL`), cleans whitespaces, splits texts using pluggable chunkers, and commits embedded float arrays to pgvector database tables.

## Consequences
* **Pros:** Highly unified document indexing workflows, robust multiformat support, secure database storage, and complete vendor decoupling.
* **Cons:** Slicing highly complex documents may require more advanced layout cleaners in future phases.
