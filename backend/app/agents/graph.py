from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.nodes.classify import classify_request
from app.agents.nodes.retrieve import retrieve_context
from app.agents.nodes.decide_tools import decide_tools
from app.agents.nodes.execute import execute_tools
from app.agents.nodes.evaluate import evaluate_action
from app.agents.nodes.approval import create_approval, wait_for_approval, execute_after_approval
from app.agents.nodes.respond import generate_response


def needs_approval(state: AgentState) -> str:
    if state.get("pending_approval"):
        return "yes"
    return "no"


def approval_resolved(state: AgentState) -> str:
    result = state.get("approval_result", "")
    if result == "APPROVED":
        return "approved"
    return "not_approved"


def should_continue(state: AgentState) -> str:
    if state.get("error"):
        return "respond"
    if state.get("tool_calls"):
        return "execute"
    return "respond"


def build_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("classify", classify_request)
    graph.add_node("retrieve", retrieve_context)
    graph.add_node("decide_tools", decide_tools)
    graph.add_node("execute_tools", execute_tools)
    graph.add_node("evaluate", evaluate_action)
    graph.add_node("create_approval", create_approval)
    graph.add_node("wait_approval", wait_for_approval)
    graph.add_node("execute_after_approval", execute_after_approval)
    graph.add_node("respond", generate_response)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "decide_tools")

    graph.add_conditional_edges(
        "decide_tools",
        should_continue,
        {
            "execute": "execute_tools",
            "respond": "respond",
        },
    )

    graph.add_edge("execute_tools", "evaluate")

    graph.add_conditional_edges(
        "evaluate",
        needs_approval,
        {
            "yes": "create_approval",
            "no": "respond",
        },
    )

    graph.add_edge("create_approval", "wait_approval")

    graph.add_conditional_edges(
        "wait_approval",
        approval_resolved,
        {
            "approved": "execute_after_approval",
            "not_approved": "respond",
        },
    )

    graph.add_edge("execute_after_approval", "respond")
    graph.add_edge("respond", END)

    return graph.compile()


agent_graph = build_agent_graph()
