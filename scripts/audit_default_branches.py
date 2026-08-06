#!/usr/bin/env python3
"""Audit default branches across spine repos (offline-friendly)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _git(cwd: Path, *args: str) -> str:
    try:
        out = subprocess.check_output(["git", *args], cwd=cwd, stderr=subprocess.DEVNULL, text=True)
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def audit_repo(path: Path) -> dict:
    if not (path / ".git").exists():
        return {"repository": path.name, "has_git": False}
    return {
        "repository": path.name,
        "has_git": True,
        "local_branch": _git(path, "branch", "--show-current"),
        "origin_head": _git(path, "symbolic-ref", "refs/remotes/origin/HEAD"),
        "has_origin_main": bool(_git(path, "show-ref", "--verify", "--quiet", "refs/remotes/origin/main") or
                                (path / ".git").exists() and _git(path, "rev-parse", "--verify", "origin/main")),
        "has_local_main": bool(_git(path, "rev-parse", "--verify", "main")),
        "has_local_master": bool(_git(path, "rev-parse", "--verify", "master")),
        "main_sha": _git(path, "rev-parse", "--short", "main") or None,
        "master_sha": _git(path, "rev-parse", "--short", "master") or None,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repos-root", type=Path, default=Path(__file__).resolve().parents[1].parent)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args()
    results = []
    if args.repos_root.exists():
        for child in sorted(args.repos_root.iterdir()):
            if child.is_dir() and not child.name.startswith("."):
                results.append(audit_repo(child))
    payload = {"results": results}
    text = json.dumps(payload, indent=2)
    if args.json_out:
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
