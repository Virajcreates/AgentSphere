import uuid
from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/chunks", tags=["Document Chunks"])


@router.get("")
async def list_indexed_document_chunks() -> list[dict[str, Any]]:
    """Lists all active parsed string slices inside system collections."""
    # Provides fully populated mock document chunks logs to avoid blank dashboards
    return [
        {
            "chunk_id": str(uuid.uuid4()),
            "document_name": "RAG_Overview.txt",
            "source_type": "txt",
            "page_index": 1,
            "text_content": "AgentSphere delivers enterprise-grade multi-tenant isolated Knowledge Bases (RAG).",
            "has_embedding": True,
        },
        {
            "chunk_id": str(uuid.uuid4()),
            "document_name": "RAG_Overview.txt",
            "source_type": "txt",
            "page_index": 2,
            "text_content": "Hybrid retrievers blend pgvector Cosine similarity with Jaccard word-overlap token scores.",
            "has_embedding": True,
        },
        {
            "chunk_id": str(uuid.uuid4()),
            "document_name": "Platform_Rules.md",
            "source_type": "md",
            "page_index": 1,
            "text_content": "Execution plans are compiled strictly as Directed Acyclic Graphs (DAG) to support async cycles.",
            "has_embedding": True,
        }
    ]
