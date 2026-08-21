from typing import TypedDict


class ToolCall(TypedDict):
    name: str
    arguments: dict


class ToolResult(TypedDict):
    name: str
    success: bool
    output: dict
    error: str | None


class AgentState(TypedDict):
    conversation_id: int
    user_message: str
    request_id: str
    classification: dict | None
    retrieved_context: list[dict]
    tool_calls: list[ToolCall]
    tool_results: list[ToolResult]
    pending_approval: dict | None
    approval_id: int | None
    approval_result: str | None
    final_response: str | None
    sources: list[dict]
    error: str | None
    iteration: int
    tool_call_count: int
