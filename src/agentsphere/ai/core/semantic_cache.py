import re

from agentsphere.ai.interfaces.cache import AICache
from agentsphere.ai.schemas.inference import LLMCompletionResponse


class InMemorySemanticAICache(AICache):
    def __init__(self, similarity_threshold: float = 0.85, enable_semantic: bool = True) -> None:
        self.similarity_threshold = similarity_threshold
        self.enable_semantic = enable_semantic

        # Dict matching: (tenant_id, sanitized_prompt) -> LLMCompletionResponse
        self._cache: dict[tuple[str | None, str], LLMCompletionResponse] = {}

    def _sanitize(self, text: str) -> str:
        # Standard cleaning: lowercase, strip, condense multiple spaces/tabs
        cleaned = text.lower().strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    def _calculate_similarity(self, s1: str, s2: str) -> float:
        # Pure Python Token-Overlap Jaccard similarity:
        # Finds overlapping words divided by total distinct words
        words1 = set(re.findall(r"\w+", s1))
        words2 = set(re.findall(r"\w+", s2))

        if not words1 or not words2:
            return 1.0 if s1 == s2 else 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    async def get(self, prompt: str, tenant_id: str | None = None) -> LLMCompletionResponse | None:
        sanitized = self._sanitize(prompt)
        cache_key = (tenant_id, sanitized)

        # 1. Exact match check
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 2. Semantic matching if enabled
        if self.enable_semantic:
            for (cached_tenant, cached_prompt), cached_res in self._cache.items():
                # Tenant isolation check
                if cached_tenant != tenant_id:
                    continue

                similarity = self._calculate_similarity(sanitized, cached_prompt)
                if similarity >= self.similarity_threshold:
                    # Semantic hit!
                    return cached_res

        return None

    async def set(
        self, prompt: str, response: LLMCompletionResponse, tenant_id: str | None = None
    ) -> None:
        sanitized = self._sanitize(prompt)
        cache_key = (tenant_id, sanitized)
        self._cache[cache_key] = response

    async def delete(self, prompt: str, tenant_id: str | None = None) -> None:
        sanitized = self._sanitize(prompt)
        cache_key = (tenant_id, sanitized)
        if cache_key in self._cache:
            del self._cache[cache_key]

    async def clear(self) -> None:
        self._cache.clear()
