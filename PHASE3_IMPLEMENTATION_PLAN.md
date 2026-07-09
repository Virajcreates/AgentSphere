# Phase 3 — Agent Runtime Platform: Final Implementation Plan

This final implementation plan integrates stateful workflows, recovery fail-safes, checkpoint persistence ports, and tool specifications into the **Agent Runtime Platform** (`agentsphere.runtime`) following Frozen Architecture `v1.1`.

---

## 1. Executive Summary
The Agent Runtime Platform is refined into a production-grade DAG-based orchestration engine. 

Instead of simple lists or free-form graphs, the runtime is governed by an **ExecutionGraph** modeled strictly as a **Directed Acyclic Graph (DAG)**. While nodes are processed sequentially in Phase 3 (parallel execution scheduling is deferred), the structure guarantees compatibility with multi-branch asynchronous execution. 

An `AgentDefinition` can manage multiple **WorkflowDefinitions** containing fine-grained tool and memory bindings. Executions map actions to exact **ToolDefinitions** (incorporating permissions, idempotency flags, and side-effects constraints) and apply step-level **RecoveryPolicies** (`Retry`, `Skip`, `Cancel`, `Rollback`, `Continue`). Stateless serialization is handled via `RuntimeSerializer`, and persistent state capturing is cleanly isolated inside the **CheckpointStore** protocol with an in-memory implementation for Phase 3.

---

## 2. Final Folder Tree
All runtime packages are grouped cleanly under `src/agentsphere/runtime/`:

```
src/agentsphere/runtime/
├── __init__.py
├── agent/
│   ├── __init__.py
│   └── agent_runtime.py         # AgentRuntime orchestrator with 8 Lifecycle Hooks
├── checkpoint/
│   ├── __init__.py
│   └── in_memory_store.py       # InMemoryCheckpointStore Conformance Adapter
├── conversation/
│   ├── __init__.py
│   └── conversation_manager.py  # Session participants & histories indexer
├── events/
│   └── __init__.py              # Domain Events schemas dispatched to platform EventBus
├── exceptions/
│   ├── __init__.py
│   └── base.py                  # State Machine, Recovery, & Policy Exceptions
├── executor/
│   ├── __init__.py
│   └── execution_engine.py      # DAG execution engine with RecoveryPolicies
├── interfaces/
│   ├── __init__.py
│   └── checkpoint.py            # CheckpointStore Protocol contract
├── memory/
│   ├── __init__.py
│   └── memory_manager.py        # Working, Conversation, and Execution memory protocols
├── planner/
│   ├── __init__.py
│   └── planner.py               # RuntimePlanner generating DAG ExecutionGraphs
├── policies/
│   ├── __init__.py
│   └── policies.py              # Depth caps, retries, and execution time bounds
├── schemas/
│   ├── __init__.py
│   └── runtime.py               # Schemas (AgentDefinition, WorkflowDefinition, ToolDefinition, RecoveryPolicy)
├── serialization/
│   ├── __init__.py
│   └── serializer.py            # RuntimeSerializer (pure JSON serialization)
├── state/
│   ├── __init__.py
│   └── state_machine.py         # Validation State Machine & ExecutionHistory tracker
├── telemetry/
│   ├── __init__.py
│   └── tracker.py               # Prometheus metrics metrics collector
└── tools/
    ├── __init__.py
    └── tool_framework.py        # Tool Registry & Schema validations
```

---

## 3. Final File Creation Plan (32 Files)

### Shared Platform Interfaces
| File Path | Purpose |
| :--- | :--- |
| **`src/agentsphere/application/ports/event_bus.py`** | **Unified EventBus Port:** Shared platform-wide async `EventBus` Protocol interface. |
| **`src/agentsphere/infrastructure/event_bus/in_memory_event_bus.py`** | **InMemory EventBus Adapter:** Shared platform-wide EventBus implementation. |

### Runtime Interfaces & Store
| File Path | Purpose |
| :--- | :--- |
| **`src/agentsphere/runtime/interfaces/__init__.py`** | Initializer for runtime interfaces. |
| **`src/agentsphere/runtime/interfaces/checkpoint.py`** | **CheckpointStore Port:** Protocol defining async `save(checkpoint_id, data)`, `load(checkpoint_id)`, and `delete(checkpoint_id)` contracts. |
| **`src/agentsphere/runtime/checkpoint/__init__.py`** | Initializer for checkpoint module. |
| **`src/agentsphere/runtime/checkpoint/in_memory_store.py`** | **InMemoryCheckpointStore Adapter:** Thread-safe in-memory state repository conforming to `CheckpointStore`. |

### Exceptions & Common Schemas
| File Path | Purpose |
| :--- | :--- |
| **`src/agentsphere/runtime/exceptions/base.py`** | Custom exceptions: `InvalidStateTransitionError`, `PolicyLimitViolationError`, `ToolValidationError`, `WorkflowCancellationError`, `ExecutionTimeoutError`, and `WorkflowRecoveryException`. |
| **`src/agentsphere/runtime/schemas/__init__.py`** | Schema package initializer. |
| **`src/agentsphere/runtime/schemas/runtime.py`** | Core schemas: **`RuntimeContext`**, **`ToolDefinition`** (incorporates permissions, idempotency flags, and side-effects constraints), **`WorkflowDefinition`**, **`AgentDefinition`**, **`RecoveryPolicy`** (encapsulates strategies: `Retry`, `Skip`, `Cancel`, `Rollback`, `Continue`), **`ExecutionGraph`** (enforced as a Directed Acyclic Graph - DAG), and **`ExecutionHistory`**. |

### Core Runtime Pipeline
| File Path | Purpose |
| :--- | :--- |
| **`src/agentsphere/runtime/__init__.py`** | Package initializer. |
| **`src/agentsphere/runtime/state/__init__.py`** | State package initializer. |
| **`src/agentsphere/runtime/state/state_machine.py`** | Governs transitions across `Created` $\rightarrow$ `Planning` $\rightarrow$ `Executing` $\rightarrow$ `Waiting` $\rightarrow$ `Completed` / `Failed` / `Cancelled`. Appends dynamic, immutable snapshots into `ExecutionHistory`. |
| **`src/agentsphere/runtime/conversation/__init__.py`** | Package initializer. |
| **`src/agentsphere/runtime/conversation/conversation_manager.py`** | Tracks conversation sessions, metadata dictionary, and conversations state. |
| **`src/agentsphere/runtime/planner/__init__.py`** | Planner package initializer. |
| **`src/agentsphere/runtime/planner/planner.py`** | Parses goal statements and selects matching `WorkflowDefinition` templates to produce a validated **`ExecutionGraph` DAG**. |
| **`src/agentsphere/runtime/executor/__init__.py`** | Executor package initializer. |
| **`src/agentsphere/runtime/executor/execution_engine.py`** | **Execution Engine**: Topologically sorts the `ExecutionGraph` DAG and processes nodes sequentially. Integrates active **`RecoveryPolicy`** strategies per step (Retry, Skip, Cancel, Rollback, Continue) on nodes failure. |
| **`src/agentsphere/runtime/tools/__init__.py`** | Tools package initializer. |
| **`src/agentsphere/runtime/tools/tool_framework.py`** | Conformance Protocols for registries, validating inputs against `ToolDefinition` json schemas, and executing tool calls. |
| **`src/agentsphere/runtime/memory/__init__.py`** | Memory package initializer. |
| **`src/agentsphere/runtime/memory/memory_manager.py`** | Stateful interfaces and memory wrappers for short-term `WorkingMemory`, `ConversationMemory`, and long-term `ExecutionMemory`. |
| **`src/agentsphere/runtime/events/__init__.py`** | Runtime schemas for domain events: `ConversationStarted`, `ConversationCompleted`, `ExecutionStarted`, `ExecutionCompleted`, `ExecutionFailed`, `ToolExecuted`, and `MemoryUpdated`. |
| **`src/agentsphere/runtime/policies/__init__.py`** | Policies package initializer. |
| **`src/agentsphere/runtime/policies/policies.py`** | Validates active depth limits, retries limits, and execution duration bounds. |
| **`src/agentsphere/runtime/telemetry/__init__.py`** | Telemetry package initializer. |
| **`src/agentsphere/runtime/telemetry/tracker.py`** | Prometheus collector tracking latencies, memory transaction counts, success ratios, and recovery policy triggers. |
| **`src/agentsphere/runtime/serialization/__init__.py`** | Serialization package initializer. |
| **`src/agentsphere/runtime/serialization/serializer.py`** | Statelessly converts execution states, graphs, context maps, and memory structures to/from JSON strings. |
| **`src/agentsphere/runtime/agent/__init__.py`** | Agent package initializer. |
| **`src/agentsphere/runtime/agent/agent_runtime.py`** | **The Core Orchestrator Class `AgentRuntime`.** Directs the overall request, execution, and state-machine transitions. Fires the standard **8 Runtime Lifecycle Hooks** (`BeforePlanning`, `AfterPlanning`, `BeforeExecution`, `AfterExecution`, `BeforeTool`, `AfterTool`, `BeforeResponse`, `AfterResponse`). |

### Architectural Decision Records (ADRs)
| File Path | Purpose |
| :--- | :--- |
| **`docs/architecture/ADR-041-agent-runtime.md`** | Agent definitions, workflow maps, and life-cycle hook patterns. |
| **`docs/architecture/ADR-042-execution-engine.md`** | Topologically-sorted DAG traversal algorithms and sequential fallback limits. |
| **`docs/architecture/ADR-043-runtime-state-machine.md`** | Valid transitions validations, immutable histories logs, and tracking rules. |
| **`docs/architecture/ADR-044-tool-framework.md`** | Tool contract definitions, idempotency features, and side-effects constraints. |
| **`docs/architecture/ADR-045-conversation-manager.md`** | Conversational boundaries, participants indexes, and state histories. |
| **`docs/architecture/ADR-046-runtime-policies.md`** | Step-level recovery policy options and global execution timeout caps. |
| **`docs/architecture/ADR-047-runtime-events.md`** | System decoupled operations via the unified shared `EventBus`. |
| **`docs/architecture/ADR-048-memory-foundation.md`** | Boundary separations of Short, Medium, and long term Execution memories. |

### Comprehensive Unit Testing (8 Files)
All testing will reside under `tests/unit/runtime/`:
*   `tests/unit/runtime/test_state_machine.py` (Asserts transition validations and history registries)
*   `tests/unit/runtime/test_conversation_manager.py` (Tests participants lifecycles and indices)
*   `tests/unit/runtime/test_planner.py` (Asserts DAG compile validations, circular dependencies errors, entry node searches)
*   `tests/unit/runtime/test_execution_engine.py` (Tests topological sorting sequence and sequential DAG execution)
*   `tests/unit/runtime/test_tool_framework.py` (Tests `ToolDefinition` json validations, idempotency flags, and registry lookups)
*   `tests/unit/runtime/test_policies.py` (Tests step-level `RecoveryPolicy` strategies: Skip, Retry, Cancel, Rollback)
*   `tests/unit/runtime/test_memory.py`
*   `tests/unit/runtime/test_agent_runtime.py` (Tests end-to-end loop: hooks executions, JSON serialization, and **`InMemoryCheckpointStore`** save/load/delete)

---

## 4. File Modification Plan (1 File)

*   **`src/agentsphere/interfaces/container.py`**
    *   *Why:* We must register and wire all newly created runtime structures in our declarative DI container tree.
    *   *Modifications:* We will add a `RuntimeContainer` class registering singletons for `InMemoryEventBus`, `ConversationManager`, `RuntimeStateMachine`, `RuntimePlanner`, `ExecutionEngine`, `ToolRegistry`, `MemoryManager`, `RuntimeTracker`, `RuntimeSerializer`, `InMemoryCheckpointStore`, and `AgentRuntime`. We will wire `runtime = providers.Container(RuntimeContainer)` inside the top-level `ApplicationContainer`.

---

## 5. Dependencies
No external unverified third-party libraries will be added. We will use standard FastAPI, Pydantic, structlog, and Python 3.12+ stdlib concurrency/JSON serialization/topological sorting tools (e.g. `graphlib`).

---

## 6. Risks & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| **Parallel Scheduling Complexity** | Parallel scheduling is intentionally deferred. To maintain low complexity, Phase 3 executes DAG nodes sequentially utilizing topological sorting (`graphlib.TopologicalSorter` from standard library). |
| **Circular Graph Reference Loop** | Ensure the `ExecutionGraph` is strictly validated to be a Directed Acyclic Graph (DAG) in the planner step. Cyclic graphs must reject immediately with `PromptCompilationError`. |
| **Thread Context / Serialization Loss**| Verify that the `RuntimeSerializer` statelessly serializes all active variables, and `CheckpointStore` manages isolated tenant state instances. |

---

## 7. Acceptance Criteria

- [ ] **DAG Validation**: The system verifies the compiled `ExecutionGraph` is a Directed Acyclic Graph (DAG) possessing distinct nodes and edges, throwing errors on cycle identification.
- [ ] **Topologically Sorted Sequential Run**: Nodes inside the compiled `ExecutionGraph` DAG are sorted topologically and executed sequentially. Parallel executions are explicitly deferred.
- [ ] **Workflow Ownership**: An `AgentDefinition` supports multiple `WorkflowDefinitions`, with fine-grained tool whitelist and memory configurations.
- [ ] **State & Lineage Tracking**: Every state change publishes through the shared platform `EventBus` and records inside an immutable `ExecutionHistory` registry.
- [ ] **Comprehensive Recovery Engine**: Steps executing tool calls support granular step-level `RecoveryPolicy` options (`Retry`, `Skip`, `Cancel`, `Rollback`, `Continue`).
- [ ] **Checkpoint Storage Persistence**: The `InMemoryCheckpointStore` saves, restores, and deletes full context and memories without data cross-tenant leakage.
- [ ] **Polished Tool Configurations**: Every active tool enforces clear boundaries (`ToolDefinition`) including idempotent and side-effects constraints.
- [ ] **Dynamic Hook Execution**: All 8 lifecycle hooks execute sequentially at their defined system thresholds.
- [ ] **DI & Code Coverage**: All DI singletons resolve successfully, and unit test coverage exceeds **`90%+`**.
