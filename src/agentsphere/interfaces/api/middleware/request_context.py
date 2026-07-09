from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from agentsphere.common.request_context import get_request_context


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        ctx = get_request_context()
        if ctx:
            request.state.request_id = ctx.request_id
            request.state.trace_id = ctx.trace_id
            request.state.correlation_id = ctx.correlation_id
        response = await call_next(request)
        return response
