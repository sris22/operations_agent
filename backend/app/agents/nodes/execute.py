import time

import structlog

from app.agents.state import AgentState, ToolResult
from app.services.enterprise_client import get_enterprise_client
from app.tools.customer import get_customer
from app.tools.orders import get_order
from app.tools.payments import get_payment, refund_payment
from app.tools.tickets import create_ticket

logger = structlog.get_logger(__name__)

TOOL_REGISTRY = {
    "get_customer": lambda client, args: get_customer(client, args["customer_id"]),
    "get_order": lambda client, args: get_order(client, args["order_id"]),
    "get_payment": lambda client, args: get_payment(client, args["payment_id"]),
    "create_ticket": lambda client, args: create_ticket(
        client,
        args["customer_id"],
        args["subject"],
        args["description"],
        args.get("priority", "MEDIUM"),
    ),
    "refund_payment": lambda client, args: refund_payment(
        client,
        args["payment_id"],
        args["amount"],
    ),
}


async def execute_tools(state: AgentState) -> dict:
    tool_calls = state.get("tool_calls", [])
    if not tool_calls:
        return {"tool_results": []}

    client = get_enterprise_client(request_id=state["request_id"])
    results = []

    for tc in tool_calls:
        tool_name = tc["name"]
        arguments = tc["arguments"]

        if tool_name not in TOOL_REGISTRY:
            results.append(
                ToolResult(
                    name=tool_name,
                    success=False,
                    output={},
                    error=f"Unknown tool: {tool_name}",
                )
            )
            continue

        start = time.time()
        try:
            result = await TOOL_REGISTRY[tool_name](client, arguments)
            duration_ms = (time.time() - start) * 1000

            result_dict = result.model_dump() if hasattr(result, "model_dump") else result.__dict__
            results.append(
                ToolResult(
                    name=tool_name,
                    success=result_dict.get("success", True),
                    output=result_dict,
                    error=result_dict.get("error"),
                )
            )

            logger.info(
                "tool_executed",
                tool=tool_name,
                success=result_dict.get("success", True),
                duration_ms=round(duration_ms, 2),
                request_id=state["request_id"],
            )

        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            results.append(
                ToolResult(
                    name=tool_name,
                    success=False,
                    output={},
                    error=str(e),
                )
            )
            logger.error(
                "tool_failed",
                tool=tool_name,
                error=str(e),
                duration_ms=round(duration_ms, 2),
                request_id=state["request_id"],
            )

    return {"tool_results": results}
