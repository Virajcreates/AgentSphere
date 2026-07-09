# ADR-054: Conversation Policies

## Status
Accepted

## Context
Multi-tenant applications are prone to high transaction cost overruns, thread starvation from hanging connections, and excessive database storage growth from never-ending conversational threads.

## Decision
We implement a lightweight policies evaluation layer inside `ConversationService`:
* **Multi-dimensional constraints:** Enforces four strict active limits on every new message turn:
  * `max_turns_policy` (default: 20 turns): Caps total thread depth.
  * `idle_timeout_policy` (default: 3600s): Expires inactive sessions.
  * `token_budget_policy` (default: 50,000 tokens): Controls request payload bounds.
  * `summary_turns_threshold` (default: 5 turns): Schedules async summary generation.

## Consequences
* **Pros:** Highly secure, protects cloud expenditures, manages thread pools, and minimizes database bloat.
* **Cons:** Triggers an exception if any policy limits are violated during in-flight executions.
