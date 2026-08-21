#!/usr/bin/env python3
"""CLI wrapper for code health authenticity baseline."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from code_integrity.run_baseline_audit import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
