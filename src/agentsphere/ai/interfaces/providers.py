from collections.abc import AsyncIterator
from typing import Protocol

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
    TTSRequest,
    TTSResponse,
)


class LLMProvider(Protocol):
    async def complete(self, request: LLMCompletionRequest) -> LLMCompletionResponse: ...

    async def complete_stream(
        self, request: LLMCompletionRequest
    ) -> AsyncIterator[LLMStreamChunk]: ...

    async def health_check(self) -> bool: ...


class EmbeddingProvider(Protocol):
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse: ...

    async def health_check(self) -> bool: ...


class STTProvider(Protocol):
    async def transcribe(self, request: STTRequest) -> STTResponse: ...

    async def health_check(self) -> bool: ...


class TTSProvider(Protocol):
    async def synthesize(self, request: TTSRequest) -> TTSResponse: ...

    async def health_check(self) -> bool: ...


class ImageProvider(Protocol):
    async def generate_image(self, request: ImageRequest) -> ImageResponse: ...

    async def health_check(self) -> bool: ...
