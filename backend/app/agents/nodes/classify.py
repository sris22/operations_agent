import structlog
from typing import Optional

from app.agents.state import AgentState, ToolCall
from app.agents.prompts.loader import load_prompt
from app.core.config import settings

logger = structlog.get_logger(__name__)


async def classify_request(state: AgentState) -> dict:
    user_message = state["user_message"]

    prompt = load_prompt("classification")
    system_prompt = load_prompt("system")

    full_prompt = f"""{system_prompt}

{prompt}

User message: {user_message}

Respond with a JSON object containing: intent, requires_tools, tool_calls, customer_id, confidence, reasoning."""

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.llm_api_key)
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{prompt}\n\nUser message: {user_message}"},
            ],
            response_format={"type": "json_object"},
            timeout=settings.llm_timeout_seconds,
        )

        import json
        classification = json.loads(response.choices[0].message.content)

        tool_calls = []
        for tc in classification.get("tool_calls", []):
            tool_calls.append(ToolCall(
                name=tc["name"],
                arguments=tc.get("arguments", {}),
            ))

        logger.info(
            "request_classified",
            intent=classification.get("intent"),
            tool_count=len(tool_calls),
            request_id=state["request_id"],
        )

        return {
            "classification": classification,
            "tool_calls": tool_calls,
        }

    except Exception as e:
        logger.error("classification_failed", error=str(e), request_id=state["request_id"])
        return {
            "error": f"Classification failed: {str(e)}",
            "tool_calls": [],
        }
