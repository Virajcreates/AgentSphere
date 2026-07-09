import pytest

from agentsphere.ai.exceptions.base import (
    AIError,
    CircuitBreakerOpenError,
    JSONParsingError,
    ModelNotFoundError,
    PromptValidationError,
    ProviderConnectionError,
    ProviderError,
    ProviderTimeoutError,
)


def test_ai_error_inheritance() -> None:
    err = AIError("A general AI error")
    assert err.title == "AI Platform Error"
    assert err.status == 500
    assert err.detail == "A general AI error"


def test_provider_error() -> None:
    err = ProviderError("openai", "Rate limit exceeded")
    assert err.title == "AI Provider Error"
    assert err.status == 502
    assert "Provider 'openai' failed: Rate limit exceeded" in err.detail


def test_provider_connection_error() -> None:
    err = ProviderConnectionError("gemini", "Network unreachable")
    assert err.title == "AI Provider Error"
    assert err.status == 503
    assert "Connection failed: Network unreachable" in err.detail


def test_provider_timeout_error() -> None:
    err = ProviderTimeoutError("anthropic", 5.0)
    assert err.title == "AI Provider Error"
    assert err.status == 504
    assert "Request timed out after 5.0s" in err.detail


def test_circuit_breaker_open_error() -> None:
    err = CircuitBreakerOpenError("groq", 4.5)
    assert err.title == "Circuit Breaker Open"
    assert err.status == 503
    assert "Circuit breaker for provider 'groq' is OPEN" in err.detail


def test_model_not_found_error() -> None:
    err = ModelNotFoundError("ollama", "nonexistent-model")
    assert err.title == "Model Not Found"
    assert err.status == 404
    assert "Model 'nonexistent-model' not found for provider 'ollama'" in err.detail


def test_prompt_validation_error() -> None:
    err = PromptValidationError("Missing variable 'user'")
    assert err.title == "Prompt Validation Error"
    assert err.status == 400


def test_json_parsing_error() -> None:
    err = JSONParsingError("Missing comma", '{"foo": "bar"')
    assert err.title == "JSON Parsing Error"
    assert err.status == 422
    assert "Failed to parse structured output" in err.detail
    assert err.raw_output == '{"foo": "bar"'
