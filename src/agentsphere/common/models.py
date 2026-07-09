from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel):
    pass


class SuccessResponse[T](BaseResponse):
    data: T
    message: str = "Success"


class ErrorResponse(BaseResponse):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str = ""
    errors: dict[str, list[str]] | None = None
    trace_id: str = ""


class PaginatedResponse[T](BaseResponse):
    items: list[T]
    total: int
    page: int = 1
    page_size: int = 20
    next_page: str | None = None
    previous_page: str | None = None
