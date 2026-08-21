from datetime import datetime

from pydantic import BaseModel


class EvaluationRunResponse(BaseModel):
    id: int
    conversation_id: int
    retrieval_score: float | None = None
    relevance_score: float | None = None
    faithfulness_score: float | None = None
    latency_ms: float | None = None
    estimated_cost: float | None = None
    tool_success_rate: float | None = None
    created_at: datetime


class EvaluationListResponse(BaseModel):
    evaluations: list[EvaluationRunResponse]
    total: int
    page: int
    page_size: int
