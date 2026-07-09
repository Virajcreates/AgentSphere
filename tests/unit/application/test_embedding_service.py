from unittest.mock import AsyncMock, MagicMock
import pytest

from agentsphere.ai.gateway.ai_gateway import AIGateway
from agentsphere.ai.schemas.inference import EmbeddingResponse, TokenUsage
from agentsphere.application.services.embedding_service import EmbeddingService


@pytest.fixture
def mock_gateway() -> AIGateway:
    gw = MagicMock(spec=AIGateway)
    # mock raw embed response
    mock_res = EmbeddingResponse(
        embeddings=[[0.1, 0.2, 0.3]],
        model="text-embedding-3-small",
        provider="openai",
        usage=TokenUsage(),
        latency=0.1,
    )
    gw.embed = AsyncMock(return_value=mock_res)
    return gw


@pytest.mark.asyncio
async def test_embedding_service_calls_gateway(mock_gateway: AIGateway) -> None:
    service = EmbeddingService(gateway=mock_gateway)
    embeddings = await service.generate_embeddings(["hello"])

    assert len(embeddings) == 1
    assert embeddings[0] == [0.1, 0.2, 0.3]
    mock_gateway.embed.assert_called_once()
