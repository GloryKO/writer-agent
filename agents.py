"""Agent nodes — the researcher and writer that form the graph's brain."""

import structlog
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from tenacity import retry, stop_after_attempt, wait_exponential

from config import MODEL_NAME
from state import AgentState
from tools import tools

log = structlog.get_logger()

# ── LLM setup ────────────────────────────────────────────────────────────────
_model_id = MODEL_NAME.replace("groq:", "") if MODEL_NAME.startswith("groq:") else MODEL_NAME
researcher_llm = ChatGroq(model=_model_id).bind_tools(tools)
writer_llm = ChatGroq(model=_model_id, max_tokens=4096)


# ── Retry wrapper ────────────────────────────────────────────────────────────
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
def _invoke_llm(llm_instance, messages):
    """Invoke an LLM with retry logic for transient API failures."""
    return llm_instance.invoke(messages)


# ── Node functions ───────────────────────────────────────────────────────────
def researcher_agent(state: AgentState) -> dict:
    """
    Research node — calls search_web in a loop until it has enough info.

    When the LLM returns tool_calls, the routing function sends execution
    to the ToolNode. Results flow back here for evaluation. Once satisfied
    the LLM responds without tool_calls and routing forwards to the writer.
    """
    log.info("researcher.start", message_count=len(state["messages"]))
    system_msg = SystemMessage(
        content=(
            "You are a research assistant. "
            "Use the search_web tool to find relevant information. "
            "When you have enough information, stop calling tools and "
            "provide a clear summary of your findings."
        )
    )
    response = _invoke_llm(researcher_llm, [system_msg] + state["messages"])
    has_tool_calls = hasattr(response, "tool_calls") and response.tool_calls
    log.info(
        "researcher.done",
        has_tool_calls=bool(has_tool_calls),
        response_length=len(getattr(response, "content", "") or ""),
    )
    return {"messages": [response]}


def writer_agent(state: AgentState) -> dict:
    """
    Writer node — produces a polished final report from the research.

    Receives the full conversation history (including tool results)
    and writes a clean, structured answer for the user.
    """
    log.info("writer.start", message_count=len(state["messages"]))
    system_msg = SystemMessage(
        content=(
            "You are a technical writer. "
            "Review the research findings in the conversation and produce "
            "a clear, well-structured, and concise final report for the user."
        )
    )
    prompt_msg = HumanMessage(
        content="Please write the final report based on the research above."
    )
    response = _invoke_llm(writer_llm, [system_msg] + state["messages"] + [prompt_msg])
    log.info("writer.done", response_length=len(getattr(response, "content", "") or ""))
    return {"messages": [response]}
