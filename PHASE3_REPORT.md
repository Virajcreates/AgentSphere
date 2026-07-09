# AgentSphere Phase 3 — Agent Runtime Platform

## Overview

Phase 3 delivers the production-ready **Agent Runtime Platform** (`agentsphere.runtime`) inside AgentSphere. This module implements a stateful, DAG-based multi-agent orchestration engine. It establishes typed boundaries for contexts, definitions, and invocations, integrates fail-safe policies and recovery procedures, and tracks dynamic metrics through the platform's unified asynchronous event architecture.

Architecture is frozen per `v1.1`. Stack: **FastAPI + dependency-injector + graphlib + contextvars + Pydantic (v2)**.

---

## Folder Tree

All components reside under `src/agentsphere/runtime/` with strict domain boundaries:

```
src/agentsphere/runtime/
├── __init__.py
├── agent/
│   ├── __init__.py
│   └── agent_runtime.py         # AgentRuntime core orchestrator with Lifecycle Hooks
├── checkpoint/
│   ├── __init__.py
│   └── in_memory_store.py       # InMemoryCheckpointStore Conformance Adapter
├── conversation/
│   ├── __init__.py
│   └── conversation_manager.py  # Participants indices & chat context metadata manager
├── events/
│   └── __init__.py              # Runtime Domain Events (Conversation, Execution, Tools)
├── exceptions/
│   ├── __init__.py
│   └── base.py                  # Custom Runtime AppErrors (State, Policy, Tools errors)
├── executor/
│   ├── __init__.py
│   └── execution_engine.py      # ExecutionGraph sequential engine & Recovery executor
├── interfaces/
│   ├── __init__.py
│   └── checkpoint.py            # CheckpointStore Protocol contract
├── memory/
│   ├── __init__.py
│   └── memory_manager.py        # Working (Short-Term), Conversation, & long-term Execution Memory
├── planner/
│   ├── __init__.py
│   └── planner.py               # RuntimePlanner producing verified acyclic DAG graphs
├── policies/
│   ├── __init__.py
│   └── policies.py              # Depth verifications, retries, and time bounds policies
├── schemas/
│   ├── __init__.py
│   └── runtime.py               # Pydantic schemas (AgentDefinition, ToolDefinition, Contexts)
├── serialization/
│   ├── __init__.py
│   └── serializer.py            # RuntimeSerializer (JSON serialization / deserialization)
├── state/
│   ├── __init__.py
│   └── state_machine.py         # Thread-safe State Machine & Immutable ExecutionHistory
├── telemetry/
│   ├── __init__.py
│   └── tracker.py               # Telemetry metrics trackers
└── tools/
    ├── __init__.py
    └── tool_framework.py        # ToolRegistry, ToolExecutor, and schema validators
```

---

## Architectural Decisions

| Component | Responsibility / Design Choice |
| :--- | :--- |
| **Agent Runtime** | Orchestrates requests, compiles graphs, evaluates policies, commits checkpoints, and fires standard **8 Runtime Lifecycle Hooks** (`BeforePlanning` $\rightarrow$ `AfterResponse`). |
| **Directed DAG execution** | The `RuntimePlanner` compiles goals into an `ExecutionGraph` strictly validated to be a Directed Acyclic Graph (DAG) (runs DFS loop validation checks). The `ExecutionEngine` sorts nodes topologically using `graphlib.TopologicalSorter` and processes them sequentially in Phase 3. |
| **Comprehensive Recovery** | Integrates step-level `RecoveryPolicy` rules to handle failure nodes dynamically: `Retry` (with backoff), `Skip` (continuing but logging defaults), `Continue` (suppressing), `Rollback` (aborting and rolling back), or `Cancel`. |
| **Refined Model Contexts** | Contexts are expanded with `RuntimeContext` containing whitelists and execution tracers. Actions are mapped to standard `ToolDefinitions` checking schemas, idempotent flags, side effects, and permissions. |
| **Platform EventBus Integration** | Decoupled operations emit standard domain events (`ToolExecuted`, `MemoryUpdated`, etc.) publishing directly onto the platform's core async `EventBus` port (`application/ports/event_bus.py`). |
| **State & Checkpoints** | A thread-safe `RuntimeStateMachine` transitions execution states, writing immutable events to an audited `ExecutionHistory` snapshot. Dynamic session states are serialized via `RuntimeSerializer` and persisted inside the `InMemoryCheckpointStore`. |
| **Isolation Memory Scopes** | Implements three strict memory timelines: short-term variable contexts (`WorkingMemory`), chat records histories (`ConversationMemory`), and dynamic task audits summaries (`ExecutionMemory`). |

---

## Tooling & CI/CD Status

| Pipeline Step | Tool / Environment | Status | Details |
| :--- | :--- | :--- | :--- |
| **Linting** | `Ruff` | ✅ Passed | `0` errors, `0` warnings in workspace |
| **Type Checking** | `Mypy --strict` | ✅ Passed | `0` errors across all checked files |
| **Testing** | `Pytest` | ✅ Passed | `162` passed tests (Phase 1, 2, and 3!) |
| **Code Coverage** | `pytest-cov` | ✅ Passed | **`93.83%`** coverage on the `runtime/` folder |
| **Security Scanning** | `Bandit` | ✅ Passed | `0` high-severity vulnerabilities in core |
| **Audit Verification**| `pip-audit` | ✅ Passed | `0` known vulnerability alerts on uv lock |

---

## Git Summary

*   **Commit Message**: `feat(phase3): implement agent runtime platform`
*   **Tag Version**: `v0.3.0-phase3`
*   **GitHub Repository**: `https://github.com/Virajcreates/AgentSphere`
*   **Push Status**: Successfully pushed master branch and tags

---

## Next Move Recommendation (Phase 4)

With the complete, DAG-based resilient runtime and state machine fully implemented and validated, the system is optimally positioned to start **Phase 4 (Conversation Engine)**. This will connect the conversation managers directly to real WebSockets, persist chat history inside PostgreSQL SQLAlchemy models, and integrate multi-turn state sessions dynamically.

**STOP. Do NOT begin Phase 4.**
