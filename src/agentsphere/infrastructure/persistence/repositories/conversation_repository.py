import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agentsphere.domain.models.conversation import (
    ConversationMessageModel,
    ConversationModel,
    ConversationSummaryModel,
)
from agentsphere.infrastructure.persistence.repositories.base_repository import BaseRepository


class ConversationRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ConversationModel)

    def _to_dict(self, instance: Any) -> dict[str, Any]:
        return {
            "id": instance.id,
            "tenant_id": instance.tenant_id,
            "status": instance.status,
            "meta_info": instance.meta_info,
            "turns_count": instance.turns_count,
            "created_at": instance.created_at,
        }

    async def add_message(
        self, conversation_id: uuid.UUID, role: str, content: str
    ) -> dict[str, Any]:
        msg = ConversationMessageModel(conversation_id=conversation_id, role=role, content=content)
        self._session.add(msg)
        await self._session.flush()
        return {
            "id": msg.id,
            "conversation_id": msg.conversation_id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at,
        }

    async def get_messages(self, conversation_id: uuid.UUID) -> list[dict[str, Any]]:
        stmt = (
            select(ConversationMessageModel)
            .where(ConversationMessageModel.conversation_id == conversation_id)
            .order_by(ConversationMessageModel.created_at.asc())
        )
        res = await self._session.execute(stmt)
        instances = res.scalars().all()
        return [
            {
                "id": inst.id,
                "conversation_id": inst.conversation_id,
                "role": inst.role,
                "content": inst.content,
                "created_at": inst.created_at,
            }
            for inst in instances
        ]

    async def add_summary(self, conversation_id: uuid.UUID, content: str) -> dict[str, Any]:
        summary = ConversationSummaryModel(conversation_id=conversation_id, content=content)
        self._session.add(summary)
        await self._session.flush()
        return {
            "id": summary.id,
            "conversation_id": summary.conversation_id,
            "content": summary.content,
            "created_at": summary.created_at,
        }

    async def get_latest_summary(self, conversation_id: uuid.UUID) -> dict[str, Any] | None:
        stmt = (
            select(ConversationSummaryModel)
            .where(ConversationSummaryModel.conversation_id == conversation_id)
            .order_by(ConversationSummaryModel.created_at.desc())
            .limit(1)
        )
        res = await self._session.execute(stmt)
        summary = res.scalar_one_or_none()
        if summary:
            return {
                "id": summary.id,
                "conversation_id": summary.conversation_id,
                "content": summary.content,
                "created_at": summary.created_at,
            }
        return None
