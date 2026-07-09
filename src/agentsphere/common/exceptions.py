from uuid import UUID


class AppError(Exception):
    def __init__(
        self,
        title: str,
        status: int,
        detail: str,
        type_url: str = "about:blank",
        instance: str = "",
        errors: dict[str, list[str]] | None = None,
    ):
        self.title = title
        self.status = status
        self.detail = detail
        self.type_url = type_url
        self.instance = instance
        self.errors = errors


class NotFoundError(AppError):
    def __init__(self, entity: str, entity_id: UUID | str, instance: str = ""):
        super().__init__(
            title="Resource Not Found",
            status=404,
            detail=f"{entity} with id '{entity_id}' not found",
            instance=instance,
        )


class UnauthorizedError(AppError):
    def __init__(self, detail: str = "Authentication required", instance: str = ""):
        super().__init__(
            title="Unauthorized",
            status=401,
            detail=detail,
            instance=instance,
        )


class ForbiddenError(AppError):
    def __init__(self, detail: str = "Insufficient permissions", instance: str = ""):
        super().__init__(
            title="Forbidden",
            status=403,
            detail=detail,
            instance=instance,
        )


class ConflictError(AppError):
    def __init__(self, detail: str, instance: str = ""):
        super().__init__(
            title="Conflict",
            status=409,
            detail=detail,
            instance=instance,
        )


class ValidationError(AppError):
    def __init__(self, detail: str, errors: dict[str, list[str]] | None = None, instance: str = ""):
        super().__init__(
            title="Validation Error",
            status=422,
            detail=detail,
            instance=instance,
            errors=errors,
        )


class RateLimitError(AppError):
    def __init__(self, retry_after: int, instance: str = ""):
        super().__init__(
            title="Too Many Requests",
            status=429,
            detail=f"Rate limit exceeded. Retry after {retry_after} seconds.",
            instance=instance,
        )
        self.retry_after = retry_after
