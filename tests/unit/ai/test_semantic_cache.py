import pytest

from agentsphere.ai.core.semantic_cache import InMemorySemanticAICache
from agentsphere.ai.schemas.inference import LLMCompletionResponse, TokenUsage


@pytest.fixture
def cache() -> InMemorySemanticAICache:
    return InMemorySemanticAICache(similarity_threshold=0.8)


def test_exact_and_semantic_cache_hits(cache: InMemorySemanticAICache) -> None:
    res = LLMCompletionResponse(
        content="Paris is the capital of France.",
        model="gpt-4o",
        provider="openai",
        usage=TokenUsage(),
        latency=0.5,
    )

    prompt = "What is the capital of France?"
    # Store in cache
    async def run() -> None:
        await cache.set(prompt, res, tenant_id="t1")

        # 1. Exact Hit (same prompt, same tenant)
        hit_exact = await cache.get(prompt, tenant_id="t1")
        assert hit_exact is not None
        assert hit_exact.content == "Paris is the capital of France."

        # 2. Tenant isolation check (different tenant -> Miss!)
        hit_other_tenant = await cache.get(prompt, tenant_id="other_tenant")
        assert hit_other_tenant is None

        # 3. Semantic Overlap Hit (very similar prompt with Jaccard > 0.8)
        similar_prompt = "What is the capital of France"  # missing question mark (100% word overlap)
        hit_semantic = await cache.get(similar_prompt, tenant_id="t1")
        assert hit_semantic is not None

        # 4. Another semantic check: "What is capital of France" (word overlap: 5 out of 6 words match)
        # Jaccard union matches > 0.8
        hit_semantic_2 = await cache.get("What is capital of France", tenant_id="t1")
        assert hit_semantic_2 is not None

        # 5. Dissimilar prompt (overlap too low -> Miss!)
        dissimilar_prompt = "Tell me about French history and capitals"
        hit_miss = await cache.get(dissimilar_prompt, tenant_id="t1")
        assert hit_miss is None

    import asyncio
    asyncio.run(run())


def test_disable_semantic_cache_matching(cache: InMemorySemanticAICache) -> None:
    cache.enable_semantic = False
    res = LLMCompletionResponse(
        content="Paris is the capital of France.",
        model="gpt-4o",
        provider="openai",
        usage=TokenUsage(),
        latency=0.5,
    )

    async def run() -> None:
        await cache.set("What is the capital of France?", res, tenant_id="t1")

        # Exact match still hits
        assert await cache.get("What is the capital of France?", tenant_id="t1") is not None

        # Semantic match misses since enable_semantic is False!
        assert await cache.get("What is capital of France", tenant_id="t1") is None

    import asyncio
    asyncio.run(run())


def test_delete_and_clear_cache(cache: InMemorySemanticAICache) -> None:
    res = LLMCompletionResponse(
        content="Test content",
        model="gpt-4o",
        provider="openai",
        usage=TokenUsage(),
        latency=0.1,
    )

    async def run() -> None:
        await cache.set("prompt", res, tenant_id="t1")
        assert await cache.get("prompt", tenant_id="t1") is not None

        # Delete
        await cache.delete("prompt", tenant_id="t1")
        assert await cache.get("prompt", tenant_id="t1") is None

        # Clear
        await cache.set("prompt2", res, tenant_id="t1")
        await cache.clear()
        assert await cache.get("prompt2", tenant_id="t1") is None

    import asyncio
    asyncio.run(run())
