# ADR-046: Runtime Policies

## Status
Accepted

## Context
Running multi-agent loops in production introduces risks of runaway execution (infinite tool loops, excessive prompt completions, high transaction cost budgets, and thread starvation).

## Decision
We implement a robust, lightweight `RuntimePolicyEvaluator` class inside `agentsphere.runtime.policies`:
* **Multi-dimensional Caps Enforcement:** Validates and enforces four strict active constraints during in-flight executions:
  * `max_execution_depth` (default: 10 steps): Caps overall DAG loop depths.
  * `max_tools_allowed` (default: 15 calls): Breaks runaway tool cycles.
  * `max_step_retries` (default: 5 retries): Validates node `RecoveryPolicy` limits.
  * `max_execution_time_sec` (default: 120s): Limits long-running thread times.
* **Proactive Rejection:** Checks limits *before* calling tools or compiling next steps, raising `PolicyLimitViolationError` to instantly break execution.

## Consequences
* **Pros:** Highly secure, prevents system-level resources exhaustion, minimizes cloud vendor budgets leakages.
* **Cons:** Introduces a policy-verification evaluation step before executing nodes in the DAG.
