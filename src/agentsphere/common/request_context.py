from contextvars import ContextVar
from dataclasses import dataclass
from uuid import UUID


@dataclass
class RequestContext:
    request_id: str = ""
    trace_id: str = ""
    correlation_id: str = ""
    tenant_id: UUID | None = None
    user_id: UUID | None = None
    conversation_id: UUID | None = None


_request_context: ContextVar[RequestContext | None] = ContextVar("request_context", default=None)


def get_request_context() -> RequestContext | None:
    return _request_context.get()


def set_request_context(ctx: RequestContext) -> None:
    _request_context.set(ctx)


def reset_request_context() -> None:
    _request_context.set(None)
