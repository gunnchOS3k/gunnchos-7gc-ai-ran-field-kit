#!/usr/bin/env python3
"""Verify integration/repo-lock.json against local checkouts. Never rewrites the lock."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = ROOT / "integration" / "repo-lock.json"


def git_rev(path: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def verify(lock_path: Path, repos_root: Path) -> dict:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    components = lock.get("components") or {}
    results = []
    failures = []
    for name, meta in components.items():
        rel = meta.get("path") or name
        repo_path = repos_root / rel
        expected = meta.get("commit")
        required = bool(meta.get("required", True))
        actual = git_rev(repo_path) if repo_path.is_dir() else None
        match = actual == expected
        entry = {
            "repository": name,
            "path": str(repo_path),
            "branch": meta.get("branch"),
            "required": required,
            "expected_commit": expected,
            "actual_commit": actual,
            "match": match,
            "present": repo_path.is_dir(),
        }
        results.append(entry)
        if required and not match:
            failures.append(name)
        if not required and repo_path.is_dir() and actual and not match:
            entry["drift_optional"] = True
    return {
        "ok": not failures,
        "lock_path": str(lock_path),
        "locked_at": lock.get("locked_at"),
        "mode": lock.get("mode"),
        "failures": failures,
        "components": results,
        "notes": "This command never silently rewrites the lock file.",
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--lock", default=str(DEFAULT_LOCK))
    p.add_argument("--repos-root", default=str(ROOT.parent))
    p.add_argument("--output", default=None)
    args = p.parse_args(argv)
    result = verify(Path(args.lock), Path(args.repos_root))
    text = json.dumps(result, indent=2)
    print(text)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
