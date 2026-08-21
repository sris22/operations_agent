import structlog

from app.agents.state import AgentState
from app.rag.retrieval import retrieve_relevant_chunks, build_rag_context

logger = structlog.get_logger(__name__)


async def retrieve_context(state: AgentState) -> dict:
    user_message = state["user_message"]

    try:
        chunks = await retrieve_relevant_chunks(user_message)
        sources = [chunk.to_dict() for chunk in chunks]

        logger.info(
            "context_retrieved",
            chunks_found=len(sources),
            request_id=state["request_id"],
        )

        return {
            "retrieved_context": sources,
            "sources": sources,
        }

    except Exception as e:
        logger.error("retrieval_failed", error=str(e), request_id=state["request_id"])
        return {
            "retrieved_context": [],
            "sources": [],
        }
