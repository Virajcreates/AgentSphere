import pytest

from agentsphere.ai.providers.anthropic import AnthropicProvider
from agentsphere.ai.providers.azure_openai import AzureOpenAIProvider
from agentsphere.ai.providers.base import BaseProviderAdapter
from agentsphere.ai.providers.gemini import GeminiProvider
from agentsphere.ai.providers.groq import GroqProvider
from agentsphere.ai.providers.nvidia import NvidiaProvider
from agentsphere.ai.providers.ollama import OllamaProvider
from agentsphere.ai.providers.openai import OpenAIProvider
from agentsphere.ai.providers.openrouter import OpenRouterProvider
from agentsphere.ai.schemas.inference import (
    EmbeddingRequest,
    LLMCompletionRequest,
    PromptMessage,
)


@pytest.fixture
def openai_prov() -> OpenAIProvider:
    return OpenAIProvider(simulated_latency=0.0)


@pytest.mark.asyncio
async def test_openai_completion(openai_prov: OpenAIProvider) -> None:
    req = LLMCompletionRequest(
        model="gpt-4o-mini",
        messages=[PromptMessage(role="user", content="Hello!")],
    )
    res = await openai_prov.complete(req)
    assert res.provider == "openai"
    assert "Hello" in res.content
    assert res.usage.prompt_tokens > 0
    assert res.usage.completion_tokens > 0
    assert res.latency > 0.0


@pytest.mark.asyncio
async def test_openai_embedding(openai_prov: OpenAIProvider) -> None:
    req = EmbeddingRequest(model="text-embedding-3-small", input=["hello world"])
    res = await openai_prov.embed(req)
    assert res.provider == "openai"
    assert len(res.embeddings) == 1
    assert len(res.embeddings[0]) == 1536


@pytest.mark.asyncio
async def test_openai_multimodal_methods(openai_prov: OpenAIProvider) -> None:
    from agentsphere.ai.schemas.inference import ImageRequest, STTRequest, TTSRequest

    # STT
    stt_res = await openai_prov.transcribe(STTRequest(audio_bytes=b"123", filename="test.mp3"))
    assert stt_res.provider == "openai"
    assert "simulated transcription" in stt_res.text

    # TTS
    tts_res = await openai_prov.synthesize(TTSRequest(text="Hello world"))
    assert tts_res.provider == "openai"
    assert tts_res.audio_bytes == b"MOCK_AUDIO_DATA_BYTES"

    # Image
    img_res = await openai_prov.generate_image(ImageRequest(prompt="A beautiful sunset"))
    assert img_res.provider == "openai"
    assert "generated-image.png" in img_res.url



@pytest.mark.asyncio
async def test_all_adapters_instantiation_and_health() -> None:
    providers = [
        OpenAIProvider(simulated_latency=0.0),
        GeminiProvider(simulated_latency=0.0),
        AnthropicProvider(simulated_latency=0.0),
        OpenRouterProvider(simulated_latency=0.0),
        GroqProvider(simulated_latency=0.0),
        AzureOpenAIProvider(simulated_latency=0.0),
        OllamaProvider(simulated_latency=0.0),
        NvidiaProvider(simulated_latency=0.0),
    ]

    for p in providers:
        assert await p.health_check() is True
