from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.database import Base


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    retrieval_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    faithfulness_score = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    tool_success_rate = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    conversation = relationship("Conversation")
