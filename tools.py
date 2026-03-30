"""Tools — external capabilities available to agents."""

from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode
import config as _config  


@tool
def search_web(query: str) -> str:
    """Search the web for up-to-date information on a topic."""
    search = TavilySearchResults(max_results=3)
    results = search.invoke(query)
    return str(results)

tools = [search_web]
tool_node = ToolNode(tools)
