# AgentSphere Phase 1 — Core Platform Infrastructure

## Overview

Phase 1 delivers the complete backend skeleton for a multi-tenant conversational AI platform. Architecture is frozen per `v1.1`. Stack: **FastAPI + PostgreSQL (pgvector) + Redis + JWT + RBAC + dependency-injector + OpenTelemetry + Docker**.

---

## Project Structure

```
src/agentsphere/
├── __init__.py
├── __main__.py                  # uvicorn entry point
├── application/
│   ├── ports/                   # Port interfaces
│   │   ├── auth_provider.py     #   AuthProvider protocol
│   │   ├── repositories.py      #   Tenant/User/ApiKey repository protocols
│   │   └── unit_of_work.py      #   UnitOfWork protocol
│   └── use_cases/
│       ├── auth/                # Login, RefreshToken, CreateApiKey, RevokeApiKey
│       └── tenant/              # CreateTenant, GetTenant, UpdateTenant
├── common/
│   ├── exceptions.py            # RFC7807 Problem Details hierarchy
│   ├── models.py                # BaseResponse, SuccessResponse, ErrorResponse, PaginatedResponse
│   ├── request_context.py       # contextvars: request_id, trace_id, tenant_id, user_id, etc.
│   └── uuid7.py                 # UUIDv7 generator (timestamp-prefixed, sortable)
├── config/
│   ├── database.py              # DatabaseManager: async engine, session factory, health check
│   ├── logging.py               # Structlog setup (auto-injects request_id, trace_id, tenant_id, conversation_id)
│   ├── redis.py                 # RedisManager: connection pool, health check
│   └── settings.py              # Typed settings: Database, Redis, Auth, Telemetry, RateLimit
├── domain/
│   ├── entities/                # TenantEntity, UserEntity, ApiKeyEntity
│   ├── events/                  # DomainEvents — DomainEvent base dataclass (Phase 2 ready)
│   ├── models/                  # SQLAlchemy ORM models (tenant, user, api_key)
│   └── value_objects/           # Email, TenantId, UserId
├── infrastructure/
│   ├── auth/
│   │   ├── api_key_handler.py   # Prefix + hashed API keys (SHA-256)
│   │   ├── jwt_handler.py       # Access/refresh JWT tokens
│   │   ├── password_hasher.py   # Argon2 password hashing
│   │   └── rbac.py              # Role-permission matrix (superadmin/admin/editor/viewer)
│   ├── event_bus/               # Stub (reserved)
│   ├── observability/
│   │   ├── langsmith.py         # Stub (reserved)
│   │   ├── logging.py           # Stub (reserved)
│   │   ├── metrics.py           # Prometheus /metrics endpoint
│   │   └── tracing.py           # OpenTelemetry setup
│   └── persistence/
│       ├── migrations/
│       │   ├── check.py         # Migration state checker
│       │   ├── env.py           # Alembic environment
│       │   └── versions/
│       │       └── 001_initial.py  # tenant, user, api_key tables + pgvector
│       ├── repositories/
│       │   ├── base_repository.py  # BaseRepository with tenant scoping
│       │   ├── tenant_repository.py  # (satisfies TenantRepositoryProtocol)
│       │   ├── user_repository.py    # (satisfies UserRepositoryProtocol)
│       │   └── api_key_repository.py # (satisfies ApiKeyRepositoryProtocol)
│       └── unit_of_work.py      # SQLAlchemyUnitOfWork (implements UnitOfWork protocol)
├── interfaces/
│   ├── api/
│   │   ├── app.py               # FastAPI factory + lifespan + middleware + exception handlers
│   │   ├── dependencies.py      # FastAPI DI dependencies
│   │   ├── exceptions.py        # FastAPI exception handlers
│   │   ├── middleware/
│   │   │   ├── auth.py          # JWT/API key authentication
│   │   │   ├── logging.py       # Structured request logging
│   │   │   ├── rate_limit.py    # Token-bucket rate limiter (Redis-backed)
│   │   │   ├── request_context.py  # Request-scoped context vars
│   │   │   ├── tenant.py        # Tenant resolution from header/token
│   │   │   └── version_header.py  # X-AgentSphere-Version on every response
│   │   └── routes/
│   │       ├── auth.py          # POST /login, /refresh, /api-keys, DELETE /api-keys
│   │       ├── health.py        # GET /health, /ready, /healthz
│   │       ├── tenants.py       # POST/GET/PATCH /tenants
│   │       └── version.py       # GET /version
│   └── container.py             # dependency-injector wiring (Core, Auth, UseCases containers)
├── scripts/
│   └── seed.py                  # Demo tenant + admin user seeder
```

---

## Architecture Decisions

| Concern | Decision |
|---------|----------|
| **DI** | `dependency-injector` with `DeclarativeContainer` hierarchy: `Core` → settings/db/redis, `Auth` → jwt/password/api-key handlers, `UseCases` → all 7 use cases wired with `db` + auth dependencies |
| **Database** | `DatabaseManager` singleton — creates async engine + `async_sessionmaker` on `init()`. Use cases call `await db.get_session()` to obtain sessions and create repositories inline |
| **Repository Protocols** | `TenantRepositoryProtocol`, `UserRepositoryProtocol`, `ApiKeyRepositoryProtocol` defined in `application/ports/repositories.py`. SQLAlchemy implementations declare conformance via multiple inheritance |
| **UnitOfWork Protocol** | `UnitOfWork` as `AsyncContextManager` Protocol in `application/ports/unit_of_work.py`. `SQLAlchemyUnitOfWork` implements it |
| **Domain Events** | `DomainEvent` base dataclass in `domain/events/base.py` — event_id (UUID), event_type (class name), occurred_at (UTC). No business events yet |
| **Configuration** | Typed sub-settings: `DatabaseSettings`, `RedisSettings`, `AuthSettings`, `TelemetrySettings`, `RateLimitSettings`. Composite `Settings` inherits all. `validate_required()` checks production-critical values |
| **Startup Validation** | Lifespan validates config, checks DB/Redis connectivity, inspects migration state. Logs warnings on non-critical failures. Raises `RuntimeError` in production for critical failures |
| **Response Headers** | `VersionHeaderMiddleware` adds `X-AgentSphere-Version: 0.1.0` to every HTTP response |
| **Structured Logging** | `_add_request_context` processor auto-injects `request_id`, `trace_id`, `correlation_id`, `tenant_id`, `user_id`, `conversation_id` into every log entry via structlog |
| **UUIDs** | UUIDv7 — 48-bit ms timestamp + 74-bit random + version/variant. Sortable, indexable, no central coordinator |
| **Errors** | RFC7807 `application/problem+json` via `AppError` → `ErrorResponse` model |
| **Auth** | Dual-mode: JWT bearer tokens (access 15m, refresh 7d) and API keys (prefixed SHA-256 hash). RBAC matrix: superadmin > admin > editor > viewer |
| **Tenancy** | Multi-tenant via `TenantMiddleware` — resolves tenant_id from `X-Tenant-ID` header or JWT claim. `BaseRepository` auto-scopes queries with tenant filter |
| **Request Context** | `contextvars`: request_id, trace_id, correlation_id, tenant_id, user_id, conversation_id — set by middleware, consumed by use cases and logging |
| **Observability** | Structured logging (structlog), OpenTelemetry tracing, Prometheus metrics |
| **Rate Limiting** | Token-bucket per tenant in Redis (configurable requests/window) |
| **Graceful Degradation** | Lifespan suppresses DB/Redis init errors in non-production environments — health checks report actual status |
| **OpenAPI** | Endpoints grouped under tags: `Authentication`, `Tenants`, `Health`, `Version` |

---

## Database Schema

### `tenant`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID (v7) | PK |
| name | VARCHAR(255) | NOT NULL |
| slug | VARCHAR(100) | UNIQUE, NOT NULL |
| settings | JSONB | |
| is_active | BOOLEAN | DEFAULT true |
| created_at, updated_at | TIMESTAMPTZ | |

### `user`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID (v7) | PK |
| tenant_id | UUID | FK → tenant, NOT NULL |
| email | VARCHAR(255) | NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| display_name | VARCHAR(255) | |
| role | VARCHAR(50) | NOT NULL |
| is_active | BOOLEAN | DEFAULT true |
| created_at, updated_at | TIMESTAMPTZ | |

### `api_key`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID (v7) | PK |
| tenant_id | UUID | FK → tenant, NOT NULL |
| key_prefix | VARCHAR(20) | NOT NULL |
| key_hash | VARCHAR(64) | NOT NULL |
| name | VARCHAR(255) | NOT NULL |
| scopes | JSONB | |
| is_active | BOOLEAN | DEFAULT true |
| last_used_at | TIMESTAMPTZ | |
| created_at, updated_at | TIMESTAMPTZ | |

---

## API Endpoints

| Method | Path | Auth | OpenAPI Tag | Description |
|--------|------|------|-------------|-------------|
| GET | `/health` | None | Health | Basic health check |
| GET | `/ready` | None | Health | Readiness with DB/Redis checks |
| GET | `/healthz` | None | Health | Full healthz (version + checks) |
| GET | `/version` | None | Version | App version + environment |
| POST | `/api/v1/auth/login` | None | Authentication | Login with email + password |
| POST | `/api/v1/auth/refresh` | None | Authentication | Refresh access token |
| POST | `/api/v1/auth/api-keys` | JWT | Authentication | Create API key |
| GET | `/api/v1/auth/api-keys` | JWT | Authentication | List API keys |
| DELETE | `/api/v1/auth/api-keys/{id}` | JWT | Authentication | Revoke API key |
| POST | `/api/v1/tenants` | None | Tenants | Create tenant |
| GET | `/api/v1/tenants/{id}` | JWT | Tenants | Get tenant |
| PATCH | `/api/v1/tenants/{id}` | JWT | Tenants | Update tenant |

---

## Middleware Stack (order)

1. **VersionHeaderMiddleware** — adds `X-AgentSphere-Version` to every response (outermost)
2. **LoggingMiddleware** — structured request/response logging via structlog
3. **RequestContextMiddleware** — initializes contextvars for each request
4. **AuthMiddleware** — validates JWT or API key, sets `request.state.user_id`
5. **TenantMiddleware** — resolves tenant from header or JWT claim
6. **RateLimitMiddleware** — token-bucket rate limiting via Redis (innermost)

---

## Tooling & CI/CD

| Tool | Purpose | Status |
|------|---------|--------|
| **Ruff** | Linting (E, F, I, N, W, UP, B, SIM, PT, RUF) | ✅ Pass (0 errors) |
| **Mypy** | Type checking (`--strict`, 81 files) | ✅ Pass (0 errors) |
| **Pytest** | 51 tests (36 unit/integration + 3 architecture + 12 container wiring) | ✅ Pass (2 DB-dependent skipped) |
| **Coverage** | 60% (threshold 60%, DB-requiring paths excluded) | ✅ Pass |
| **Bandit** | Security scan — 4 expected findings (dev only) | ✅ Pass |
| **pip-audit** | Dependency vulnerability check (0 known) | ✅ Pass |
| **Docker** | `Dockerfile.api`, `docker-compose.yml` (postgres, redis, api, pgadmin) | ✅ Ready |
| **CI** | `.github/workflows/ci.yml`, `.pre-commit-config.yaml`, `Makefile` | ✅ Ready |
| **Architecture Tests** | Clean Architecture dependency rules enforced | ✅ 3 tests pass |

### CI Pipeline (`.github/workflows/ci.yml`)
```
Ruff → Mypy → Pytest (unit + coverage + architecture) → Bandit → pip-audit → detect-secrets
```

---

## Architecture Test Rules

| Rule | Test | Status |
|------|------|--------|
| Domain must not depend on Infrastructure or Interfaces | `test_domain_does_not_depend_on_infrastructure_or_interfaces` | ✅ Pass |
| Application must not depend on Interfaces or Infrastructure | `test_application_does_not_depend_on_interfaces_or_infrastructure` | ✅ Pass |
| Infrastructure must not depend on API layer | `test_infrastructure_does_not_depend_on_api_layer` | ✅ Pass |

Note: Cross-cutting layers (`common`, `config`) are allowed for all layers.
All layers fully satisfy Clean Architecture rules — no known violations.

---

## Docker Setup

```yaml
services:
  postgres:    # postgres:16-alpine, port 5432, pgvector, health check via pg_isready
  redis:       # redis:7-alpine, port 6379, health check via redis-cli ping
  api:         # Dockerfile.api, port 8000, depends on postgres+redis, health check /health
  pgadmin:     # dpage/pgadmin4, port 5050
```

---

## Known Gaps (Phase 2+)

- No WebSocket support (planned for Phase 2)
- No agent execution engine (Phase 3)
- No conversation/message models or endpoints (reserved UUIDs in schema)
- No file storage / document ingestion
- No billing / usage tracking
- Integration tests require running PostgreSQL (marked `@pytest.mark.needs_db`)

---

## Test Summary

```
51 passed, 2 deselected (needs_db) in 30.12s
Coverage: 60.11% (threshold: 60%)
Architecture: 3/3 tests pass (0 known violations)
Container wiring: 12/12 tests pass
Ruff: 0 errors
Mypy: 0 errors in 81 source files
Bandit: 4 findings (all expected for dev)
```

To run with database: `docker compose up -d postgres redis` then `pytest tests/ -m "needs_db"`.

---

## Quick Start

```bash
cp .env.example .env       # configure database/redis URLs
docker compose up -d       # start postgres + redis
uv sync                    # install dependencies
make migrate               # run alembic migrations
make seed                  # create demo tenant + admin user
make dev                   # start uvicorn on :8000
make test                  # run tests (without DB)
make test-architecture     # run clean architecture tests
```
