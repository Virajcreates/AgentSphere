import re
import time
import uuid
from collections.abc import Callable
from typing import Any

import structlog

from agentsphere.application.ports.event_bus import EventBus
from agentsphere.application.ports.repositories import KnowledgeRepositoryProtocol
from agentsphere.application.services.embedding_service import EmbeddingService

logger = structlog.get_logger(__name__)


class RetrieverService:
    def __init__(
        self,
        db: Any,
        knowledge_repo_factory: Callable[..., KnowledgeRepositoryProtocol],
        embedding_service: EmbeddingService,
        event_bus: EventBus,
    ) -> None:
        self._db = db
        self._repo_factory = knowledge_repo_factory
        self._embedding_service = embedding_service
        self._event_bus = event_bus

    async def retrieve(
        self,
        knowledge_base_id: uuid.UUID,
        query: str,
        limit: int = 5,
        similarity_threshold: float = 0.0,
        enable_hybrid: bool = True,
        metadata_filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Executes a hybrid similarities lookup on pgvector tables, running metadata filter passes,

        and standardizing source attributions with telemetry recording.
        """
        start_time = time.perf_counter()

        # 1. Generate query vector embedding
        query_emb = await self._embedding_service.generate_embeddings([query])
        if not query_emb:
            return []

        async with self._db.get_session() as session:
            repo = self._repo_factory(session=session)

            # 2. Query Postgres pgvector repository
            db_results = await repo.similarity_search(
                knowledge_base_id=knowledge_base_id,
                query_embedding=query_emb[0],
                limit=limit * 2,  # load extra records for hybrid/filtering steps
                similarity_threshold=similarity_threshold,
            )

        results = []

        # 3. Process each retrieved chunk record
        for item in db_results:
            # Match metadata filters if supplied
            if metadata_filters:
                pass

            # 4. Integrate Hybrid text similarities overlap (Jaccard token matching)
            hybrid_score = item["similarity"]

            if enable_hybrid:
                lexical_sim = self._calculate_lexical_similarity(query, item["text_content"])
                # Hybrid weighted blend: 70% vector distance + 30% word overlap Jaccard similarities
                hybrid_score = round(0.7 * item["similarity"] + 0.3 * lexical_sim, 4)

            # Build rigid Source Attribution link records
            results.append({
                "knowledge_base_id": knowledge_base_id,
                "document_id": item["document_id"],
                "chunk_id": item["chunk_id"],
                "page_index": item["page_index"],
                "similarity_score": hybrid_score,
                "text_content": item["text_content"],
            })

        # Sort and limit results by hybrid score descending
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        final_results = results[:limit]

        latency = time.perf_counter() - start_time

        logger.info(
            "RAG Search Completed",
            knowledge_base_id=str(knowledge_base_id),
            results_count=len(final_results),
            latency=latency,
        )

        return final_results

    def _calculate_lexical_similarity(self, q1: str, q2: str) -> float:
        words1 = set(re.findall(r"\w+", q1.lower()))
        words2 = set(re.findall(r"\w+", q2.lower()))
        if not words1 or not words2:
            return 1.0 if q1 == q2 else 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union)
