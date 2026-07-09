# ADR-035: Prompt Manager Implementation

## Status
Accepted

## Context
Prompts are standard configurations that must not be hardcoded in application code. They must support parameters rendering, semantic validation, version control, and multi-tenant custom overrides (e.g. tenant A wants a different system prompt for an agent than tenant B).

## Decision
We implement a highly flexible `PromptManager` class supporting:
* **Template Rendering:** Employs industry-standard `{{variable}}` style double curly braces templates.
* **Variable Validation:** A validation phase scans templates via regular expressions to verify no required variables are missing from prompt executions and unclosed brackets are flagged.
* **Tenant Overrides:** Templates are matched using keys `(tenant_id, namespace, template_name)` first, falling back to system defaults `(namespace, template_name, version)`.
* **Versioning:** Stored templates are tagged (e.g., `v1`, `v2`, `latest`), supporting rollbacks and A/B prompt testing.

## Consequences
* **Pros:** Strict validation reduces runtime runtime errors, decouples prompt engineering from backend code deploys, and enforces safe multi-tenant overrides.
* **Cons:** Keeps templates in memory for Phase 2; future phases should hook this manager to a database or Redis for persistent custom storage.
