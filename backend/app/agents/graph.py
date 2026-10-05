from typing import Literal
from langgraph.graph import StateGraph, END
from backend.app.agents.state import AgentState
from backend.app.agents.planner import planner_node
from backend.app.agents.architect import architect_node
from backend.app.agents.coder import coder_node
from backend.app.agents.tester import tester_node
from backend.app.agents.debugger import debugger_node
from backend.app.agents.reviewer import reviewer_node
from backend.app.agents.documenter import documenter_node

def route_after_tester(state: AgentState) -> Literal["debugger", "reviewer"]:
    """
    Evaluates test execution results. If tests failed and attempts remaining,
    routes to debugger; otherwise routes to reviewer.
    """
    test_results = state.get("test_results", {})
    success = test_results.get("success", False)
    debug_attempts = state.get("debug_attempts", 0)
    max_debug_attempts = state.get("max_debug_attempts", 5)

    if success or not state.get("options", {}).get("generate_tests", True):
        return "reviewer"
    
    if debug_attempts < max_debug_attempts:
        return "debugger"
    
    return "reviewer"

def route_after_reviewer(state: AgentState) -> Literal["documenter", "coder"]:
    """
    Checks code review findings for blocking critical security issues.
    """
    review_results = state.get("review_results", [])
    has_critical = any(item.get("severity") == "critical" for item in review_results)
    
    # In case of critical issues, could loop back to coder if not already retried
    if has_critical and state.get("debug_attempts", 0) < 2:
        return "coder"
    
    return "documenter"

def build_agent_graph():
    """
    Compiles the LangGraph StateGraph with conditional execution edges.
    """
    workflow = StateGraph(AgentState)

    # Add agent nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("tester", tester_node)
    workflow.add_node("debugger", debugger_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("documenter", documenter_node)

    # Add edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "architect")
    workflow.add_edge("architect", "coder")
    workflow.add_edge("coder", "tester")

    # Conditional branching after testing
    workflow.add_conditional_edges(
        "tester",
        route_after_tester,
        {
            "debugger": "debugger",
            "reviewer": "reviewer"
        }
    )

    # Debugger loops back to test runner
    workflow.add_edge("debugger", "tester")

    # Conditional branching after reviewer
    workflow.add_conditional_edges(
        "reviewer",
        route_after_reviewer,
        {
            "coder": "coder",
            "documenter": "documenter"
        }
    )

    workflow.add_edge("documenter", END)

    return workflow.compile()

agent_executor = build_agent_graph()
