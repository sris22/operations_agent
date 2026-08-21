import structlog

from app.db.database import async_session
from app.db.repositories.evaluation_run_repo import EvaluationRunRepository

logger = structlog.get_logger(__name__)


async def list_evaluation_runs(page: int = 1, page_size: int = 20) -> dict:
    async with async_session() as session:
        repo = EvaluationRunRepository(session)
        runs = await repo.list_runs(page=page, page_size=page_size)
        total = await repo.count()
        return {
            "evaluations": [
                {
                    "id": r.id,
                    "conversation_id": r.conversation_id,
                    "retrieval_score": r.retrieval_score,
                    "relevance_score": r.relevance_score,
                    "faithfulness_score": r.faithfulness_score,
                    "latency_ms": r.latency_ms,
                    "estimated_cost": r.estimated_cost,
                    "tool_success_rate": r.tool_success_rate,
                    "created_at": r.created_at.isoformat(),
                }
                for r in runs
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }


async def get_evaluation_run(run_id: int) -> dict | None:
    async with async_session() as session:
        repo = EvaluationRunRepository(session)
        run = await repo.get_by_id(run_id)
        if not run:
            return None
        return {
            "id": run.id,
            "conversation_id": run.conversation_id,
            "retrieval_score": run.retrieval_score,
            "relevance_score": run.relevance_score,
            "faithfulness_score": run.faithfulness_score,
            "latency_ms": run.latency_ms,
            "estimated_cost": run.estimated_cost,
            "tool_success_rate": run.tool_success_rate,
            "created_at": run.created_at.isoformat(),
        }
