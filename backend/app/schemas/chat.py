from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str


class ToolExecutionInfo(BaseModel):
    tool_name: str
    status: str
    duration_ms: Optional[float] = None


class SourceInfo(BaseModel):
    document_name: str
    content: str
    similarity_score: float


class ChatResponse(BaseModel):
    conversation_id: int
    message_id: int
    response: str
    sources: List[SourceInfo] = []
    tool_executions: List[ToolExecutionInfo] = []
    approval_required: bool = False
    approval_id: Optional[int] = None


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    metadata_: Optional[dict] = None
    created_at: datetime


class ConversationResponse(BaseModel):
    id: int
    customer_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
