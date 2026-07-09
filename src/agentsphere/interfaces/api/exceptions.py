from agentsphere.common.exceptions import AppError
from agentsphere.common.models import ErrorResponse
from agentsphere.common.request_context import get_request_context


def problem_detail_to_response(exc: AppError) -> ErrorResponse:
    ctx = get_request_context()
    return ErrorResponse(
        type=exc.type_url,
        title=exc.title,
        status=exc.status,
        detail=exc.detail,
        instance=exc.instance,
        errors=exc.errors,
        trace_id=ctx.trace_id if ctx else "",
    )
