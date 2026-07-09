import re

from agentsphere.application.services.chunking.base import ChunkingStrategy


class SemanticChunkingStrategy(ChunkingStrategy):
    def __init__(self, break_threshold: float = 0.45) -> None:
        self.break_threshold = break_threshold

    def _calculate_jaccard_distance(self, s1: str, s2: str) -> float:
        words1 = set(re.findall(r"\w+", s1.lower()))
        words2 = set(re.findall(r"\w+", s2.lower()))
        if not words1 or not words2:
            return 0.0 if s1 == s2 else 1.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)
        jaccard_similarity = len(intersection) / len(union)
        return 1.0 - jaccard_similarity

    def split_text(self, text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
        if not text:
            return []

        # 1. Parse text into sentences using regex boundary splitters
        sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return []

        chunks = []
        current_chunk = ""

        # 2. Iterate through sentences, evaluating token-overlap distances with consecutive sentences
        for i, sentence in enumerate(sentences):
            if not current_chunk:
                current_chunk = sentence
                continue

            # Calculate Jaccard distance of the current sentence to the accumulated chunk's last sentence
            prev_sentence = sentences[i - 1]
            distance = self._calculate_jaccard_distance(prev_sentence, sentence)

            # If lexical similarity drops (distance crosses threshold), trigger a semantic breakpoint!
            if distance >= self.break_threshold or len(current_chunk) + len(sentence) > chunk_size:
                chunks.append(current_chunk)
                current_chunk = sentence
            else:
                current_chunk += " " + sentence

        if current_chunk:
            chunks.append(current_chunk)

        return chunks
