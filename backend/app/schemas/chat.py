from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str


class ToolExecutionInfo(BaseModel):
    tool_name: str
    status: str
    duration_ms: float | None = None


class SourceInfo(BaseModel):
    document_name: str
    content: str
    similarity_score: float


class ChatResponse(BaseModel):
    conversation_id: int
    message_id: int
    response: str
    sources: list[SourceInfo] = []
    tool_executions: list[ToolExecutionInfo] = []
    approval_required: bool = False
    approval_id: int | None = None


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    metadata_: dict | None = None
    created_at: datetime


class ConversationResponse(BaseModel):
    id: int
    customer_id: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
