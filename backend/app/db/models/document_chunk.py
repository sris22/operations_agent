from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, DateTime, Text, ForeignKey, JSON, Index
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)  # pgvector extension handled at DB level
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    document = relationship("Document")
