# ADR-053: LangGraph Integration

## Status
Accepted

## Context
Standard agent graphs contain complex, cyclical state flows. Replacing our core `AgentRuntime` engine with an external vendor tool breaks overall platform consistency, complicates telemetry tracking, and creates tight vendor lock-in.

## Decision
We establish a clean, non-obtrusive LangGraph adapter model:
* **`LangGraphAdapter` Executor:** LangGraph operates strictly as an execution adapter *under* the orchestrating lifecycle of `AgentRuntime`.
* **Stateful Adapter Nodes:** Nodes are implemented as lightweight task closures (`MemoryNode`, `RetrievalNode`, `ToolNode`, `LLMNode`) that map properties onto the standard platform `RuntimeContext` and state structures.

## Consequences
* **Pros:** Complete design consistency, telemetry logging of step latencies, safe context passing, and zero replacement risk of the runtime.
* **Cons:** Nodes must write output dictionaries conforming to LangGraph state structures.
