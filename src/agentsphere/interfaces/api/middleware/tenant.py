from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

PUBLIC_PATHS = {"/health", "/ready", "/healthz", "/version", "/docs", "/openapi.json"}


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)
        return await call_next(request)
