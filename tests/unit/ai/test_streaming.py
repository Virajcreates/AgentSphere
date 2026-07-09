from typing import AsyncIterator
import pytest

from agentsphere.ai.schemas.inference import LLMStreamChunk, TokenUsage
from agentsphere.ai.streaming.stream import AIStream


@pytest.mark.asyncio
async def test_streaming_accumulation() -> None:
    async def mock_generator() -> AsyncIterator[LLMStreamChunk]:
        yield LLMStreamChunk(text="Hello", delta="Hello")
        yield LLMStreamChunk(text="Hello world", delta=" world")
        yield LLMStreamChunk(
            text="Hello world!",
            delta="!",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=3, cost=0.005),
            finish_reason="stop",
        )

    callback_data = {}

    async def on_complete(**kwargs) -> None:
        callback_data.update(kwargs)

    stream = AIStream(
        stream_generator=mock_generator(),
        provider="openai",
        model="gpt-4o",
        on_complete=on_complete,
    )

    chunks = []
    async for chunk in stream:
        chunks.append(chunk)

    assert len(chunks) == 3
    assert chunks[0].delta == "Hello"
    assert chunks[1].delta == " world"
    assert chunks[2].delta == "!"

    # Verify stream stats accumulated properly
    assert stream.accumulated_text == "Hello world!"
    assert stream.prompt_tokens == 10
    assert stream.completion_tokens == 3
    assert stream.total_cost == 0.005

    # Verify callback was executed on complete with correct kwargs
    assert callback_data["provider"] == "openai"
    assert callback_data["model"] == "gpt-4o"
    assert callback_data["prompt_tokens"] == 10
    assert callback_data["completion_tokens"] == 3
    assert callback_data["text"] == "Hello world!"
    assert callback_data["cost"] == 0.005
    assert "latency" in callback_data
