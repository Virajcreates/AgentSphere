# ADR-041: Agent Runtime

## Status
Accepted

## Context
AgentSphere needs a highly resilient execution engine to drive multi-agent systems, sequential/directed loops, and task-oriented workflows. Hardcoding execution paths or relying on ad-hoc runtime loops makes debugging, auditing, and multi-tenant isolation extremely difficult.

## Decision
We implement a highly decoupled, async `AgentRuntime` orchestrator (`agentsphere.runtime.agent.AgentRuntime`):
* **Stateful Loop Coordinator:** Coordinates the transition of system-level states and executes DAG-based execution graphs.
* **Pluggable Lifecycle Hooks:** Supports 8 registerable hooks (`BeforePlanning`, `AfterPlanning`, `BeforeExecution`, `AfterExecution`, `BeforeTool`, `AfterTool`, `BeforeResponse`, `AfterResponse`) allowing third-party extensions to hook into execution.
* **Checkpoint Isolation:** Commits completed working and session state variables to an isolated `CheckpointStore` using standard `RuntimeSerializer` serialization layers.

## Consequences
* **Pros:** Highly polished orchestrator, strict multi-tenant boundary isolations, dynamic extensions points via hooks, and robust error safety.
* **Cons:** Introduces moderate orchestration layer overhead.
