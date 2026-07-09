from typing import Protocol


class ChunkingStrategy(Protocol):
    def split_text(self, text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
        """Splits the raw text input into a list of parsed string chunks under chunk size limits."""
        ...
