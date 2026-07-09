from collections.abc import Callable
from functools import wraps
from typing import Any

from agentsphere.common.exceptions import ForbiddenError

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "superadmin": ["*"],
    "admin": [
        "tenants:read",
        "tenants:write",
        "users:read",
        "users:write",
        "conversations:read",
        "conversations:write",
        "documents:read",
        "documents:write",
        "tools:read",
        "tools:write",
        "analytics:read",
    ],
    "editor": [
        "conversations:read",
        "conversations:write",
        "documents:read",
        "documents:write",
    ],
    "viewer": [
        "conversations:read",
        "analytics:read",
    ],
}

ROLE_HIERARCHY: dict[str, int] = {
    "viewer": 0,
    "editor": 1,
    "admin": 2,
    "superadmin": 3,
}


def has_permission(role: str, permission: str) -> bool:
    permissions = ROLE_PERMISSIONS.get(role, [])
    if "*" in permissions:
        return True
    return permission in permissions


def require_permission(permission: str) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            request = kwargs.get("request")
            if request and hasattr(request.state, "role"):
                role = request.state.role
                if has_permission(role, permission):
                    return await func(*args, **kwargs)
            raise ForbiddenError(f"Missing required permission: {permission}")
        return wrapper
    return decorator
