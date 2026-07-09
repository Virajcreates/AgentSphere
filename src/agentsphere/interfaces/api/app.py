from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from agentsphere.common.exceptions import AppError
from agentsphere.common.models import ErrorResponse
from agentsphere.common.request_context import get_request_context
from agentsphere.config.logging import setup_logging
from agentsphere.infrastructure.observability.metrics import mount_metrics_endpoint
from agentsphere.infrastructure.observability.tracing import setup_tracing
from agentsphere.infrastructure.persistence.migrations.check import check_migration_state
from agentsphere.interfaces.api.middleware.auth import AuthMiddleware
from agentsphere.interfaces.api.middleware.logging import LoggingMiddleware
from agentsphere.interfaces.api.middleware.rate_limit import RateLimitMiddleware
from agentsphere.interfaces.api.middleware.request_context import RequestContextMiddleware
from agentsphere.interfaces.api.middleware.tenant import TenantMiddleware
from agentsphere.interfaces.api.middleware.version_header import VersionHeaderMiddleware
from agentsphere.interfaces.api.routes.agents import router as agents_router
from agentsphere.interfaces.api.routes.analytics import router as analytics_router
from agentsphere.interfaces.api.routes.auth import auth_router
from agentsphere.interfaces.api.routes.benchmarks import router as benchmarks_router
from agentsphere.interfaces.api.routes.chunks import router as chunks_router
from agentsphere.interfaces.api.routes.conversations import router as conversations_router
from agentsphere.interfaces.api.routes.health import health_router
from agentsphere.interfaces.api.routes.knowledge import router as knowledge_router
from agentsphere.interfaces.api.routes.prompts import router as prompts_router
from agentsphere.interfaces.api.routes.replay import router as replay_router
from agentsphere.interfaces.api.routes.search import router as search_router
from agentsphere.interfaces.api.routes.tenants import tenant_router
from agentsphere.interfaces.api.routes.version import version_router
from agentsphere.interfaces.container import init_container

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, Any]:
    container = init_container()
    settings = container.core.settings()

    setup_logging(settings.LOG_LEVEL)
    setup_tracing(settings.OTEL_SERVICE_NAME, settings.OTEL_EXPORTER_OTLP_ENDPOINT)

    if settings.PROMETHEUS_ENABLED:
        mount_metrics_endpoint(application)

    config_errors = settings.validate_required()
    for err in config_errors:
        logger.warning("configuration_issue", detail=err)

    db_initialized = False
    with suppress(Exception):
        await container.core.db().init(
            settings.DATABASE_URL,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
        )
        db_initialized = True

    redis_initialized = False
    with suppress(Exception):
        await container.core.redis().init(settings.REDIS_URL)
        redis_initialized = True

    application.state.container = container

    if db_initialized:
        db_ok = await container.core.db().health_check()
        logger.info("db_health_check", status="ok" if db_ok else "unreachable")
        if db_ok:
            migration_ok, migration_msg = await check_migration_state(container.core.db())
            if migration_ok:
                logger.info("migration_state", detail=migration_msg)
            else:
                logger.warning("migration_state", detail=migration_msg)

    if redis_initialized:
        redis_ok = await container.core.redis().health_check()
        logger.info("redis_health_check", status="ok" if redis_ok else "unreachable")

    if settings.ENVIRONMENT == "production":
        if config_errors:
            raise RuntimeError(
                f"Configuration validation failed: {'; '.join(config_errors)}"
            )
        if not db_initialized:
            raise RuntimeError("Database connection failed")
        if not redis_initialized:
            raise RuntimeError("Redis connection failed")

    yield

    await container.core.db().close()
    await container.core.redis().close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="AgentSphere API",
        version="0.1.0",
        docs_url="/docs",
        lifespan=lifespan,
        swagger_ui_parameters={"tagsSorter": "alpha"},
    )

    app.add_middleware(VersionHeaderMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(TenantMiddleware)
    app.add_middleware(RateLimitMiddleware)

    @app.exception_handler(AppError)
    async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
        ctx = get_request_context()
        error = ErrorResponse(
            type=exc.type_url,
            title=exc.title,
            status=exc.status,
            detail=exc.detail,
            instance=str(request.url),
            errors=exc.errors,
            trace_id=ctx.trace_id if ctx else "",
        )
        return JSONResponse(
            status_code=exc.status,
            content=error.model_dump(exclude_none=True),
            headers=getattr(exc, "headers", {}),
        )

    @app.exception_handler(Exception)
    async def internal_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        ctx = get_request_context()
        error = ErrorResponse(
            type="about:blank",
            title="Internal Server Error",
            status=500,
            detail="An unexpected error occurred",
            instance=str(request.url),
            trace_id=ctx.trace_id if ctx else "",
        )
        return JSONResponse(
            status_code=500,
            content=error.model_dump(exclude_none=True),
        )

    app.include_router(health_router, prefix="", tags=["Health"])
    app.include_router(version_router, prefix="", tags=["Version"])
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(tenant_router, prefix="/api/v1/tenants", tags=["Tenants"])
    app.include_router(conversations_router)
    app.include_router(knowledge_router)
    app.include_router(agents_router)
    app.include_router(prompts_router)
    app.include_router(benchmarks_router)
    app.include_router(analytics_router)
    app.include_router(replay_router)
    app.include_router(chunks_router)
    app.include_router(search_router)

    return app


app = create_app()
