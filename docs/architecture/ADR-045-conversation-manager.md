# ADR-045: Conversation Manager

## Status
Accepted

## Context
Enterprise multi-tenant conversational platforms support many active chat contexts. Tracking participant indexing, starting/closing conversations, isolating tenant messages, and storing session metadata need a robust, unified management layer.

## Decision
We implement a highly cohesive `ConversationManager` class:
* **Session Metadata & States:** Manages active chat contexts, custom metadata dictionaries, and conversation states (`active` or `closed`) isolated by tenant boundaries.
* **Participant Indices:** Indexes and exposes list maps of authorized participant IDs (users or agents) per conversation.
* **Unified Event Dispatching:** Triggers standard `ConversationStarted` and `ConversationCompleted` domain events when conversations are initialized or finalized.

## Consequences
* **Pros:** Highly structured conversation context and participants boundaries, unified lifecycle tracking, and isolated storage.
* **Cons:** State is in-memory for Phase 3 (will be connected to PostgreSQL repositories in next stages).
