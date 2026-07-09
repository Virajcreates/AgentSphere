import datetime
import uuid
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from agentsphere.common.uuid7 import uuid7
from agentsphere.config.database import Base


class ConversationModel(Base):
    __tablename__ = "conversation"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    meta_info: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    turns_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    messages: Mapped[list["ConversationMessageModel"]] = relationship(
        "ConversationMessageModel", back_populates="conversation", cascade="all, delete-orphan"
    )
    summaries: Mapped[list["ConversationSummaryModel"]] = relationship(
        "ConversationSummaryModel", back_populates="conversation", cascade="all, delete-orphan"
    )


class ConversationMessageModel(Base):
    __tablename__ = "conversation_message"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversation.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    conversation: Mapped[ConversationModel] = relationship("ConversationModel", back_populates="messages")


class ConversationSummaryModel(Base):
    __tablename__ = "conversation_summary"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversation.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    conversation: Mapped[ConversationModel] = relationship("ConversationModel", back_populates="summaries")
