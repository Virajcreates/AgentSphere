
from agentsphere.application.services.chunking.base import ChunkingStrategy


class RecursiveChunkingStrategy(ChunkingStrategy):
    def split_text(self, text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
        if not text:
            return []

        # Recursively slice text using splitters list: double newlines, single newlines, spaces, empty string
        splitters = ["\n\n", "\n", " ", ""]
        return self._split_recursive(text, splitters, chunk_size, chunk_overlap)

    def _split_recursive(
        self, text: str, splitters: list[str], chunk_size: int, chunk_overlap: int
    ) -> list[str]:
        if len(text) <= chunk_size:
            return [text]

        if not splitters:
            # Fallback to fixed character slice if splitters are exhausted
            chunks = []
            start = 0
            while start < len(text):
                chunks.append(text[start : start + chunk_size])
                start += chunk_size - chunk_overlap
            return chunks

        splitter = splitters[0]
        remaining_splitters = splitters[1:]

        # Split current block
        if splitter == "":
            parts = list(text)
        else:
            parts = text.split(splitter)

        chunks = []
        current_chunk = ""

        for part in parts:
            # Check if part itself exceeds chunk size
            if len(part) > chunk_size:
                # If current chunk has some content, commit it first
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                # Recursively split the long part with remaining splitters
                sub_chunks = self._split_recursive(part, remaining_splitters, chunk_size, chunk_overlap)
                chunks.extend(sub_chunks)
            else:
                # Part fits. Check if combining it exceeds chunk_size limit
                joiner = splitter if current_chunk else ""
                if len(current_chunk) + len(joiner) + len(part) <= chunk_size:
                    current_chunk += joiner + part
                else:
                    # Current chunk is full, commit it
                    if current_chunk:
                        chunks.append(current_chunk)
                    # Start next chunk, incorporating overlap
                    current_chunk = part

        if current_chunk:
            chunks.append(current_chunk)

        return chunks
