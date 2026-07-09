# Phase 4 — Business Integration Layer

## Objectives

Implement the adapter-based business integration layer with ShoeFusion as the first tenant. Deliver working tool definitions, REST client, credential management, and resilient execution.

## Deliverables

| Deliverable | Description |
|-------------|-------------|
| Integration Protocol | `IntegrationProtocol` — `execute_tool()`, `health_check()`, `get_supported_tools()` |
| Integration Registry | Register, discover, and route tools to adapters by tenant |
| ShoeFusion REST Client | Async HTTP client with retries, timeout, auth header injection |
| ShoeFusion Adapter | Implements `IntegrationProtocol`, maps tool calls to ShoeFusion API endpoints |
| Tool: `get_product` | Fetch product by ID or search by query |
| Tool: `get_order` | Fetch order by ID or search by customer email |
| Tool: `check_inventory` | Check stock levels for product SKU + size/color |
| Tool: `create_ticket` | Create customer support ticket with idempotency key |
| Tool: `get_customer` | Fetch customer profile by ID |
| Credential Management | Encrypted storage of API keys per integration; rotation support |
| Tool Execution History | Persist tool_name, parameters, result, status, timestamps |
| Structured Error Handling | All failures return `ToolResult` with `ToolError` (code, message, retryable, retry_after) |
| Idempotency Middleware | Mutating tools check idempotency_key before execution |
| Unit Tests | Each tool, adapter, registry, credential manager |
| Integration Tests | Against ShoeFusion API (staging or mock server) |

## Dependencies

- Phase 1 (DB, auth, encrypted credential storage)
- Phase 2 (tool execution node, tool registry)
- ShoeFusion REST API (must implement required endpoints)
- `httpx` (async HTTP client)

## Risks

| Risk | Mitigation |
|------|------------|
| ShoeFusion API unavailable | Return `INTEGRATION_UNAVAILABLE` error; cache stale data if available |
| API rate limits | Implement per-tenant rate limiter; exponential backoff + circuit breaker |
| Credential exposure | Encrypt at rest (AES-256-GCM); never log; mask in responses |
| Breaking API changes | Versioned tools; pin to known-working API version if available |

## Acceptance Criteria

- [ ] `get_product("SKU-123")` returns product details
- [ ] `get_order("ORD-456")` returns order status
- [ ] `check_inventory("SKU-123", "10", "Black")` returns stock count
- [ ] `create_ticket(...)` creates ticket and returns ticket ID
- [ ] Same `create_ticket` call with same idempotency_key returns existing ticket (no duplicate)
- [ ] ShoeFusion API returning 503 causes `INTEGRATION_UNAVAILABLE` error
- [ ] Invalid parameters cause `INVALID_PARAMETERS` error
- [ ] Executed tool calls are stored with full parameters and results
- [ ] Tenant credentials can be configured, rotated, and tested via API