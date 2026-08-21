import time
from uuid import uuid4

import structlog

from app.agents.graph import agent_graph
from app.agents.state import AgentState
from app.db.database import async_session
from app.db.models.message import MessageRole
from app.db.models.tool_execution import ToolExecutionStatus
from app.db.repositories.conversation_repo import ConversationRepository
from app.db.repositories.message_repo import MessageRepository
from app.db.repositories.tool_execution_repo import ToolExecutionRepository

logger = structlog.get_logger(__name__)


async def process_message(
    user_id: int,
    message: str,
    conversation_id: int | None = None,
    request_id: str | None = None,
) -> dict:
    request_id = request_id or str(uuid4())
    start_time = time.time()

    async with async_session() as session:
        conv_repo = ConversationRepository(session)
        msg_repo = MessageRepository(session)
        tool_repo = ToolExecutionRepository(session)

        if conversation_id:
            conversation = await conv_repo.get_by_id(conversation_id)
            if not conversation:
                raise ValueError("Conversation not found")
        else:
            conversation = await conv_repo.create(user_id=user_id)
            conversation_id = conversation.id

        await msg_repo.create(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=message,
        )
        await session.commit()

    initial_state: AgentState = {
        "conversation_id": conversation_id,
        "user_message": message,
        "request_id": request_id,
        "classification": None,
        "retrieved_context": [],
        "tool_calls": [],
        "tool_results": [],
        "pending_approval": None,
        "approval_id": None,
        "approval_result": None,
        "final_response": None,
        "sources": [],
        "error": None,
        "iteration": 0,
        "tool_call_count": 0,
    }

    result = await agent_graph.ainvoke(initial_state)

    async with async_session() as session:
        msg_repo = MessageRepository(session)
        tool_repo = ToolExecutionRepository(session)

        for tr in result.get("tool_results", []):
            await tool_repo.create(
                conversation_id=conversation_id,
                tool_name=tr["name"],
                input_=tr.get("output", {}),
                output_=tr.get("output", {}),
                status=ToolExecutionStatus.SUCCESS
                if tr["success"]
                else ToolExecutionStatus.FAILURE,
                error=tr.get("error"),
            )

        assistant_msg = await msg_repo.create(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=result.get("final_response", ""),
            metadata_={
                "sources": result.get("sources", []),
                "tool_executions": [
                    {"name": tr["name"], "success": tr["success"]}
                    for tr in result.get("tool_results", [])
                ],
                "approval_id": result.get("approval_id"),
            },
        )
        await session.commit()

    latency_ms = (time.time() - start_time) * 1000

    logger.info(
        "message_processed",
        conversation_id=conversation_id,
        message_id=assistant_msg.id,
        latency_ms=round(latency_ms, 2),
        tool_count=len(result.get("tool_results", [])),
        request_id=request_id,
    )

    return {
        "conversation_id": conversation_id,
        "message_id": assistant_msg.id,
        "response": result.get("final_response", ""),
        "sources": result.get("sources", []),
        "tool_executions": [
            {"tool_name": tr["name"], "status": "SUCCESS" if tr["success"] else "FAILURE"}
            for tr in result.get("tool_results", [])
        ],
        "approval_required": result.get("approval_id") is not None,
        "approval_id": result.get("approval_id"),
    }
