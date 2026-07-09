import pytest

from agentsphere.ai.schemas.inference import PromptMessage
from agentsphere.ai.tokenizer.token_counter import TokenCounter


@pytest.fixture
def counter() -> TokenCounter:
    return TokenCounter()


def test_fallback_token_counting(counter: TokenCounter) -> None:
    text = "Hello, world! This is a simple test sentence to count tokens."
    token_count = counter.count_tokens(text)
    assert token_count > 0
    # Empty string should yield 0
    assert counter.count_tokens("") == 0


def test_custom_tokenizer_registration(counter: TokenCounter) -> None:
    # Register a dummy tokenizer that always returns 42
    counter.register_tokenizer("gpt-custom", lambda text: 42)

    assert counter.count_tokens("Any text", model="gpt-custom") == 42
    # Standard fallback is used for unregister models
    assert counter.count_tokens("Any text", model="other-model") != 42


def test_count_messages_tokens(counter: TokenCounter) -> None:
    messages = [
        PromptMessage(role="system", content="You are a helpful assistant."),
        PromptMessage(role="user", content="Hello!"),
    ]
    token_count = counter.count_messages_tokens(messages)
    assert token_count > 0
