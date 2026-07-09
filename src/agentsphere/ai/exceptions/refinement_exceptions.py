from agentsphere.ai.exceptions.base import AIError


class PolicyViolationError(AIError):
    def __init__(self, detail: str, instance: str = "") -> None:
        super().__init__(
            title="Policy Violation Error",
            status=403,
            detail=f"AI Request blocked by policy engine: {detail}",
            instance=instance,
        )


class QuotaExceededError(AIError):
    def __init__(self, detail: str, instance: str = "") -> None:
        super().__init__(
            title="Quota Exceeded Error",
            status=429,
            detail=f"Usage quota threshold exceeded: {detail}",
            instance=instance,
        )


class CapabilityNegotiationError(AIError):
    def __init__(self, detail: str, instance: str = "") -> None:
        super().__init__(
            title="Capability Negotiation Error",
            status=400,
            detail=f"Failed to negotiate compatible model: {detail}",
            instance=instance,
        )


class PromptCompilationError(AIError):
    def __init__(self, detail: str, instance: str = "") -> None:
        super().__init__(
            title="Prompt Compilation Error",
            status=400,
            detail=f"Prompt compiler error: {detail}",
            instance=instance,
        )
