from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ApprovalResponse(BaseModel):
    id: int
    conversation_id: int
    action_type: str
    action_payload: dict
    status: str
    requested_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None


class ApprovalAction(BaseModel):
    reason: Optional[str] = None
