"""Tools — external capabilities available to agents."""

import structlog
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

import config as _config  # noqa: F401  — ensure env vars are loaded

log = structlog.get_logger()


@tool
def search_web(query: str) -> str:
    """Search the web for up-to-date information on a topic."""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _search(q: str) -> str:
        search = TavilySearchResults(max_results=3)
        return str(search.invoke(q))

    log.info("search_web", query=query)
    results = _search(query)
    log.info("search_web.done", result_length=len(results))
    return results


tools = [search_web]
tool_node = ToolNode(tools)
