# ADR-047: Runtime Events

## Status
Accepted

## Context
Decoupling internal state shifts, memory operations, and tool actions from outer platform components is essential for Clean Architecture compliance. Direct component referencing introduces circular loops and high maintenance friction.

## Decision
We establish a unified, asynchronous platform-wide event-driven model:
* **Shared EventBus Contract:** We declare a platform-level `EventBus` Protocol inside `application/ports/event_bus.py`, with an async in-memory implementation in `infrastructure/event_bus/`.
* **Standard Domain Events:** Exposes dataclasses for platform operations:
  * `ConversationStarted` / `ConversationCompleted`
  * `ExecutionStarted` / `ExecutionCompleted` / `ExecutionFailed`
  * `ExecutionStateChangedEvent`
  * `ToolExecuted`
  * `MemoryUpdated`
* **Concurrence Processing:** Executions dispatch these events as async task targets, letting multiple downstream modules (like audit trails, logging, or metric gatherers) process actions concurrently.

## Consequences
* **Pros:** Complete component isolation, simple integration of new metrics, and highly responsive operational workflows.
* **Cons:** Concurrently executing gathering tasks requires defensive error handling within each listener to avoid crashing thread loops.
