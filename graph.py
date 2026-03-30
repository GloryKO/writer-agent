"""Graph — builds and compiles the multi-agent LangGraph workflow."""

from typing import Literal

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from state import AgentState
from tools import tool_node
from agents import researcher_agent, writer_agent


# ── Routing ──────────────────────────────────────────────────────────────────
def should_use_tools(state: AgentState) -> Literal["tools", "writer"]:
    """
    After the researcher responds, inspect the last message:
      • Has tool_calls → route to the ToolNode to execute them
      • No tool_calls  → researcher is done, hand off to the writer
    """
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "writer"


# ── Graph construction ───────────────────────────────────────────────────────
def build_graph():
    """Construct, compile, and return the multi-agent app."""
    workflow = StateGraph(AgentState)

    # Nodes
    workflow.add_node("researcher", researcher_agent)
    workflow.add_node("tools", tool_node)
    workflow.add_node("writer", writer_agent)

    # Entry point
    workflow.set_entry_point("researcher")

    # Researcher → tools OR writer (conditional)
    workflow.add_conditional_edges(
        "researcher",
        should_use_tools,
        {
            "tools": "tools",       # tool calls found  → execute them
            "writer": "writer",     # no tool calls     → go to writer
        },
    )

    # After tools run → back to researcher to evaluate results
    workflow.add_edge("tools", "researcher")

    # Writer → done
    workflow.add_edge("writer", END)

    # Compile with memory so threads retain context across turns
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


# Pre-built app instance for easy import
app = build_graph()
