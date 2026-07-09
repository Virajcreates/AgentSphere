# ADR-049: Conversation Engine

## Status
Accepted

## Context
AgentSphere needs to manage stateful multi-turn conversational loops. Lacking structured abstractions over chat lifecycles, message histories, and participant details leads to direct database leakages, thread collisions, and unstructured metadata.

## Decision
We implement a highly decoupled, async conversational architecture exposed via a high-level **Public Service Interface**:
* **`ConversationService` Orchestrator:** The single public gateway for conversational lifecycles, isolating other platform subsystems from repositories.
* **Database Messages Persistence:** Appends raw turn messages asynchronously to SQLAlchemy models (`ConversationModel`, `ConversationMessageModel`) isolated strictly by tenant UUIDs.

## Consequences
* **Pros:** Complete repository isolation, standard session boundaries, multi-tenant safety, and highly cohesive interfaces.
* **Cons:** Introduces minor boilerplate parameters mapping steps in service proxies.
