import datetime
import uuid
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import UserDefinedType

from agentsphere.common.uuid7 import uuid7
from agentsphere.config.database import Base


# Define standard custom PGVector column type without needing the uninstalled 'pgvector' library
class VectorType(UserDefinedType):
    def __init__(self, dim: int = 1536) -> None:
        self.dim = dim

    def get_col_spec(self, **kw: Any) -> str:
        return f"vector({self.dim})"


class KnowledgeBaseModel(Base):
    __tablename__ = "knowledge_base"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    collections: Mapped[list["CollectionModel"]] = relationship(
        "CollectionModel", back_populates="knowledge_base", cascade="all, delete-orphan"
    )


class CollectionModel(Base):
    __tablename__ = "collection"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_base.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    knowledge_base: Mapped[KnowledgeBaseModel] = relationship("KnowledgeBaseModel", back_populates="collections")
    documents: Mapped[list["DocumentModel"]] = relationship(
        "DocumentModel", back_populates="collection", cascade="all, delete-orphan"
    )


class DocumentModel(Base):
    __tablename__ = "document"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    collection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("collection.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pdf, docx, txt, markdown, html, url
    meta_info: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    collection: Mapped[CollectionModel] = relationship("CollectionModel", back_populates="documents")
    chunks: Mapped[list["DocumentChunkModel"]] = relationship(
        "DocumentChunkModel", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunkModel(Base):
    __tablename__ = "document_chunk"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("document.id"), nullable=False
    )
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    page_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Define standard 1536-dimensional vector embedding column type
    embedding: Mapped[list[float] | None] = mapped_column(VectorType(1536), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    document: Mapped[DocumentModel] = relationship("DocumentModel", back_populates="chunks")
