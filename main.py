"""Main — CLI entry point for the writer agent."""

from graph import app


def main():
    config = {"configurable": {"thread_id": "demo-1"}}

    result = app.invoke(
        {"messages": [("user", "What are the latest developments in AI agents in 2025?")]},
        config=config,
    )

    print("\n=== Final Answer ===")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
