"""Agent nodes — the researcher and writer that form the graph's brain."""

from langchain_core.messages import SystemMessage
from langchain.chat_models import init_chat_model

from config import MODEL_NAME
from state import AgentState
from tools import tools

# ── LLM setup ────────────────────────────────────────────────────────────────
llm = init_chat_model(MODEL_NAME)
researcher_llm = llm.bind_tools(tools)   # researcher can call tools
writer_llm = llm                          # writer just writes


# ── Node functions ───────────────────────────────────────────────────────────
def researcher_agent(state: AgentState) -> dict:
    """
    Research node — calls search_web in a loop until it has enough info.

    When the LLM returns tool_calls, the routing function sends execution
    to the ToolNode. Results flow back here for evaluation. Once satisfied
    the LLM responds without tool_calls and routing forwards to the writer.
    """
    system_msg = SystemMessage(
        content=(
            "You are a research assistant. "
            "Use the search_web tool to find relevant information. "
            "When you have enough information, stop calling tools and "
            "provide a clear summary of your findings."
        )
    )
    response = researcher_llm.invoke([system_msg] + state["messages"])
    return {"messages": [response]}


def writer_agent(state: AgentState) -> dict:
    """
    Writer node — produces a polished final report from the research.

    Receives the full conversation history (including tool results)
    and writes a clean, structured answer for the user.
    """
    system_msg = SystemMessage(
        content=(
            "You are a technical writer. "
            "Review the research findings in the conversation and produce "
            "a clear, well-structured, and concise final report for the user."
        )
    )
    response = writer_llm.invoke([system_msg] + state["messages"])
    return {"messages": [response]}
