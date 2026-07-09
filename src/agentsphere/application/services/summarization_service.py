from agentsphere.ai.gateway.ai_gateway import AIGateway
from agentsphere.ai.schemas.inference import LLMCompletionRequest, PromptMessage


class SummarizationService:
    def __init__(self, gateway: AIGateway) -> None:
        self._gateway = gateway

    async def summarize_history(self, messages: list[dict[str, str]], model: str = "gpt-4o-mini") -> str:
        """Converts raw list messages history into a condensed text summary utilizing LLM completions."""
        if not messages:
            return ""

        # Format historical items
        formatted_history = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])

        prompt = (
            f"Please summarize the following conversation history concisely, preserving all key decisions, "
            f"names, numbers, and goals:\n\n{formatted_history}\n\nSummary:"
        )

        request = LLMCompletionRequest(
            model=model,
            messages=[PromptMessage(role="user", content=prompt)],
            temperature=0.3,
            max_tokens=250,
        )

        res = await self._gateway.complete(request)
        return res.content.strip()
