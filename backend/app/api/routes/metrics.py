from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.db.database import async_session
from app.db.repositories.evaluation_run_repo import EvaluationRunRepository
from app.evaluation.evaluator import run_evaluation

router = APIRouter()


@router.post("/run")
async def run_eval(current_user=Depends(get_current_user)):
    if current_user.get("role") not in ("ADMIN", "OPERATOR"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await run_evaluation(user_id=int(current_user["id"]))
    return result


@router.get("")
async def list_evaluations(
    page: int = 1,
    page_size: int = 20,
    current_user=Depends(get_current_user),
):
    async with async_session() as session:
        repo = EvaluationRunRepository(session)
        runs = await repo.list_runs(page=page, page_size=min(page_size, 100))
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


@router.get("/{evaluation_id}")
async def get_evaluation(
    evaluation_id: int,
    current_user=Depends(get_current_user),
):
    async with async_session() as session:
        repo = EvaluationRunRepository(session)
        run = await repo.get_by_id(evaluation_id)

        if not run:
            raise HTTPException(status_code=404, detail="Evaluation not found")

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
