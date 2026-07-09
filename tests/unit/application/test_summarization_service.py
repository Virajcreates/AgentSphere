from unittest.mock import AsyncMock, MagicMock
import pytest

from agentsphere.ai.gateway.ai_gateway import AIGateway
from agentsphere.ai.schemas.inference import LLMCompletionResponse, TokenUsage
from agentsphere.application.services.summarization_service import SummarizationService


@pytest.fixture
def mock_gateway() -> AIGateway:
    gw = MagicMock(spec=AIGateway)
    mock_res = LLMCompletionResponse(
        content="This conversation was summarized cleanly.",
        model="gpt-4o-mini",
        provider="openai",
        usage=TokenUsage(),
        latency=0.3,
    )
    gw.complete = AsyncMock(return_value=mock_res)
    return gw


@pytest.mark.asyncio
async def test_summarization_service_calls_gateway(mock_gateway: AIGateway) -> None:
    service = SummarizationService(gateway=mock_gateway)
    summary = await service.summarize_history([{"role": "user", "content": "Help me"}])

    assert summary == "This conversation was summarized cleanly."
    mock_gateway.complete.assert_called_once()
