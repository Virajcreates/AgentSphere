
from agentsphere.ai.gateway.ai_gateway import AIGateway
from agentsphere.ai.schemas.inference import EmbeddingRequest


class EmbeddingService:
    def __init__(self, gateway: AIGateway) -> None:
        self._gateway = gateway

    async def generate_embeddings(self, texts: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
        """Invokes the central platform AIGateway to resolve vector embeddings for a list of texts."""
        if not texts:
            return []

        request = EmbeddingRequest(model=model, input=texts)
        res = await self._gateway.embed(request)
        return res.embeddings
