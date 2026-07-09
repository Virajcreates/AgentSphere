"""conversation and knowledge platform schema

Revision ID: 002
Revises: 001
Create Date: 2026-07-09
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create Knowledge Bases, Collections, Documents, and Chunks tables
    op.create_table(
        "knowledge_base",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "collection",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("knowledge_base_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_base.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "document",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("collection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("collection.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("meta_info", postgresql.JSONB, server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Use native 'vector' column type in PostgreSQL
    op.create_table(
        "document_chunk",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("document.id"), nullable=False),
        sa.Column("text_content", sa.Text(), nullable=False),
        sa.Column("page_index", sa.Integer(), nullable=True),
        sa.Column("embedding", sa.UserDefinedType(), nullable=True),  # custom UserDefinedType resolves to vector
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Convert UserDefinedType raw column definition back to PGVector 'vector(1536)' during table creation execution
    op.execute("ALTER TABLE document_chunk ALTER COLUMN embedding TYPE vector(1536)")

    # Create HNSW high-speed cosine similarity retrieval index
    op.execute(
        "CREATE INDEX IF NOT EXISTS document_chunk_embedding_hnsw_idx ON document_chunk USING hnsw (embedding vector_cosine_ops)"
    )

    # 2. Create Conversations, Messages, and Summaries tables
    op.create_table(
        "conversation",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("status", sa.String(50), server_default="active", nullable=False),
        sa.Column("meta_info", postgresql.JSONB, server_default="{}", nullable=False),
        sa.Column("turns_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "conversation_message",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversation.id"), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "conversation_summary",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversation.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("conversation_summary")
    op.drop_table("conversation_message")
    op.drop_table("conversation")
    op.execute("DROP INDEX IF EXISTS document_chunk_embedding_hnsw_idx")
    op.drop_table("document_chunk")
    op.drop_table("document")
    op.drop_table("collection")
    op.drop_table("knowledge_base")
