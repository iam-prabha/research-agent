"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "research_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="planning"),
        sa.Column("report_markdown", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "sub_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("research_sessions.id"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
    )

    op.create_table(
        "source_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("research_sessions.id"), nullable=False),
        sa.Column("sub_question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sub_questions.id"), nullable=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("snippet", sa.Text(), nullable=True),
        sa.Column("content_full", sa.Text(), nullable=True),
        sa.Column("relevance_score", sa.Float(), nullable=True),
    )

    op.create_table(
        "extracted_claims",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("research_sessions.id"), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
    )

    op.create_table(
        "verification_checks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("extracted_claims.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("search_round", sa.Integer(), nullable=False, server_default="1"),
    )


def downgrade() -> None:
    op.drop_table("verification_checks")
    op.drop_table("extracted_claims")
    op.drop_table("source_documents")
    op.drop_table("sub_questions")
    op.drop_table("research_sessions")
