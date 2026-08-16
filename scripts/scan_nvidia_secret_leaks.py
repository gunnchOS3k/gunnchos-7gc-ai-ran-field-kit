#!/usr/bin/env python3
"""Scan for likely NGC/API secret leaks. Never prints raw secret values."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PATTERNS = [
    ("nvapi_key", re.compile(r"nvapi-[A-Za-z0-9_-]{8,}")),
    ("ngc_api_key_assignment", re.compile(r"(?i)(NGC_API_KEY|NGC_API_KEY_FILE)\s*=\s*\S+")),
    ("docker_password_literal", re.compile(r"(?i)docker\s+login[^\n]*--password\s+\S+")),
    ("oauth_token_literal", re.compile(r"(?i)oauthtoken[^\n]{0,40}[:=]\s*[A-Za-z0-9._-]{12,}")),
]

SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".wave5_lab_artifacts", ".worktrees", "stream_c_work"}
TEXT_SUFFIX = {".py", ".md", ".json", ".yml", ".yaml", ".toml", ".sh", ".env", ".txt", ".csv", ".ini", ".cfg", ".rs", ".go", ".ts", ".js", ".cmake", ".txt"}


def mask(s: str) -> str:
    if len(s) <= 8:
        return "***"
    return s[:6] + "***MASKED***"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--fail", action="store_true", help="exit 1 if findings")
    args = ap.parse_args()
    findings = []
    for path in args.root.rglob("*"):
        if not path.is_file():
            continue
        if any(p in SKIP_DIRS for p in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIX and path.name not in {".env", ".env.example", "Dockerfile"}:
            continue
        if path.name == ".env.example":
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for cls, pat in PATTERNS:
                m = pat.search(line)
                if m:
                    findings.append(
                        {
                            "path": str(path.relative_to(args.root)),
                            "line": i,
                            "class": cls,
                            "masked": mask(m.group(0)),
                        }
                    )
    import json

    print(json.dumps({"ok": not findings, "findings": findings}, indent=2))
    if findings and args.fail:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
