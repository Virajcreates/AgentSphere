from agentsphere.application.services.chunking.base import ChunkingStrategy


class FixedChunkingStrategy(ChunkingStrategy):
    def split_text(self, text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
        if not text:
            return []

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunks.append(text[start:end])
            if end >= text_len or chunk_size <= chunk_overlap:
                break
            start += chunk_size - chunk_overlap

        return chunks
