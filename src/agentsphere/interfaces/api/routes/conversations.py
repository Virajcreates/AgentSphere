import uuid
from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from agentsphere.application.services.conversation_service import ConversationService
from agentsphere.interfaces.container import ApplicationContainer

router = APIRouter(prefix="/api/v1/conversations", tags=["Conversations"])


class CreateConversationRequest(BaseModel):
    metadata: dict[str, Any] = Field(default_factory=dict)


class AddMessageRequest(BaseModel):
    role: str = Field(..., description="Message author, e.g. 'user' or 'assistant'")
    content: str = Field(..., description="Message string content")


@router.post("", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
@inject
async def create_conversation(
    request: CreateConversationRequest,
    tenant_id: str = "default_tenant",  # Fallback dummy tenant or resolve from header middleware
    conversation_service: ConversationService = Depends(Provide[ApplicationContainer.runtime.conversation_service]),
) -> dict[str, Any]:
    """Starts a new stateful conversational session thread."""
    try:
        tid_uuid = uuid.UUID(hash=hash(tenant_id)) if "-" not in tenant_id else uuid.UUID(tenant_id)
    except Exception:
        # Generate stable UUID for text-based fallback slugs
        tid_uuid = uuid.UUID("00000000-0000-0000-0000-000000000001")

    return await conversation_service.create_conversation(tenant_id=tid_uuid, metadata=request.metadata)


@router.get("/{id}", response_model=list[dict[str, Any]])
@inject
async def get_conversation_history(
    id: uuid.UUID,
    conversation_service: ConversationService = Depends(Provide[ApplicationContainer.runtime.conversation_service]),
) -> list[dict[str, Any]]:
    """Retrieves full sequence raw messages history for the requested thread."""
    return await conversation_service.get_history(id)


@router.post("/{id}/messages", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
@inject
async def add_conversation_message(
    id: uuid.UUID,
    request: AddMessageRequest,
    conversation_service: ConversationService = Depends(Provide[ApplicationContainer.runtime.conversation_service]),
) -> dict[str, Any]:
    """Appends a new turn message onto the conversational thread, enforcing policies."""
    try:
        return await conversation_service.add_message(
            conversation_id=id,
            role=request.role,
            content=request.content,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{id}/summary", response_model=dict[str, Any] | None)
@inject
async def get_latest_conversation_summary(
    id: uuid.UUID,
    conversation_service: ConversationService = Depends(Provide[ApplicationContainer.runtime.conversation_service]),
) -> dict[str, Any] | None:
    """Retrieves the latest compiled LLM conversation summary, if available."""
    return await conversation_service.get_latest_summary(id)
