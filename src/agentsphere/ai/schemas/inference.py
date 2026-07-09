from typing import Any, Literal

from pydantic import BaseModel, Field


class PromptMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    name: str | None = None


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    embedding_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0


class LLMCompletionRequest(BaseModel):
    model: str
    messages: list[PromptMessage]
    temperature: float = 0.7
    max_tokens: int | None = None
    json_mode: bool = False
    tools: list[dict[str, Any]] | None = None
    response_format: Any | None = None


class LLMCompletionResponse(BaseModel):
    content: str
    role: str = "assistant"
    raw_response: dict[str, Any] = Field(default_factory=dict)
    model: str
    provider: str
    usage: TokenUsage
    latency: float


class LLMStreamChunk(BaseModel):
    text: str
    delta: str
    usage: TokenUsage | None = None
    finish_reason: str | None = None


class EmbeddingRequest(BaseModel):
    model: str
    input: list[str]


class EmbeddingResponse(BaseModel):
    embeddings: list[list[float]]
    model: str
    provider: str
    usage: TokenUsage
    latency: float


class STTRequest(BaseModel):
    audio_bytes: bytes
    filename: str
    model: str | None = None


class STTResponse(BaseModel):
    text: str
    model: str
    provider: str
    latency: float


class TTSRequest(BaseModel):
    text: str
    voice: str | None = None
    model: str | None = None


class TTSResponse(BaseModel):
    audio_bytes: bytes
    model: str
    provider: str
    latency: float


class ImageRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    quality: str = "standard"
    model: str | None = None


class ImageResponse(BaseModel):
    url: str | None = None
    b64_json: str | None = None
    model: str
    provider: str
    latency: float
