"""Configuration — loads environment variables and exports settings."""

import os
from dotenv import load_dotenv

# Load .env from the project root
load_dotenv()

# ── API Keys ─────────────────────────────────────────────────────────────────
GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY: str | None = os.getenv("TAVILY_API_KEY")

# Ensure they're also set in os.environ (some SDKs expect this)
if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY
if TAVILY_API_KEY:
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

# ── Model ────────────────────────────────────────────────────────────────────
MODEL_NAME: str = os.getenv("MODEL_NAME", "groq:llama-3.1-8b-instant")
