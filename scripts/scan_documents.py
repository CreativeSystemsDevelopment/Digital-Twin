#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

# Allow running the script without installing the package
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
SRC_PATH = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from digital_twin.ingestion import main


if __name__ == "__main__":
    main()
