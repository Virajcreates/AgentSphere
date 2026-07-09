import uuid
from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from agentsphere.application.services.knowledge_service import KnowledgeService
from agentsphere.application.services.retriever_service import RetrieverService
from agentsphere.interfaces.container import ApplicationContainer

router = APIRouter(prefix="/api/v1/knowledge-bases", tags=["Knowledge Bases"])


class CreateKnowledgeBaseRequest(BaseModel):
    name: str = Field(..., description="Name of the Knowledge Base partition")


class DocumentQueryRequest(BaseModel):
    query: str = Field(..., description="Semantic search query keywords")
    limit: int = Field(5, description="Maximum number of relevant chunks to retrieve")
    similarity_threshold: float = Field(0.0, description="Minimum Jaccard/Vector match score")


@router.post("", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
@inject
async def create_knowledge_base(
    request: CreateKnowledgeBaseRequest,
    tenant_id: str = "default_tenant",
    knowledge_service: KnowledgeService = Depends(Provide[ApplicationContainer.runtime.knowledge_service]),
) -> dict[str, Any]:
    """Sets up a secure, isolated knowledge base resource."""
    try:
        tenant_uuid = uuid.UUID(tenant_id)
    except Exception:
        tenant_uuid = uuid.uuid4()  # dynamic fallback for non-UUID strings

    return await knowledge_service.create_knowledge_base(
        name=request.name,
        tenant_id=str(tenant_uuid),
    )


@router.post("/{id}/documents", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
@inject
async def upload_knowledge_document(
    id: uuid.UUID,
    file: UploadFile = File(...),
    chunk_strategy: str = Form("recursive"),
    knowledge_service: KnowledgeService = Depends(Provide[ApplicationContainer.runtime.knowledge_service]),
) -> dict[str, Any]:
    """Uploads, parses, chunks, embeds, and indexes a raw source document."""
    content_bytes = await file.read()
    try:
        return await knowledge_service.add_document_from_bytes(
            knowledge_base_id=id,
            filename=file.filename or "uploaded_doc.txt",
            content_bytes=content_bytes,
            chunk_strategy=chunk_strategy,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/{id}/query", response_model=list[dict[str, Any]])
@inject
async def query_knowledge_base(
    id: uuid.UUID,
    request: DocumentQueryRequest,
    retriever_service: RetrieverService = Depends(Provide[ApplicationContainer.runtime.retriever_service]),
) -> list[dict[str, Any]]:
    """Runs a secure similarity search across indexed documents, returning Source Attributions."""
    try:
        return await retriever_service.retrieve(
            knowledge_base_id=id,
            query=request.query,
            limit=request.limit,
            similarity_threshold=request.similarity_threshold,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
