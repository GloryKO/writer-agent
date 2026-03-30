"""Configuration — loads environment variables, sets up logging, exports settings."""

import os
import sys
from pathlib import Path

import structlog
from dotenv import load_dotenv

# Load .env from the project root
load_dotenv()

# ── Logging ──────────────────────────────────────────────────────────────────
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger()

# ── API Keys ─────────────────────────────────────────────────────────────────
GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY: str | None = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY:
    log.error("GROQ_API_KEY is not set. Add it to your .env file.")
    sys.exit(1)
if not TAVILY_API_KEY:
    log.error("TAVILY_API_KEY is not set. Add it to your .env file.")
    sys.exit(1)

# Ensure they're also set in os.environ (some SDKs expect this)
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

# ── Model ────────────────────────────────────────────────────────────────────
MODEL_NAME: str = os.getenv("MODEL_NAME", "groq:llama-3.1-8b-instant")

# ── Output ───────────────────────────────────────────────────────────────────
OUTPUT_DIR: Path = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
