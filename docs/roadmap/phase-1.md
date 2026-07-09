# Phase 1 — Core Platform Infrastructure

## Objectives

Establish the foundational infrastructure for AgentSphere: a working FastAPI application with authentication, tenant management, database, configuration, CI/CD, and observability. This phase delivers a running, testable API layer that all subsequent phases build upon.

## Deliverables

| Deliverable | Description |
|-------------|-------------|
| FastAPI Application Shell | Project structure, entry point, dependency injection container |
| Configuration Management | Pydantic Settings with `.env` support, environment-specific profiles |
| PostgreSQL + pgvector Setup | Database initialization, Alembic migrations, base schema (tenants, users, api_keys) |
| Redis Integration | Connection pool, health check, configuration |
| Authentication & Authorization | JWT issue/refresh/validate, Argon2 password hashing, API key auth |
| Tenant Management CRUD | Create, read, update, delete tenants with UUID primary keys |
| User Management CRUD | Create, read, update users; RBAC roles (admin, agent, viewer) |
| Middleware Stack | AuthMiddleware (JWT/API key extraction), TenantMiddleware (tenant loading + RLS), RateLimitMiddleware (token bucket per tenant), LoggingMiddleware (correlation IDs) |
| Structured Logging | JSON logging with `trace_id`, `span_id`, `tenant_id`, `conversation_id` |
| Health Check Endpoints | `/health` (liveness), `/ready` (readiness — DB + Redis), `/healthz` (detailed) |
| CI/CD Pipeline | GitHub Actions: Ruff, mypy --strict, pytest, pip-audit, bandit, gitleaks, detect-secrets |
| Pre-commit Hooks | ruff, ruff-format, isort, mypy, gitleaks, detect-secrets |
| Docker Compose | `docker-compose.yml` for local dev (API, PostgreSQL, Redis, pgAdmin) |
| Makefile | `make dev`, `make test`, `make lint`, `make migrate`, `make seed` |
| Unit Tests | Minimum 80% coverage on all modules above |
| OpenAPI Spec | Auto-generated via FastAPI routes, served at `/api/v1/openapi.json` |

## Dependencies

- Python 3.11+
- PostgreSQL 15+ with pgvector extension
- Redis 7+
- Docker & Docker Compose (local dev)
- No external AI provider dependencies

## Risks

| Risk | Mitigation |
|------|------------|
| PostgreSQL RLS complexity | Start with application-level tenant scoping; add RLS as defense-in-depth in Phase 2 |
| JWT secret management | Use Pydantic Settings with `SecretsManager` class; fail fast if JWT_SECRET not set |
| Redis not available in CI | Mock Redis with `fakeredis` for unit tests; integration tests require Docker |
| Migration conflicts between team members | Use Alembic auto-generation; enforce one migration per PR |

## Acceptance Criteria

- [ ] `GET /health` returns 200 with `{"status": "ok"}`
- [ ] `GET /ready` returns 200 only when PostgreSQL and Redis are reachable
- [ ] `POST /api/v1/auth/login` returns a valid JWT for valid credentials
- [ ] `POST /api/v1/auth/login` returns 401 for invalid credentials
- [ ] `GET /api/v1/tenants` returns the authenticated user's tenant (scoped)
- [ ] `POST /api/v1/tenants` creates a new tenant (superadmin only)
- [ ] JWT tokens expire after configured TTL (default 15 min)
- [ ] API keys can be created, listed, and revoked
- [ ] Requests without valid auth return 401
- [ ] Requests from tenant A cannot access tenant B's data
- [ ] Rate limiting returns 429 when exceeded
- [ ] All logs are valid JSON with the expected fields
- [ ] `ruff check src/` passes with 0 errors
- [ ] `mypy --strict src/` passes with 0 errors
- [ ] `pytest tests/ -v --cov=src --cov-fail-under=80` passes