import structlog

from app.agents.state import AgentState
from app.db.database import async_session
from app.db.repositories.approval_repo import ApprovalRepository

logger = structlog.get_logger(__name__)


async def create_approval(state: AgentState) -> dict:
    pending = state.get("pending_approval")
    if not pending:
        return {"approval_id": None}

    async with async_session() as session:
        repo = ApprovalRepository(session)
        approval = await repo.create(
            conversation_id=state["conversation_id"],
            action_type=pending["action_type"],
            action_payload=pending["action_payload"],
        )
        await session.commit()

        logger.info(
            "approval_created",
            approval_id=approval.id,
            action_type=pending["action_type"],
            request_id=state["request_id"],
        )

        return {"approval_id": approval.id}


async def wait_for_approval(state: AgentState) -> dict:
    approval_id = state.get("approval_id")
    if not approval_id:
        return {"approval_result": "skipped"}

    async with async_session() as session:
        repo = ApprovalRepository(session)
        approval = await repo.get_by_id(approval_id)

        if not approval:
            return {"approval_result": "not_found"}

        return {"approval_result": approval.status.value}


async def execute_after_approval(state: AgentState) -> dict:
    approval_result = state.get("approval_result")
    if approval_result != "APPROVED":
        return {"tool_results": state.get("tool_results", [])}

    pending = state.get("pending_approval")
    if not pending:
        return {"tool_results": state.get("tool_results", [])}

    from app.agents.nodes.execute import TOOL_REGISTRY
    from app.services.enterprise_client import get_enterprise_client

    client = get_enterprise_client(request_id=state["request_id"])
    payload = pending.get("action_payload", {})

    try:
        if pending["action_type"] == "refund_payment":
            result = await TOOL_REGISTRY["refund_payment"](client, {
                "payment_id": payload.get("payment_id"),
                "amount": payload.get("refund_amount", payload.get("amount", 0)),
            })
            result_dict = result.model_dump() if hasattr(result, "model_dump") else result.__dict__
            return {"tool_results": state.get("tool_results", []) + [{
                "name": "refund_payment",
                "success": result_dict.get("success", False),
                "output": result_dict,
                "error": result_dict.get("error"),
            }]}
    except Exception as e:
        logger.error("approval_execution_failed", error=str(e), request_id=state["request_id"])

    return {"tool_results": state.get("tool_results", [])}
