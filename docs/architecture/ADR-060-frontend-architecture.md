# ADR-060: Frontend Architecture

## Status
Accepted

## Context
As client dashboards expand, loose components and scattered fetch states lead to file duplicates, circular inclusions, and fragile network layers.

## Decision
We establish a professional **Feature-Based Frontend Architecture**:
* **Centralized API SDK:** The web app routes network calls exclusively through the SDK (`web/lib/api/`). Raw API fetch is prohibited in Next pages.
* **OpenAPI Types Generation:** Autogenerates types from Python FastAPI schema, saving them in `web/types/` (ensuring 0 manual duplication).
* **Next.js API BFF Layer:** Intercepts Next `/api/...` routes, forwarding them to FastAPI, centralizing tracing IDs and cache mappings.
* **Feature Boundaries:** Groups dashboard, prompts, and play panels strictly under local feature scopes (`features/`).

## Consequences
* **Pros:** Bulletproof client safety, clean boundaries, simple onboarding, and guaranteed typings consistency.
* **Cons:** Requires running the schema typings generator task when changing Python contracts.
