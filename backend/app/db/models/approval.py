import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, DateTime, Enum, JSON, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class ApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    action_type = Column(String(255), nullable=False)
    action_payload = Column(JSON, nullable=False)
    status = Column(Enum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING)
    requested_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    conversation = relationship("Conversation", back_populates="approvals")
