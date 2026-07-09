from uuid import UUID

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from agentsphere.common.request_context import get_request_context
from agentsphere.interfaces.container import get_container

PUBLIC_PATHS = {"/health", "/ready", "/healthz", "/version", "/docs", "/openapi.json"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            container = get_container()
            payload = await container.auth.jwt_handler().validate_token(token)
            if payload:
                request.state.user_id = UUID(payload["sub"])
                request.state.tenant_id = UUID(payload["tenant_id"])
                request.state.role = payload.get("role", "viewer")
                ctx = get_request_context()
                if ctx:
                    ctx.user_id = UUID(payload["sub"])
                    ctx.tenant_id = UUID(payload["tenant_id"])

        return await call_next(request)
