from datetime import datetime

from pydantic import BaseModel


class ApprovalResponse(BaseModel):
    id: int
    conversation_id: int
    action_type: str
    action_payload: dict
    status: str
    requested_at: datetime
    resolved_at: datetime | None = None
    resolved_by: int | None = None


class ApprovalAction(BaseModel):
    reason: str | None = None
