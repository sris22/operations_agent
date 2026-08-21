from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EvaluationRunResponse(BaseModel):
    id: int
    conversation_id: int
    retrieval_score: Optional[float] = None
    relevance_score: Optional[float] = None
    faithfulness_score: Optional[float] = None
    latency_ms: Optional[float] = None
    estimated_cost: Optional[float] = None
    tool_success_rate: Optional[float] = None
    created_at: datetime


class EvaluationListResponse(BaseModel):
    evaluations: list[EvaluationRunResponse]
    total: int
    page: int
    page_size: int
