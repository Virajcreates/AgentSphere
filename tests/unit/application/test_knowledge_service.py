import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock
import pytest

from agentsphere.application.services.embedding_service import EmbeddingService
from agentsphere.application.services.knowledge_service import KnowledgeService
from agentsphere.infrastructure.persistence.repositories.knowledge_repository import KnowledgeRepository
from agentsphere.infrastructure.rag.parsing.document_parser import DocumentParser


class FakeSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


@pytest.fixture
def mock_repo() -> KnowledgeRepository:
    repo = MagicMock(spec=KnowledgeRepository)
    repo.get_collections = AsyncMock(return_value=[])
    repo.create_collection = AsyncMock(return_value={"id": uuid.uuid4()})
    repo.create_document = AsyncMock(return_value={"id": uuid.uuid4()})
    repo.add_chunk = AsyncMock()
    repo.create = AsyncMock(return_value={"id": uuid.uuid4(), "status": "active"})
    return repo


@pytest.fixture
def mock_embed() -> EmbeddingService:
    service = MagicMock(spec=EmbeddingService)
    service.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2]])
    return service


@pytest.fixture
def mock_parser() -> DocumentParser:
    parser = MagicMock(spec=DocumentParser)
    parser.parse = AsyncMock(return_value="This is a simple parsed text content block.")
    parser.fetch_url = AsyncMock(return_value="Parsed URL content text.")
    return parser


@pytest.fixture
def mock_db() -> Any:
    db = MagicMock()
    db.get_session = MagicMock(return_value=FakeSession())
    return db


@pytest.mark.asyncio
async def test_knowledge_service_lifecycle_and_upload(
    mock_db: Any,
    mock_repo: KnowledgeRepository,
    mock_embed: EmbeddingService,
    mock_parser: DocumentParser,
) -> None:
    service = KnowledgeService(
        db=mock_db,
        knowledge_repo_factory=MagicMock(return_value=mock_repo),
        embedding_service=mock_embed,
        document_parser=mock_parser,
    )

    tenant_id = uuid.uuid4()
    # 1. Create KB
    kb = await service.create_knowledge_base(tenant_id=tenant_id, name="Corporate KB")
    assert kb is not None
    assert kb["status"] == "active"

    # 2. Upload Document
    doc = await service.add_document_from_bytes(
        knowledge_base_id=uuid.uuid4(),
        filename="notes.txt",
        content_bytes=b"Corporate notes text bytes info.",
        chunk_strategy="recursive",
    )

    assert doc is not None
    mock_parser.parse.assert_called_once()
    mock_embed.generate_embeddings.assert_called_once()
    assert mock_repo.add_chunk.called is True


@pytest.mark.asyncio
async def test_knowledge_service_add_from_url(
    mock_db: Any,
    mock_repo: KnowledgeRepository,
    mock_embed: EmbeddingService,
    mock_parser: DocumentParser,
) -> None:
    service = KnowledgeService(
        db=mock_db,
        knowledge_repo_factory=MagicMock(return_value=mock_repo),
        embedding_service=mock_embed,
        document_parser=mock_parser,
    )

    url = "https://example.com/page1"
    doc = await service.add_document_from_url(
        knowledge_base_id=uuid.uuid4(),
        url=url,
        chunk_strategy="recursive",
    )

    assert doc is not None
    mock_parser.fetch_url.assert_called_once_with(url)
