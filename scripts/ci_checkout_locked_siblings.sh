#!/usr/bin/env bash
# Checkout sibling repositories at SHAs recorded in integration/repo-lock.json
# into REPOS_ROOT (default: parent of this repo). Used by CI so repo-lock tests
# exercise real checkouts rather than skipping.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPOS_ROOT="${1:-$(dirname "$ROOT")}"
LOCK="$ROOT/integration/repo-lock.json"
python3 - <<PY
import json, subprocess, sys
from pathlib import Path
lock = json.loads(Path("$LOCK").read_text())
repos_root = Path("$REPOS_ROOT")
repos_root.mkdir(parents=True, exist_ok=True)
failures = []
for name, meta in (lock.get("components") or {}).items():
    rel = meta.get("path") or name
    commit = meta.get("commit")
    url = meta.get("repository") or f"https://github.com/gunnchOS3k/{name}"
    url = url.replace("gunnchos3k", "gunnchOS3k").replace("Gunnchos3k", "gunnchOS3k")
    if "github.com" in url and not url.endswith(".git"):
        url = url + ".git"
    dest = repos_root / rel
    required = bool(meta.get("required", True))
    print(f"checkout {name} -> {dest} @ {commit} required={required}")
    try:
        if not dest.exists():
            subprocess.check_call(["git", "clone", "--no-checkout", url, str(dest)])
        subprocess.check_call(["git", "-C", str(dest), "fetch", "--depth", "1", "origin", commit])
        subprocess.check_call(["git", "-C", str(dest), "checkout", "--force", commit])
        # Ensure clean tree for dirty-tree prohibition
        subprocess.check_call(["git", "-C", str(dest), "reset", "--hard", commit])
        subprocess.check_call(["git", "-C", str(dest), "clean", "-fd"])
    except Exception as exc:
        if required:
            failures.append(f"{name}: {exc}")
        else:
            print(f"optional missing/skip: {name}: {exc}")
if failures:
    print("FAILURES", failures)
    sys.exit(2)
print("siblings ready at", repos_root)
PY
