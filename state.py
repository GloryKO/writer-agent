"""Agent state — defines the shared state passed between graph nodes."""

from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """
    Extends MessagesState (which provides `messages` with add_messages reducer).

    Attributes:
        next_agent: Optional routing hint for future multi-agent expansion.
    """
    next_agent: str