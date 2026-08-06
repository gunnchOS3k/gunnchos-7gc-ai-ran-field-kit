#!/usr/bin/env python3
"""Fail if active config reintroduces master as default/base outside allowlist."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

ACTIVE_GLOBS = [
    ".github/workflows/*.yml",
    ".github/workflows/*.yaml",
    "Makefile",
    "pyproject.toml",
    ".gitmodules",
    "integration/*.json",
    "CROSS_REPO_VERSION_LOCK.json",
]

MASTER_DEFAULT_PATTERNS = [
    re.compile(r"default[_-]branch\s*[:=]\s*['\"]?master['\"]?", re.I),
    re.compile(r"base\s*:\s*['\"]master['\"]", re.I),
    re.compile(r"branches\s*:\s*\[[^\]]*['\"]master['\"]", re.I),
    re.compile(r"branches:\s*\n(?:\s*-\s*(?:main|master)\s*\n)*\s*-\s*master\s*$", re.M),
]


def load_policy(root: Path) -> dict:
    path = root / "program" / "repositories" / "branch_policy.yaml"
    if not path.exists():
        return {
            "new_master_references_prohibited": True,
            "allowlist_globs_for_master_mentions": [],
            "allowlist_workflow_dual_triggers": True,
        }
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def is_allowlisted(root: Path, path: Path, policy: dict) -> bool:
    rel = path.relative_to(root).as_posix()
    if rel.startswith("program/reports/") or rel.startswith("program/repositories/branch_migration"):
        return True
    if "MIGRATION" in path.name.upper() or "REMEDIATION" in path.name.upper():
        return True
    for glob in policy.get("allowlist_globs_for_master_mentions") or []:
        try:
            if path.match(glob) or Path(rel).match(glob):
                return True
        except Exception:
            pass
        if rel == glob:
            return True
    return False


def workflow_has_main_and_master(text: str) -> bool:
    return bool(re.search(r"\bmain\b", text)) and bool(re.search(r"\bmaster\b", text))


def sole_master_branches_block(text: str) -> bool:
    """True when workflow branches list is only master (no main)."""
    # Simple push branches list
    m = re.search(r"branches:\s*\[([^\]]+)\]", text)
    if m:
        items = [x.strip().strip("'\"") for x in m.group(1).split(",")]
        if items == ["master"]:
            return True
    # YAML list form under branches:
    if re.search(r"branches:\s*\n(?:[ \t]*-\s*master\s*\n)+(?![ \t]*-\s*)", text):
        if not re.search(r"branches:\s*\n(?:.*\n)*?[ \t]*-\s*main\s*$", text, re.M):
            # check if main appears in same branches block
            block = re.search(r"branches:\s*\n((?:[ \t]*-\s*\S+\s*\n)+)", text)
            if block:
                names = re.findall(r"-\s*(\S+)", block.group(1))
                if names == ["master"]:
                    return True
    return False


def scan(root: Path) -> list[str]:
    policy = load_policy(root)
    if not policy.get("new_master_references_prohibited", True):
        return []
    findings: list[str] = []
    files: list[Path] = []
    for pattern in ACTIVE_GLOBS:
        files.extend(root.glob(pattern))
    seen: set[str] = set()
    for path in files:
        if not path.is_file():
            continue
        key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        if is_allowlisted(root, path, policy):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "workflows" in path.parts and path.suffix in {".yml", ".yaml"}:
            if policy.get("allowlist_workflow_dual_triggers") and workflow_has_main_and_master(text):
                if re.search(r"default[_-]branch\s*[:=]\s*['\"]?master['\"]?", text, re.I):
                    findings.append(f"{path.relative_to(root)}: default_branch master")
                continue
            if sole_master_branches_block(text):
                findings.append(f"{path.relative_to(root)}: branches list is only master")
                continue
        for pat in MASTER_DEFAULT_PATTERNS:
            if pat.search(text):
                findings.append(f"{path.relative_to(root)}: matches /{pat.pattern}/")
                break
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    findings = scan(args.root.resolve())
    if findings:
        print("MAIN_BRANCH_POLICY_FAIL")
        for f in findings:
            print(f"  {f}")
        return 1
    print("MAIN_BRANCH_POLICY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
