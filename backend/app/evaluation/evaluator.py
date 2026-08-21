import structlog
import time

from app.db.database import async_session
from app.db.repositories.evaluation_run_repo import EvaluationRunRepository
from app.evaluation.test_cases import get_test_cases
from app.services.chat_service import process_message

logger = structlog.get_logger(__name__)


async def run_evaluation(user_id: int) -> dict:
    cases = get_test_cases()
    results = []

    for case in cases:
        start = time.time()
        try:
            chat_result = await process_message(
                user_id=user_id,
                message=case["input"],
                request_id=f"eval-{case['id']}",
            )

            latency_ms = (time.time() - start) * 1000

            tool_names = [te["tool_name"] for te in chat_result.get("tool_executions", [])]
            expected_tools = set(case["expected_tools"])
            actual_tools = set(tool_names)

            tool_match = len(expected_tools.intersection(actual_tools)) / max(len(expected_tools), 1)
            has_response = bool(chat_result.get("response"))
            has_sources = len(chat_result.get("sources", [])) > 0

            retrieval_score = min(1.0, len(chat_result.get("sources", [])) / 3)
            relevance_score = tool_match if expected_tools else (1.0 if has_response else 0.0)
            faithfulness_score = 1.0 if has_response else 0.0

            results.append({
                "case_id": case["id"],
                "success": True,
                "latency_ms": latency_ms,
                "retrieval_score": retrieval_score,
                "relevance_score": relevance_score,
                "faithfulness_score": faithfulness_score,
                "tool_success_rate": tool_match,
                "response": chat_result.get("response", "")[:200],
            })

        except Exception as e:
            latency_ms = (time.time() - start) * 1000
            results.append({
                "case_id": case["id"],
                "success": False,
                "latency_ms": latency_ms,
                "error": str(e),
                "retrieval_score": 0.0,
                "relevance_score": 0.0,
                "faithfulness_score": 0.0,
                "tool_success_rate": 0.0,
            })

    avg_latency = sum(r["latency_ms"] for r in results) / len(results) if results else 0
    avg_retrieval = sum(r.get("retrieval_score", 0) for r in results) / len(results) if results else 0
    avg_relevance = sum(r.get("relevance_score", 0) for r in results) / len(results) if results else 0
    avg_faithfulness = sum(r.get("faithfulness_score", 0) for r in results) / len(results) if results else 0
    avg_tool_success = sum(r.get("tool_success_rate", 0) for r in results) / len(results) if results else 0
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    async with async_session() as session:
        repo = EvaluationRunRepository(session)
        run = await repo.create(
            conversation_id=0,
            retrieval_score=avg_retrieval,
            relevance_score=avg_relevance,
            faithfulness_score=avg_faithfulness,
            latency_ms=avg_latency,
            tool_success_rate=avg_tool_success,
        )
        await session.commit()

    summary = {
        "evaluation_run_id": run.id,
        "total_cases": len(cases),
        "successful_cases": successful,
        "failed_cases": failed,
        "average_latency_ms": round(avg_latency, 2),
        "retrieval_score": round(avg_retrieval, 4),
        "relevance_score": round(avg_relevance, 4),
        "faithfulness_score": round(avg_faithfulness, 4),
        "tool_success_rate": round(avg_tool_success, 4),
        "results": results,
    }

    logger.info(
        "evaluation_complete",
        total=len(cases),
        successful=successful,
        failed=failed,
        avg_latency=round(avg_latency, 2),
    )

    return summary
