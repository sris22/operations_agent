from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, Sequence

from app.db.models.evaluation_run import EvaluationRun


class EvaluationRunRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        conversation_id: int,
        retrieval_score: Optional[float] = None,
        relevance_score: Optional[float] = None,
        faithfulness_score: Optional[float] = None,
        latency_ms: Optional[float] = None,
        estimated_cost: Optional[float] = None,
        tool_success_rate: Optional[float] = None,
    ) -> EvaluationRun:
        run = EvaluationRun(
            conversation_id=conversation_id,
            retrieval_score=retrieval_score,
            relevance_score=relevance_score,
            faithfulness_score=faithfulness_score,
            latency_ms=latency_ms,
            estimated_cost=estimated_cost,
            tool_success_rate=tool_success_rate,
        )
        self.db.add(run)
        await self.db.flush()
        await self.db.refresh(run)
        return run

    async def get_by_id(self, run_id: int) -> Optional[EvaluationRun]:
        result = await self.db.execute(select(EvaluationRun).where(EvaluationRun.id == run_id))
        return result.scalar_one_or_none()

    async def list_runs(self, page: int = 1, page_size: int = 20) -> Sequence[EvaluationRun]:
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(EvaluationRun)
            .order_by(EvaluationRun.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return result.scalars().all()

    async def count(self) -> int:
        result = await self.db.execute(select(func.count(EvaluationRun.id)))
        return result.scalar_one()
