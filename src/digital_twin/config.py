from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from a local .env if present.
# Check project root first, then src directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
if not ENV_PATH.exists():
    ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


def get_gemini_api_key() -> Optional[str]:
    """Return the Gemini API key from the environment, if set."""
    return os.getenv("GEMINI_API_KEY")
