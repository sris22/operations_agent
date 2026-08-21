import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, DateTime, Enum, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class ConversationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    customer_id = Column(String(255), nullable=True, index=True)
    status = Column(Enum(ConversationStatus), nullable=False, default=ConversationStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")
    tool_executions = relationship("ToolExecution", back_populates="conversation")
    approvals = relationship("Approval", back_populates="conversation")
