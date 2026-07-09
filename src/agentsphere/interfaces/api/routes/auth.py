from typing import Any
from uuid import UUID

from fastapi import APIRouter, Header, Request

from agentsphere.common.exceptions import UnauthorizedError
from agentsphere.infrastructure.persistence.repositories.api_key_repository import ApiKeyRepository

auth_router = APIRouter()


@auth_router.post("/login")
async def login(request: Request, body: dict[str, Any]) -> dict[str, Any]:
    container = request.app.state.container
    use_case = container.use_cases.login()
    result = await use_case.execute(
        email=body.get("email", ""),
        password=body.get("password", ""),
    )
    return {"data": result, "message": "Login successful"}


@auth_router.post("/refresh")
async def refresh(request: Request, body: dict[str, Any]) -> dict[str, Any]:
    container = request.app.state.container
    use_case = container.use_cases.refresh_token()
    result = await use_case.execute(
        refresh_token=body.get("refresh_token", ""),
    )
    return {"data": result, "message": "Token refreshed"}


@auth_router.post("/api-keys")
async def create_api_key(
    request: Request,
    body: dict[str, Any],
    x_tenant_id: str | None = Header(None),
) -> dict[str, Any]:
    container = request.app.state.container
    use_case = container.use_cases.create_api_key()
    tenant_id = (
        request.state.tenant_id if hasattr(request.state, "tenant_id") else UUID(x_tenant_id)
    )
    if not tenant_id:
        raise UnauthorizedError("Tenant ID required")
    result = await use_case.execute(
        tenant_id=UUID(str(tenant_id)),
        name=body.get("name", ""),
        scopes=body.get("scopes"),
    )
    return {"data": result, "message": "API key created"}


@auth_router.get("/api-keys")
async def list_api_keys(request: Request) -> dict[str, Any]:
    container = request.app.state.container
    tenant_id = request.state.tenant_id if hasattr(request.state, "tenant_id") else None
    if not tenant_id:
        raise UnauthorizedError("Tenant ID required")
    async with await container.core.db().get_session() as session:
        repo = ApiKeyRepository(session=session)
        keys = await repo.get_all(tenant_id=UUID(str(tenant_id)))
    return {"data": keys, "message": "Success"}


@auth_router.delete("/api-keys/{key_id}")
async def revoke_api_key(request: Request, key_id: str) -> dict[str, Any]:
    container = request.app.state.container
    tenant_id = request.state.tenant_id if hasattr(request.state, "tenant_id") else None
    if not tenant_id:
        raise UnauthorizedError("Tenant ID required")
    use_case = container.use_cases.revoke_api_key()
    await use_case.execute(api_key_id=UUID(key_id), tenant_id=UUID(str(tenant_id)))
    return {"data": None, "message": "API key revoked"}
