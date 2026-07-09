# ADR-048: Memory Foundation

## Status
Accepted

## Context
AI Agents operate across three distinct memory timelines: local step variables (Working memory), conversational history contexts (Conversation memory), and long-term task histories/summaries (Execution memory). Lacking standard separations of these timelines causes confusing variable overrides and limits contextual flexibility.

## Decision
We define clean, separate Protocols and in-memory stores for each memory dimension:
* **WorkingMemory Port:** Short-term in-flight execution parameters (including async methods `get`, `set`, `clear`, and `get_all` to serialize).
* **ConversationMemory Port:** Accumulates structured chat lists (messages history context).
* **ExecutionMemory Port:** Standard logs for long-term task audits and final summaries.
* **Unified Managers:** Coordinates instantiation of thread-safe in-memory stores inside a `MemoryManager`.
* **Event Dispatching:** Any write operation onto memory automatically publishes a `MemoryUpdated` domain event through the common EventBus.

## Consequences
* **Pros:** Standard memory separations, highly flexible long-term contextual mapping, complete auditing, and strict thread isolations.
* **Cons:** Requires a cleanup phase inside the orchestrator to prune in-memory dictionaries once execute scopes exit.
