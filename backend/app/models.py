import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="planning")
    report_markdown = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    sub_questions = relationship("SubQuestion", back_populates="session", cascade="all, delete-orphan")
    sources = relationship("SourceDocument", back_populates="session", cascade="all, delete-orphan")
    claims = relationship("ExtractedClaim", back_populates="session", cascade="all, delete-orphan")


class SubQuestion(Base):
    __tablename__ = "sub_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("research_sessions.id"), nullable=False)
    question = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")

    session = relationship("ResearchSession", back_populates="sub_questions")
    sources = relationship("SourceDocument", back_populates="sub_question", cascade="all, delete-orphan")


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("research_sessions.id"), nullable=False)
    sub_question_id = Column(UUID(as_uuid=True), ForeignKey("sub_questions.id"), nullable=True)
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    snippet = Column(Text, nullable=True)
    content_full = Column(Text, nullable=True)
    relevance_score = Column(Float, nullable=True)

    session = relationship("ResearchSession", back_populates="sources")
    sub_question = relationship("SubQuestion", back_populates="sources")
    claims = relationship("ExtractedClaim", back_populates="source", cascade="all, delete-orphan")


class ExtractedClaim(Base):
    __tablename__ = "extracted_claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("research_sessions.id"), nullable=False)
    source_id = Column(UUID(as_uuid=True), ForeignKey("source_documents.id"), nullable=False)
    text = Column(Text, nullable=False)

    session = relationship("ResearchSession", back_populates="claims")
    source = relationship("SourceDocument", back_populates="claims")
    checks = relationship("VerificationCheck", back_populates="claim", cascade="all, delete-orphan")


class VerificationCheck(Base):
    __tablename__ = "verification_checks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("extracted_claims.id"), nullable=False)
    status = Column(String(20), nullable=False)
    note = Column(Text, nullable=True)
    search_round = Column(Integer, nullable=False, default=1)

    claim = relationship("ExtractedClaim", back_populates="checks")
