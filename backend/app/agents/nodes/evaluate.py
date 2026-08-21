import structlog

from app.agents.state import AgentState
from app.core.config import settings

logger = structlog.get_logger(__name__)


async def evaluate_action(state: AgentState) -> dict:
    tool_results = state.get("tool_results", [])

    for result in tool_results:
        if result["name"] == "refund_payment":
            output = result.get("output", {})
            if output.get("requires_approval"):
                logger.info(
                    "approval_required",
                    payment_id=output.get("payment_id"),
                    request_id=state["request_id"],
                )
                return {
                    "pending_approval": {
                        "action_type": "refund_payment",
                        "action_payload": output,
                    }
                }

    return {"pending_approval": None}
