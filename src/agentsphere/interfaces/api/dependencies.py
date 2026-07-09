from collections.abc import Callable, Coroutine
from typing import Any
from uuid import UUID

from fastapi import Depends, Request

from agentsphere.common.exceptions import ForbiddenError, UnauthorizedError
from agentsphere.infrastructure.auth.rbac import has_permission


async def get_current_user_id(request: Request) -> UUID:
    if not hasattr(request.state, "user_id"):
        raise UnauthorizedError("Authentication required")
    return UUID(request.state.user_id)


async def get_current_tenant_id(request: Request) -> UUID:
    if not hasattr(request.state, "tenant_id"):
        raise UnauthorizedError("Tenant context required")
    return UUID(request.state.tenant_id)


async def get_current_role(request: Request) -> str:
    if not hasattr(request.state, "role"):
        raise UnauthorizedError("Authentication required")
    return str(request.state.role)


def require_permission(permission: str) -> Callable[..., Coroutine[Any, Any, None]]:
    async def checker(request: Request, role: str = Depends(get_current_role)) -> None:
        if not has_permission(role, permission):
            raise ForbiddenError(f"Missing required permission: {permission}")
    return checker
