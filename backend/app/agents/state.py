from typing import TypedDict, Optional


class ToolCall(TypedDict):
    name: str
    arguments: dict


class ToolResult(TypedDict):
    name: str
    success: bool
    output: dict
    error: Optional[str]


class AgentState(TypedDict):
    conversation_id: int
    user_message: str
    request_id: str
    classification: Optional[dict]
    retrieved_context: list[dict]
    tool_calls: list[ToolCall]
    tool_results: list[ToolResult]
    pending_approval: Optional[dict]
    approval_id: Optional[int]
    approval_result: Optional[str]
    final_response: Optional[str]
    sources: list[dict]
    error: Optional[str]
    iteration: int
    tool_call_count: int
