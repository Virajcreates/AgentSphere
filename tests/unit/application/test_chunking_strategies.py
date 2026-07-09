import pytest

from agentsphere.application.services.chunking.fixed import FixedChunkingStrategy
from agentsphere.application.services.chunking.markdown import MarkdownChunkingStrategy
from agentsphere.application.services.chunking.recursive import RecursiveChunkingStrategy
from agentsphere.application.services.chunking.semantic import SemanticChunkingStrategy


def test_fixed_chunking_strategy() -> None:
    strategy = FixedChunkingStrategy()
    text = "abcdefghijklmnopqrstuvwxyz"  # 26 chars

    # split by chunk_size 10, overlap 2
    chunks = strategy.split_text(text, chunk_size=10, chunk_overlap=2)
    assert len(chunks) == 3
    assert chunks[0] == "abcdefghij"  # 10 chars
    assert chunks[1] == "ijklmnopqr"  # starts at start + size - overlap = 10 - 2 = 8 -> index 8 is 'i'


def test_recursive_chunking_strategy() -> None:
    strategy = RecursiveChunkingStrategy()
    text = "First paragraph.\n\nSecond paragraph has some words.\nThird paragraph."

    # Splits beautifully by double newlines first
    chunks = strategy.split_text(text, chunk_size=35, chunk_overlap=5)
    assert len(chunks) >= 3
    assert "First paragraph." in chunks[0]
    assert "Third paragraph." in chunks[-1]


def test_markdown_chunking_strategy() -> None:
    strategy = MarkdownChunkingStrategy()
    text = "# Title\nSome content here.\n## Subtitle\nMore content here."

    chunks = strategy.split_text(text, chunk_size=50, chunk_overlap=0)
    assert len(chunks) >= 2
    assert "# Title" in chunks[0]
    assert "## Subtitle" in chunks[1]


def test_semantic_chunking_strategy() -> None:
    strategy = SemanticChunkingStrategy()
    text = "What is capital of France? Paris is capital of France. What is capital of Spain? Madrid is capital of Spain."

    chunks = strategy.split_text(text, chunk_size=150, chunk_overlap=10)
    assert len(chunks) > 0
    assert "Paris" in "".join(chunks)
