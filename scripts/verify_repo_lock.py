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
REQUIRED_LOCK_FIELDS = (
    "schema_version",
    "locked_at",
    "dirty_tree_prohibition",
    "components",
)
REQUIRED_COMPONENT_FIELDS = (
    "commit",
    "required",
)


def git_rev(path: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def git_branch(path: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def git_dirty(path: Path) -> bool | None:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(path), "status", "--porcelain"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return bool(out.strip())
    except Exception:
        return None


def _resolve_path(repos_root: Path, meta: dict, name: str) -> Path:
    rel = meta.get("local_path_hint") or meta.get("path") or name
    if rel in (".", "", name) and name == "gunnchos-7gc-ai-ran-field-kit":
        return ROOT
    if rel == ".":
        return ROOT
    candidate = repos_root / rel
    if candidate.is_dir():
        return candidate
    # Path in lock may be sibling-relative from older schema.
    return repos_root / name


def validate_lock_schema(lock: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(lock, dict) or not lock:
        return ["malformed lock: empty or non-object"]
    for key in REQUIRED_LOCK_FIELDS:
        if key not in lock:
            errors.append(f"malformed lock: missing field {key}")
    components = lock.get("components")
    if not isinstance(components, dict) or not components:
        errors.append("malformed lock: components must be a non-empty object")
        return errors
    for name, meta in components.items():
        if not isinstance(meta, dict):
            errors.append(f"malformed lock: component {name} not an object")
            continue
        for key in REQUIRED_COMPONENT_FIELDS:
            if key not in meta:
                errors.append(f"malformed lock: {name} missing {key}")
        commit = meta.get("commit")
        if commit is None or commit == "" or commit == "0" * 40:
            errors.append(f"empty commit: {name}")
        if not isinstance(commit, str) or (commit and len(commit) < 7):
            errors.append(f"malformed commit: {name}")
    return errors


def verify(
    lock_path: Path,
    repos_root: Path,
    *,
    enforce_branch: bool = False,
    allow_dirty: bool = False,
) -> dict:
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "ok": False,
            "lock_path": str(lock_path),
            "failures": ["malformed_lock"],
            "errors": [f"malformed lock: {exc}"],
            "components": [],
            "notes": "This command never silently rewrites the lock file.",
        }

    schema_errors = validate_lock_schema(lock)
    if schema_errors:
        return {
            "ok": False,
            "lock_path": str(lock_path),
            "locked_at": lock.get("locked_at"),
            "mode": lock.get("mode"),
            "failures": ["malformed_lock"],
            "errors": schema_errors,
            "components": [],
            "notes": "This command never silently rewrites the lock file.",
        }

    components = lock.get("components") or {}
    results = []
    failures = []
    for name, meta in components.items():
        repo_path = _resolve_path(repos_root, meta, name)
        expected = meta.get("commit")
        required = bool(meta.get("required", True))
        intended = meta.get("intended_branch") or meta.get("default_branch") or meta.get("branch")
        actual = git_rev(repo_path) if repo_path.is_dir() else None
        actual_branch = git_branch(repo_path) if repo_path.is_dir() else None
        match = actual == expected
        dirty = git_dirty(repo_path) if repo_path.is_dir() else None
        forbid_dirty = bool(lock.get("dirty_tree_prohibition", True))
        if meta.get("dirty_tree_prohibition") is False:
            # Per-component opt-out only if explicitly false.
            forbid_dirty = False
        branch_ok = True
        if enforce_branch and intended and actual_branch and actual_branch != intended:
            # Corrective workflow may use feature branches; only fail when locked
            # intended branch is required and enforce_branch is set.
            branch_ok = actual_branch == intended or actual_branch.startswith("cursor/")
            # Wrong *required* stable branch when not on corrective: fail closed for RC.
            if required and actual_branch not in (intended, meta.get("checked_out_branch")) and not actual_branch.startswith("cursor/"):
                branch_ok = False
        entry = {
            "repository": name,
            "path": str(repo_path),
            "branch": intended,
            "checked_out_branch": actual_branch,
            "required": required,
            "expected_commit": expected,
            "actual_commit": actual,
            "match": match,
            "present": repo_path.is_dir(),
            "dirty": dirty,
            "branch_ok": branch_ok,
        }
        results.append(entry)
        if required and not repo_path.is_dir():
            failures.append(name)
            entry["missing"] = True
            continue
        if required and not match:
            failures.append(name)
        if required and forbid_dirty and dirty and not allow_dirty:
            entry["dirty_failure"] = True
            if name not in failures:
                failures.append(name)
        if required and enforce_branch and not branch_ok:
            entry["branch_failure"] = True
            if name not in failures:
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
    p.add_argument("--allow-dirty", action="store_true", help="Do not fail required dirty trees")
    p.add_argument("--enforce-branch", action="store_true", help="Fail when branch policy violated")
    args = p.parse_args(argv)
    result = verify(
        Path(args.lock),
        Path(args.repos_root),
        enforce_branch=args.enforce_branch,
        allow_dirty=args.allow_dirty,
    )
    if args.allow_dirty:
        result["allow_dirty"] = True
    text = json.dumps(result, indent=2)
    print(text)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
