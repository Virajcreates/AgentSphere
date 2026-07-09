import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from agentsphere.common.request_context import RequestContext, set_request_context


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        ctx = RequestContext(
            request_id=str(uuid.uuid4()),
            trace_id=str(uuid.uuid4()),
            correlation_id=request.headers.get("X-Correlation-ID", ""),
        )
        set_request_context(ctx)
        response = await call_next(request)
        return response
