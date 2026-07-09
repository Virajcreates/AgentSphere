from typing import Any

from fastapi import APIRouter, Request

version_router = APIRouter()


@version_router.get("/version")
async def version(request: Request) -> dict[str, Any]:
    container = request.app.state.container
    settings = container.core.settings()
    return {
        "version": settings.APP_VERSION,
        "git_commit": settings.GIT_COMMIT,
        "environment": settings.ENVIRONMENT,
        "build_timestamp": settings.APP_BUILD_TIMESTAMP,
    }
