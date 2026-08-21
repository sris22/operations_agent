import structlog

from app.agents.state import AgentState
from app.agents.prompts.loader import load_prompt
from app.core.config import settings

logger = structlog.get_logger(__name__)


async def generate_response(state: AgentState) -> dict:
    user_message = state["user_message"]
    tool_results = state.get("tool_results", [])
    sources = state.get("sources", [])
    approval_id = state.get("approval_id")
    approval_result = state.get("approval_result")
    error = state.get("error")

    tool_summary = []
    for tr in tool_results:
        status = "success" if tr["success"] else "failed"
        tool_summary.append(f"- {tr['name']}: {status}")
        if tr.get("error"):
            tool_summary.append(f"  Error: {tr['error']}")

    source_summary = []
    for s in sources:
        source_summary.append(f"- {s['document_name']} (relevance: {s['similarity_score']:.2f})")

    prompt = load_prompt("response_generation")
    system_prompt = load_prompt("system")

    context_parts = [f"User request: {user_message}"]
    if tool_summary:
        context_parts.append("Tool results:\n" + "\n".join(tool_summary))
    if source_summary:
        context_parts.append("Retrieved sources:\n" + "\n".join(source_summary))
    if approval_id:
        if approval_result == "PENDING":
            context_parts.append(f"Approval #{approval_id} is pending operator approval.")
        elif approval_result == "APPROVED":
            context_parts.append(f"Approval #{approval_id} was approved.")
        elif approval_result == "REJECTED":
            context_parts.append(f"Approval #{approval_id} was rejected.")
    if error:
        context_parts.append(f"Errors encountered: {error}")

    full_context = "\n\n".join(context_parts)

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.llm_api_key)
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": f"{system_prompt}\n\n{prompt}"},
                {"role": "user", "content": full_context},
            ],
            timeout=settings.llm_timeout_seconds,
        )

        final_response = response.choices[0].message.content

        logger.info(
            "response_generated",
            response_length=len(final_response),
            request_id=state["request_id"],
        )

        return {"final_response": final_response}

    except Exception as e:
        logger.error("response_generation_failed", error=str(e), request_id=state["request_id"])
        return {"final_response": f"I encountered an error generating a response: {str(e)}"}
