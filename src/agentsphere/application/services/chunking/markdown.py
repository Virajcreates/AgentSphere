import re

from agentsphere.application.services.chunking.base import ChunkingStrategy


class MarkdownChunkingStrategy(ChunkingStrategy):
    def split_text(self, text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
        if not text:
            return []

        # Find Markdown headings using regex
        # Slices contents into sections bounded by '# Heading 1', '## Heading 2', etc.
        pattern = r"(^|\n)(?=#{1,6}\s+\w)"
        sections = re.split(pattern, text)

        chunks = []
        current_block = ""

        for sec in sections:
            if not sec.strip():
                continue
            # If combining with current block fits under size limit, accumulate
            if len(current_block) + len(sec) <= chunk_size:
                current_block += sec
            else:
                if current_block:
                    chunks.append(current_block)
                # Slices too long sections using character fallback if section exceeds chunk size
                if len(sec) > chunk_size:
                    start = 0
                    while start < len(sec):
                        chunks.append(sec[start : start + chunk_size])
                        start += chunk_size - chunk_overlap
                    current_block = ""
                else:
                    current_block = sec

        if current_block:
            chunks.append(current_block)

        return chunks
