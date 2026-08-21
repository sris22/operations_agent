import structlog

from app.agents.state import AgentState, ToolCall

logger = structlog.get_logger(__name__)


async def decide_tools(state: AgentState) -> dict:
    classification = state.get("classification", {})
    existing_calls = state.get("tool_calls", [])

    if existing_calls:
        return {"tool_calls": existing_calls}

    tool_calls = []
    for tc in classification.get("tool_calls", []):
        tool_calls.append(
            ToolCall(
                name=tc["name"],
                arguments=tc.get("arguments", {}),
            )
        )

    logger.info(
        "tools_decided",
        tool_count=len(tool_calls),
        request_id=state["request_id"],
    )

    return {"tool_calls": tool_calls}
