# Writer Agent

A multi-agent system built with LangGraph that researches a topic on the web and produces a polished written report.

## How It Works

The system chains two specialised agents together:

1. **Researcher** — Uses the Tavily search API to gather information. It runs in a loop, calling the search tool as many times as needed until it has enough material, then hands off to the writer.
2. **Writer** — Receives the full conversation (including all search results) and produces a clear, structured final report.

```
User query --> Researcher --[search loop]--> Writer --> Final report
```

## Project Structure

```
writer-agent/
├── config.py          # Environment variables, structlog setup, settings
├── state.py           # AgentState definition (shared graph state)
├── tools.py           # Tool definitions (search_web) with retry logic
├── agents.py          # LLM setup, researcher and writer node functions
├── graph.py           # Graph construction, routing logic, compilation
├── main.py            # Interactive CLI entry point
├── requirements.txt   # Python dependencies
├── output/            # Generated reports (git-ignored)
└── .env               # API keys (not committed to version control)
```

## Prerequisites

- Python 3.11+
- A [Groq](https://console.groq.com/) API key
- A [Tavily](https://tavily.com/) API key

## Setup

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd writer-agent
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys**

   Create a `.env` file in the project root:

   ```
   GROQ_API_KEY=your-groq-key-here
   TAVILY_API_KEY=your-tavily-key-here
   ```

## Usage

Run the interactive CLI:

```bash
python3 main.py
```

You'll be prompted to enter research queries. The agent will search the web, compile findings, and produce a written report. Type `quit`, `exit`, or `q` to stop.

```
Writer Agent — Interactive CLI
Type your research query, or 'quit' / 'exit' to stop.

📝 Query: What are the latest developments in AI agents?

🔍 Researching: What are the latest developments in AI agents?

=== Final Answer ===
...

💾 Saved to output/what_are_the_latest_developments_in_ai_agents_20260330_223000.txt

📝 Query: quit
Goodbye!
```

Conversation memory is maintained within a session — follow-up questions can reference earlier answers.

You can also use the compiled app programmatically:

```python
from graph import app

config = {"configurable": {"thread_id": "my-session"}}

result = app.invoke(
    {"messages": [("user", "Your question here")]},
    config=config,
)

print(result["messages"][-1].content)
```

## Module Reference

| Module | Purpose |
|-----------|----------------------------------------------|
| `config.py` | Loads `.env`, sets up structlog, exports API keys, `MODEL_NAME`, and `OUTPUT_DIR` |
| `state.py` | Defines `AgentState`, the shared state passed between nodes |
| `tools.py` | Declares `search_web` tool with retry logic and wraps it in a `ToolNode` |
| `agents.py` | Initialises the LLM and defines the researcher/writer node functions |
| `graph.py` | Builds the `StateGraph`, adds routing logic, compiles to a runnable `app` |
| `main.py` | Interactive CLI — loops queries, saves reports to `output/` |

## Customisation

- **Change the model**: Set `MODEL_NAME` in `.env` (e.g. `MODEL_NAME=groq:llama-3.3-70b-versatile`).
- **Add more tools**: Define new `@tool` functions in `tools.py` and add them to the `tools` list.
- **Add more agents**: Create new node functions in `agents.py`, then register them in `graph.py`.

## License

MIT
