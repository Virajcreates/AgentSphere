# ADR-042: Execution Engine

## Status
Accepted

## Context
Multi-agent tasks often contain complex prerequisites and sequential steps. Re-evaluating or writing nested loops across agents causes fragile logic, race conditions, and prevents future branching or multi-threaded parallelism.

## Decision
We implement a highly reliable `ExecutionEngine` class using standard topological sorting:
* **Directed Acyclic Graphs (DAG):** Plans are represented inside an `ExecutionGraph` modeled strictly as a DAG of nodes and edges.
* **Topological Sort Sequence:** Sequences nodes topologically using `graphlib.TopologicalSorter` from the Python standard library. Parallel execution of nodes is deferred, with sequential execution acting as the Phase 3 baseline.
* **Granular Step-level Recovery Policies:** On node failure, evaluates and processes step-level `RecoveryPolicy` rules: `Retry` (with backoff delay), `Skip` (continuing but setting a default error value), `Continue` (completely suppressing failure), `Rollback` (aborting run and reverting states), and `Cancel` (raising a cancellation signal).

## Consequences
* **Pros:** Highly resilient sequential DAG execution, simple topological dependency resolutions, and fully compatible with future parallel multi-branch execution.
* **Cons:** Requires a topologically sorting step before executing any graph workflow.
