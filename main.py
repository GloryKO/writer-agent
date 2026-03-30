"""Main — interactive CLI entry point for the writer agent."""

import re
from datetime import datetime

import structlog

from config import OUTPUT_DIR
from graph import app

log = structlog.get_logger()


def make_filename(query: str) -> str:
    """Turn the query into a short, filesystem-safe filename."""
    slug = re.sub(r"[^a-z0-9]+", "_", query.lower()).strip("_")[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{slug}_{timestamp}.txt"


def run_query(query: str, thread_id: str) -> str | None:
    """Run a single query through the agent graph and return the answer."""
    log.info("query.start", query=query, thread_id=thread_id)

    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = app.invoke(
            {"messages": [("user", query)]},
            config=config,
        )
    except Exception:
        log.exception("query.failed")
        print("\n❌ Something went wrong while processing your query. Check logs above.")
        return None

    # Get the final answer — handle both .content and string responses
    last_msg = result["messages"][-1]
    final_answer = getattr(last_msg, "content", str(last_msg)) or ""

    if not final_answer:
        log.warning("query.empty_response")
        print("\nThe agent returned an empty response.")
        return None

    log.info("query.done", answer_length=len(final_answer))
    return final_answer


def save_output(query: str, answer: str) -> str:
    """Save the query and answer to the output directory. Returns the filepath."""
    filename = make_filename(query)
    filepath = OUTPUT_DIR / filename

    with open(filepath, "w") as f:
        f.write(f"Query: {query}\n")
        f.write(f"Date:  {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("-" * 60 + "\n\n")
        f.write(answer)

    return str(filepath)


def main():
    thread_id = f"session-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print("Writer Agent — Interactive CLI")
    print("Type your research query, or 'quit' / 'exit' to stop.\n")

    while True:
        try:
            query = input("📝 Query: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        print(f"\n🔍 Researching: {query}\n")
        answer = run_query(query, thread_id)

        if answer:
            print("\n=== Final Answer ===")
            print(answer)

            filepath = save_output(query, answer)
            print(f"\n💾 Saved to {filepath}\n")


if __name__ == "__main__":
    main()
