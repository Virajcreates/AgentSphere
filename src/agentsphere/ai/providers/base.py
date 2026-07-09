import asyncio
import random
import time
from collections.abc import AsyncIterator

from agentsphere.ai.exceptions.base import ProviderConnectionError, ProviderError
from agentsphere.ai.schemas.inference import (
    EmbeddingRequest,
    EmbeddingResponse,
    ImageRequest,
    ImageResponse,
    LLMCompletionRequest,
    LLMCompletionResponse,
    LLMStreamChunk,
    STTRequest,
    STTResponse,
    TokenUsage,
    TTSRequest,
    TTSResponse,
)


class BaseProviderAdapter:
    def __init__(
        self,
        provider_name: str,
        error_rate: float = 0.0,
        simulated_latency: float = 0.05,
    ) -> None:
        self.provider_name = provider_name
        self.error_rate = error_rate
        self.simulated_latency = simulated_latency

    async def _simulate_latency_and_errors(self) -> None:
        if self.simulated_latency > 0:
            await asyncio.sleep(self.simulated_latency)

        if self.error_rate > 0.0 and random.random() < self.error_rate:
            if random.random() < 0.5:
                raise ProviderConnectionError(
                    self.provider_name, "Simulated network connection reset"
                )
            else:
                raise ProviderError(self.provider_name, "Simulated service internal error", 500)

    def _generate_mock_completion(self, request: LLMCompletionRequest) -> tuple[str, TokenUsage]:
        # Simple heuristic response generation based on the messages
        prompt_text = " ".join([m.content for m in request.messages])
        prompt_len = len(prompt_text)

        # Token counting estimation
        prompt_tokens = max(5, int(prompt_len / 4))

        if request.json_mode:
            content = (
                '{"status": "success", "message": "This is a simulated JSON response", '
                f'"data": {{"received_prompt_length": {prompt_len}}}}}'
            )
        elif "hello" in prompt_text.lower():
            content = (
                f"Hello! This is a mock response from the "
                f"{self.provider_name.capitalize()} provider."
            )
        elif "echo" in prompt_text.lower():
            content = f"Echoing your input: {request.messages[-1].content}"
        else:
            content = (
                f"This is a simulated response from {self.provider_name.capitalize()} "
                f"to your query: '{request.messages[-1].content[:40]}...'"
            )

        completion_tokens = max(10, int(len(content) / 4))
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
        return content, usage

    async def complete(self, request: LLMCompletionRequest) -> LLMCompletionResponse:
        start_time = time.perf_counter()
        await self._simulate_latency_and_errors()
        content, usage = self._generate_mock_completion(request)
        latency = time.perf_counter() - start_time

        return LLMCompletionResponse(
            content=content,
            role="assistant",
            raw_response={"simulated": True, "provider": self.provider_name},
            model=request.model,
            provider=self.provider_name,
            usage=usage,
            latency=latency,
        )

    async def complete_stream(
        self, request: LLMCompletionRequest
    ) -> AsyncIterator[LLMStreamChunk]:
        await self._simulate_latency_and_errors()
        content, usage = self._generate_mock_completion(request)

        # Split the content into chunks of ~1-2 words
        words = content.split(" ")
        num_chunks = len(words)

        async def generator() -> AsyncIterator[LLMStreamChunk]:
            for i, word in enumerate(words):
                # Add back the space except for the last word
                delta = word + (" " if i < num_chunks - 1 else "")
                # Simulate streaming delay between chunks
                await asyncio.sleep(0.01)

                is_last = i == num_chunks - 1
                chunk_usage = usage if is_last else None
                finish_reason = "stop" if is_last else None

                yield LLMStreamChunk(
                    text=content[: sum(len(w) + 1 for w in words[: i + 1])],
                    delta=delta,
                    usage=chunk_usage,
                    finish_reason=finish_reason,
                )

        return generator()

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        start_time = time.perf_counter()
        await self._simulate_latency_and_errors()

        # Generate mock float embeddings of dimension 1536
        embeddings = []
        total_tokens = 0
        for text in request.input:
            tokens = max(1, int(len(text) / 4))
            total_tokens += tokens
            # Simple pseudo-random float generation for mock embedding
            embedding = [random.random() for _ in range(1536)]
            embeddings.append(embedding)

        latency = time.perf_counter() - start_time
        usage = TokenUsage(
            prompt_tokens=total_tokens, embedding_tokens=total_tokens, total_tokens=total_tokens
        )

        return EmbeddingResponse(
            embeddings=embeddings,
            model=request.model,
            provider=self.provider_name,
            usage=usage,
            latency=latency,
        )

    async def transcribe(self, request: STTRequest) -> STTResponse:
        start_time = time.perf_counter()
        await self._simulate_latency_and_errors()
        latency = time.perf_counter() - start_time

        return STTResponse(
            text="This is a simulated transcription of the audio file.",
            model=request.model or "whisper-1",
            provider=self.provider_name,
            latency=latency,
        )

    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        start_time = time.perf_counter()
        await self._simulate_latency_and_errors()
        latency = time.perf_counter() - start_time

        # Generate mock audio bytes
        audio_bytes = b"MOCK_AUDIO_DATA_BYTES"

        return TTSResponse(
            audio_bytes=audio_bytes,
            model=request.model or "tts-1",
            provider=self.provider_name,
            latency=latency,
        )

    async def generate_image(self, request: ImageRequest) -> ImageResponse:
        start_time = time.perf_counter()
        await self._simulate_latency_and_errors()
        latency = time.perf_counter() - start_time

        return ImageResponse(
            url=f"https://api.mock-provider.com/{self.provider_name}/generated-image.png",
            model=request.model or "dall-e-3",
            provider=self.provider_name,
            latency=latency,
        )

    async def health_check(self) -> bool:
        try:
            await self._simulate_latency_and_errors()
            return True
        except Exception:
            return False
