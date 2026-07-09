from agentsphere.common.exceptions import AppError


class AIError(AppError):
    def __init__(
        self,
        detail: str,
        title: str = "AI Platform Error",
        status: int = 500,
        instance: str = "",
    ) -> None:
        super().__init__(title=title, status=status, detail=detail, instance=instance)

    def __str__(self) -> str:
        return self.detail


class ProviderError(AIError):
    def __init__(self, provider: str, detail: str, status: int = 502, instance: str = "") -> None:
        super().__init__(
            title="AI Provider Error",
            status=status,
            detail=f"Provider '{provider}' failed: {detail}",
            instance=instance,
        )


class ProviderConnectionError(ProviderError):
    def __init__(self, provider: str, detail: str, instance: str = "") -> None:
        super().__init__(
            provider=provider, detail=f"Connection failed: {detail}", status=503, instance=instance
        )


class ProviderTimeoutError(ProviderError):
    def __init__(self, provider: str, timeout: float, instance: str = "") -> None:
        super().__init__(
            provider=provider,
            detail=f"Request timed out after {timeout}s",
            status=504,
            instance=instance,
        )


class CircuitBreakerOpenError(AIError):
    def __init__(self, provider: str, cooldown_remaining: float, instance: str = "") -> None:
        super().__init__(
            title="Circuit Breaker Open",
            status=503,
            detail=(
                f"Circuit breaker for provider '{provider}' is OPEN. "
                f"Cooldown remaining: {cooldown_remaining:.1f}s"
            ),
            instance=instance,
        )


class ModelNotFoundError(AIError):
    def __init__(self, provider: str, model: str, instance: str = "") -> None:
        super().__init__(
            title="Model Not Found",
            status=404,
            detail=f"Model '{model}' not found for provider '{provider}'",
            instance=instance,
        )


class PromptValidationError(AIError):
    def __init__(self, detail: str, instance: str = "") -> None:
        super().__init__(
            title="Prompt Validation Error", status=400, detail=detail, instance=instance
        )


class JSONParsingError(AIError):
    def __init__(self, detail: str, raw_output: str, instance: str = "") -> None:
        super().__init__(
            title="JSON Parsing Error",
            status=422,
            detail=f"Failed to parse structured output: {detail}",
            instance=instance,
        )
        self.raw_output = raw_output
