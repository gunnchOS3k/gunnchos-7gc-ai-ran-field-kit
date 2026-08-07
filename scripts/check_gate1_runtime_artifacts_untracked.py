#!/usr/bin/env python3
"""Fail if Gate 1 runtime evidence outputs are git-tracked."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PREFIXES = (
    "gate1/evidence/pending/",
    "gate1/evidence/runs/",
    "gate1/evidence/accepted/",
    "gate1/evidence/rejected/",
)
ALLOWED_SUFFIX = "/.gitkeep"
ALLOWED_FILES = {
    "gate1/evidence/README.md",
}


def main() -> int:
    tracked = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-files", "gate1/evidence"],
        text=True,
    ).splitlines()
    bad: list[str] = []
    for rel in tracked:
        if rel in ALLOWED_FILES:
            continue
        if any(rel.startswith(p) for p in FORBIDDEN_PREFIXES):
            if rel.endswith(ALLOWED_SUFFIX) or rel.endswith(".gitkeep"):
                continue
            bad.append(rel)
    if bad:
        print("GATE1_RUNTIME_ARTIFACTS_TRACKED")
        for b in bad:
            print(f"  {b}")
        print("Remove with: git rm --cached <path>; keep only .gitkeep placeholders")
        return 1
    print("GATE1_RUNTIME_ARTIFACTS_CLEAN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
