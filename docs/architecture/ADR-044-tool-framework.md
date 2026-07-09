# ADR-044: Tool Framework

## Status
Accepted

## Context
AI agents are empowered by pluggable tool execution capabilities (APIs, searches, DB lookups). Unvalidated parameter models, lack of execution tracking, and direct vendor dependencies degrade systems security.

## Decision
We establish a clean, validated `Tool` and `ToolExecutor` architecture:
* **Tool Protocols and Definitions:** Tools are modeled as classes implementing the `Tool` Protocol. They expose a structured `ToolDefinition` metadata schema (input schemas, output schemas, timeout limits, idempotent flags, permissions, and side-effects constraints).
* **JSON Schema Input Validations:** The `ToolExecutor` validates inbound `ToolInvocation` parameters against the JSON Schema `input_schema` rules in the `ToolDefinition` before execution, raising `ToolValidationError` on mismatch.
* **Asynchronous Telemetry & Eventing:** Captures tool execution time (latencies) and publishes a `ToolExecuted` domain event through the common EventBus.

## Consequences
* **Pros:** Secure parameters validating, structured and isolated whitelisted tool registering, and complete operational observability.
* **Cons:** Boilerplate definition of parameters schema is required when writing new tools.
