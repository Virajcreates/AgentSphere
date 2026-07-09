import logging
from collections.abc import MutableMapping
from typing import Any

import structlog

from agentsphere.common.request_context import get_request_context


def setup_logging(log_level: str = "INFO") -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            timestamper,
            _add_request_context,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
        force=True,
    )


def _add_request_context(
    logger: Any, method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    ctx = get_request_context()
    if ctx:
        event_dict["request_id"] = ctx.request_id
        event_dict["trace_id"] = ctx.trace_id
        event_dict["correlation_id"] = ctx.correlation_id
        if ctx.tenant_id:
            event_dict["tenant_id"] = str(ctx.tenant_id)
        if ctx.user_id:
            event_dict["user_id"] = str(ctx.user_id)
        if ctx.conversation_id:
            event_dict["conversation_id"] = str(ctx.conversation_id)
    return event_dict
