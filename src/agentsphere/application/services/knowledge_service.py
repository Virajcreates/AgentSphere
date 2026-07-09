import uuid
from collections.abc import Callable
from typing import Any

import structlog

from agentsphere.application.ports.document_parser import DocumentParserProtocol
from agentsphere.application.ports.repositories import KnowledgeRepositoryProtocol
from agentsphere.application.services.chunking.fixed import FixedChunkingStrategy
from agentsphere.application.services.chunking.markdown import MarkdownChunkingStrategy
from agentsphere.application.services.chunking.recursive import RecursiveChunkingStrategy
from agentsphere.application.services.chunking.semantic import SemanticChunkingStrategy
from agentsphere.application.services.embedding_service import EmbeddingService

logger = structlog.get_logger(__name__)


class KnowledgeService:
    def __init__(
        self,
        db: Any,
        knowledge_repo_factory: Callable[..., KnowledgeRepositoryProtocol],
        embedding_service: EmbeddingService,
        document_parser: DocumentParserProtocol,
    ) -> None:
        self._db = db
        self._repo_factory = knowledge_repo_factory
        self._embedding_service = embedding_service
        self._parser = document_parser

        # Maps chunking strategy name -> Strategy implementation class
        self._strategies = {
            "recursive": RecursiveChunkingStrategy(),
            "markdown": MarkdownChunkingStrategy(),
            "fixed": FixedChunkingStrategy(),
            "semantic": SemanticChunkingStrategy(),
        }

    async def create_knowledge_base(self, tenant_id: uuid.UUID, name: str) -> dict[str, Any]:
        """Creates a new knowledge base container partition within an isolated transaction session."""
        logger.info("Creating Knowledge Base", tenant_id=str(tenant_id), name=name)
        async with self._db.get_session() as session:
            repo = self._repo_factory(session=session)
            return await repo.create(tenant_id=tenant_id, name=name, status="active")

    async def add_document_from_bytes(
        self,
        knowledge_base_id: uuid.UUID,
        filename: str,
        content_bytes: bytes,
        chunk_strategy: str = "recursive",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> dict[str, Any]:
        """Parses, cleans, chunks, generates embeddings, and indexes a raw bytes document."""
        logger.info("Processing Document Upload Pipeline", kb_id=str(knowledge_base_id), file=filename)

        async with self._db.get_session() as session:
            repo = self._repo_factory(session=session)

            # 1. Resolve / Create Collections
            collections = await repo.get_collections(knowledge_base_id)
            if not collections:
                # Create a default system collection for this KB
                coll = await repo.create_collection(knowledge_base_id, "default_collection")
                collection_id = coll["id"]
            else:
                collection_id = collections[0]["id"]

            # 2. Pipeline: Parse raw string from document bytes
            raw_text = await self._parser.parse(filename, content_bytes)

            # 3. Pipeline: Chunker strategy selection
            strategy = self._strategies.get(chunk_strategy.lower(), self._strategies["recursive"])
            text_chunks = strategy.split_text(raw_text, chunk_size, chunk_overlap)

            if not text_chunks:
                text_chunks = ["No parsed text content extracted from document."]

            # 4. Pipeline: Batch embedding resolution
            embeddings = await self._embedding_service.generate_embeddings(text_chunks)

            # 5. Pipeline: Write to database tables
            doc = await repo.create_document(
                collection_id=collection_id,
                name=filename,
                source_type=filename.split(".")[-1] if "." in filename else "txt",
                meta_info={"chunks_count": len(text_chunks)},
            )

            # Commit chunks individually to Postgres
            for i, text_content in enumerate(text_chunks):
                embedding = embeddings[i] if i < len(embeddings) else None
                await repo.add_chunk(
                    document_id=doc["id"],
                    text_content=text_content,
                    embedding=embedding,
                    page_index=i + 1,
                )

            return doc

    async def add_document_from_url(
        self,
        knowledge_base_id: uuid.UUID,
        url: str,
        chunk_strategy: str = "recursive",
    ) -> dict[str, Any]:
        """Asynchronously fetches text body content from URL target and indexes it."""
        # Fetch page text content asynchronously using httpx
        page_text = await self._parser.fetch_url(url)
        content_bytes = page_text.encode("utf-8")
        filename = url.replace("https://", "").replace("http://", "").replace("/", "_") + ".html"

        return await self.add_document_from_bytes(
            knowledge_base_id=knowledge_base_id,
            filename=filename,
            content_bytes=content_bytes,
            chunk_strategy=chunk_strategy,
        )
