# ADR-043: Runtime State Machine

## Status
Accepted

## Context
Agent workflows proceed through varying runtime lifecycles (created, planning, executing, completed, cancelled, failed). Lacking strict validation maps over these states causes invalid jumps, state desyncs, and prevents audit tracking.

## Decision
We implement a stateful, thread-safe `RuntimeStateMachine` class:
* **Validated Transitions Mapping:** Enforces a rigid state transitions matrix:
  * `Created` $\rightarrow$ `Planning`, `Cancelled`
  * `Planning` $\rightarrow$ `Executing`, `Failed`, `Cancelled`
  * `Executing` $\rightarrow$ `Waiting`, `Completed`, `Failed`, `Cancelled`
  * `Waiting` $\rightarrow$ `Executing`, `Failed`, `Cancelled`
  * Terminal states (`Completed`, `Failed`, `Cancelled`) cannot transition anywhere else.
* **Immutable Snapshot Recording:** Every atomic transition appends a detailed snapshot (timestamp, from_state, to_state) into an immutable, thread-local `ExecutionHistory` record.
* **Shared EventBus Dispatching:** Automatically publishes an async `ExecutionStateChangedEvent` domain event on every successful state change.

## Consequences
* **Pros:** Bulletproof state safety, idempotent checks, and robust auditable histories.
* **Cons:** Requires a locked transition operation on state shifts.
