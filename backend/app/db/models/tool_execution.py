import enum
from datetime import UTC, datetime

from sqlalchemy import JSON, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class ToolExecutionStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PENDING = "PENDING"


class ToolExecution(Base):
    __tablename__ = "tool_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    tool_name = Column(String(255), nullable=False, index=True)
    input_ = Column("input", JSON, nullable=False)
    output_ = Column("output", JSON, nullable=True)
    status = Column(Enum(ToolExecutionStatus), nullable=False, default=ToolExecutionStatus.PENDING)
    error = Column(Text, nullable=True)
    duration_ms = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    conversation = relationship("Conversation", back_populates="tool_executions")
