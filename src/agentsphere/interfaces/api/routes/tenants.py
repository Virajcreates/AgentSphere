from typing import Any
from uuid import UUID

from fastapi import APIRouter, Request

from agentsphere.common.exceptions import UnauthorizedError

tenant_router = APIRouter()


@tenant_router.post("")
async def create_tenant(request: Request, body: dict[str, Any]) -> dict[str, Any]:
    container = request.app.state.container
    use_case = container.use_cases.create_tenant()
    result = await use_case.execute(
        name=body.get("name", ""),
        slug=body.get("slug", ""),
    )
    return {"data": result, "message": "Tenant created"}


@tenant_router.get("")
async def get_current_tenant(request: Request) -> dict[str, Any]:
    container = request.app.state.container
    tenant_id = request.state.tenant_id if hasattr(request.state, "tenant_id") else None
    if not tenant_id:
        raise UnauthorizedError("Tenant ID required")
    use_case = container.use_cases.get_tenant()
    result = await use_case.execute(tenant_id=UUID(str(tenant_id)))
    return {"data": result, "message": "Success"}


@tenant_router.get("/{tenant_id}")
async def get_tenant(request: Request, tenant_id: str) -> dict[str, Any]:
    container = request.app.state.container
    use_case = container.use_cases.get_tenant()
    result = await use_case.execute(tenant_id=UUID(tenant_id))
    return {"data": result, "message": "Success"}


@tenant_router.patch("/{tenant_id}")
async def update_tenant(request: Request, tenant_id: str, body: dict[str, Any]) -> dict[str, Any]:
    container = request.app.state.container
    use_case = container.use_cases.update_tenant()
    result = await use_case.execute(
        tenant_id=UUID(tenant_id),
        name=body.get("name"),
        settings=body.get("settings"),
    )
    return {"data": result, "message": "Tenant updated"}
