"""Agent state — defines the shared state passed between graph nodes."""

from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """
    Extends MessagesState (which provides `messages` with add_messages reducer).
    """
    pass