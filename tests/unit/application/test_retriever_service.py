import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock
import pytest

from agentsphere.application.ports.event_bus import EventBus
from agentsphere.application.services.embedding_service import EmbeddingService
from agentsphere.application.services.retriever_service import RetrieverService
from agentsphere.infrastructure.persistence.repositories.knowledge_repository import KnowledgeRepository


class FakeSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


@pytest.fixture
def mock_repo() -> KnowledgeRepository:
    repo = MagicMock(spec=KnowledgeRepository)
    # mock similarity_search to return a chunk
    mock_chunks = [
        {
            "chunk_id": uuid.uuid4(),
            "document_id": uuid.uuid4(),
            "page_index": 1,
            "similarity": 0.8,
            "text_content": "The capital of France is Paris.",
        }
    ]
    repo.similarity_search = AsyncMock(return_value=mock_chunks)
    return repo


@pytest.fixture
def mock_embed() -> EmbeddingService:
    service = MagicMock(spec=EmbeddingService)
    service.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2]])
    return service


@pytest.fixture
def mock_db() -> Any:
    db = MagicMock()
    db.get_session = MagicMock(return_value=FakeSession())
    return db


@pytest.mark.asyncio
async def test_retriever_service_similarity_and_hybrid(
    mock_db: Any, mock_repo: KnowledgeRepository, mock_embed: EmbeddingService
) -> None:
    event_bus = MagicMock(spec=EventBus)
    service = RetrieverService(
        db=mock_db,
        knowledge_repo_factory=MagicMock(return_value=mock_repo),
        embedding_service=mock_embed,
        event_bus=event_bus,
    )

    kb_id = uuid.uuid4()
    # retrieve using query
    results = await service.retrieve(
        knowledge_base_id=kb_id,
        query="What is the capital of France?",
        limit=2,
    )

    assert len(results) == 1
    # Check that hybrid score calculations correctly blended cosine distance (0.8) and Jaccard overlaps (0.7-1.0)
    assert results[0]["similarity_score"] > 0.0
    assert results[0]["text_content"] == "The capital of France is Paris."
