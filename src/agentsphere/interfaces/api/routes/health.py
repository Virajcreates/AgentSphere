from typing import Any

from fastapi import APIRouter, Request

from agentsphere.interfaces.container import get_container

health_router = APIRouter()


@health_router.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ok"}


@health_router.get("/ready")
async def ready(request: Request) -> dict[str, Any]:
    container = get_container()
    db_ok = await container.core.db().health_check()
    redis_ok = await container.core.redis().health_check()
    return {
        "status": "ok" if (db_ok and redis_ok) else "degraded",
        "checks": {
            "database": "ok" if db_ok else "unreachable",
            "redis": "ok" if redis_ok else "unreachable",
        },
    }


@health_router.get("/healthz")
async def healthz(request: Request) -> dict[str, Any]:
    container = get_container()
    db_ok = await container.core.db().health_check()
    redis_ok = await container.core.redis().health_check()
    settings = container.core.settings()
    return {
        "status": "ok" if (db_ok and redis_ok) else "degraded",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {
            "database": {"status": "ok" if db_ok else "unreachable"},
            "redis": {"status": "ok" if redis_ok else "unreachable"},
        },
    }
