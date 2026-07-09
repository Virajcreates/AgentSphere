import uuid
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from agentsphere.domain.models.knowledge import (
    CollectionModel,
    DocumentChunkModel,
    DocumentModel,
    KnowledgeBaseModel,
)
from agentsphere.infrastructure.persistence.repositories.base_repository import BaseRepository


class KnowledgeRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, KnowledgeBaseModel)

    def _to_dict(self, instance: Any) -> dict[str, Any]:
        return {
            "id": instance.id,
            "tenant_id": instance.tenant_id,
            "name": instance.name,
            "status": instance.status,
            "created_at": instance.created_at,
        }

    async def create_collection(self, knowledge_base_id: uuid.UUID, name: str) -> dict[str, Any]:
        coll = CollectionModel(knowledge_base_id=knowledge_base_id, name=name)
        self._session.add(coll)
        await self._session.flush()
        return {
            "id": coll.id,
            "knowledge_base_id": coll.knowledge_base_id,
            "name": coll.name,
            "created_at": coll.created_at,
        }

    async def get_collections(self, knowledge_base_id: uuid.UUID) -> list[dict[str, Any]]:
        stmt = select(CollectionModel).where(CollectionModel.knowledge_base_id == knowledge_base_id)
        res = await self._session.execute(stmt)
        instances = res.scalars().all()
        return [
            {
                "id": inst.id,
                "knowledge_base_id": inst.knowledge_base_id,
                "name": inst.name,
                "created_at": inst.created_at,
            }
            for inst in instances
        ]

    async def create_document(self, collection_id: uuid.UUID, name: str, source_type: str, meta_info: dict[str, Any] | None = None) -> dict[str, Any]:
        doc = DocumentModel(collection_id=collection_id, name=name, source_type=source_type, meta_info=meta_info or {})
        self._session.add(doc)
        await self._session.flush()
        return {
            "id": doc.id,
            "collection_id": doc.collection_id,
            "name": doc.name,
            "source_type": doc.source_type,
            "meta_info": doc.meta_info,
            "created_at": doc.created_at,
        }

    async def get_documents(self, collection_id: uuid.UUID) -> list[dict[str, Any]]:
        stmt = select(DocumentModel).where(DocumentModel.collection_id == collection_id)
        res = await self._session.execute(stmt)
        instances = res.scalars().all()
        return [
            {
                "id": inst.id,
                "collection_id": inst.collection_id,
                "name": inst.name,
                "source_type": inst.source_type,
                "meta_info": inst.meta_info,
                "created_at": inst.created_at,
            }
            for inst in instances
        ]

    async def add_chunk(self, document_id: uuid.UUID, text_content: str, embedding: list[float] | None = None, page_index: int | None = None) -> dict[str, Any]:
        chunk = DocumentChunkModel(document_id=document_id, text_content=text_content, embedding=embedding, page_index=page_index)
        self._session.add(chunk)
        await self._session.flush()
        return {
            "id": chunk.id,
            "document_id": chunk.document_id,
            "text_content": chunk.text_content,
            "page_index": chunk.page_index,
            "created_at": chunk.created_at,
        }

    async def similarity_search(
        self,
        knowledge_base_id: uuid.UUID,
        query_embedding: list[float],
        limit: int = 5,
        similarity_threshold: float = 0.0,
    ) -> list[dict[str, Any]]:
        """Conducts high-speed Cosine Distance similarity query on pgvector across whitelisted

        collections inside the requested knowledge base.
        """
        # Convert embedding float array into standard Postgres pgvector literal format: '[0.1, 0.2, ...]'
        emb_str = f"[{','.join(map(str, query_embedding))}]"

        # Cosine distance: embedding <=> query_embedding
        # Cosine similarity: 1.0 - (embedding <=> query_embedding)
        query = (
            select(
                DocumentChunkModel,
                (text("1.0 - (embedding <=> :emb)")).label("similarity")
            )
            .join(DocumentModel, DocumentModel.id == DocumentChunkModel.document_id)
            .join(CollectionModel, CollectionModel.id == DocumentModel.collection_id)
            .where(CollectionModel.knowledge_base_id == knowledge_base_id)
            .order_by(text("embedding <=> :emb"))
            .params(emb=emb_str)
            .limit(limit)
        )

        res = await self._session.execute(query)
        rows = res.all()

        results = []
        for chunk, similarity in rows:
            similarity_val = float(similarity) if similarity is not None else 0.0
            if similarity_val >= similarity_threshold:
                results.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "text_content": chunk.text_content,
                    "page_index": chunk.page_index,
                    "similarity": similarity_val,
                })
        return results
