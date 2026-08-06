#!/usr/bin/env python3
"""Write integration/repo-lock.json from local sibling checkouts.

Never called by verify-repo-lock. Explicit regeneration only.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = ROOT / "integration" / "repo-lock.json"
SCHEMA_VERSION = "1.2.0"

# Portfolio roles for Gates 2 and 4–6 control-plane locking.
DEFAULT_SPEC = [
    {
        "name": "edge-io-measurement-node",
        "path": "edge-io-measurement-node",
        "url": "https://github.com/gunnchOS3k/edge-io-measurement-node",
        "intended_branch": "main",
        "required": True,
        "role": "measurement",
        "visibility": "private",
    },
    {
        "name": "7gc-digital-twin",
        "path": "7gc-digital-twin",
        "url": "https://github.com/gunnchOS3k/7gc-digital-twin",
        "intended_branch": "main",
        "required": True,
        "role": "digital_twin",
        "visibility": "private",
    },
    {
        "name": "spectrumx-ai-ran-gary",
        "path": "spectrumx-ai-ran-gary",
        "url": "https://github.com/gunnchOS3k/spectrumx-ai-ran-gary",
        "intended_branch": "main",
        "required": True,
        "role": "ai_ran",
        "visibility": "private",
    },
    {
        "name": "ntn-resilience-sim",
        "path": "ntn-resilience-sim",
        "url": "https://github.com/gunnchOS3k/ntn-resilience-sim",
        "intended_branch": "main",
        "required": True,
        "role": "ntn_sim",
        "visibility": "private",
    },
    {
        "name": "readygary-6g-beam-selection",
        "path": "readygary-6g-beam-selection",
        "url": "https://github.com/gunnchOS3k/readygary-6g-beam-selection",
        "intended_branch": "main",
        "required": False,
        "role": "beam_selection_optional",
        "visibility": "private",
    },
    {
        "name": "gunnchos-emergent-service-intent-protocols",
        "path": "gunnchos-emergent-service-intent-protocols",
        "url": "https://github.com/gunnchOS3k/gunnchos-emergent-service-intent-protocols",
        "intended_branch": "main",
        "required": True,
        "role": "oulu_scientific",
        "visibility": "private",
    },
    {
        "name": "gunnchos-gpu-nr-baseband-platform",
        "path": "gunnchos-gpu-nr-baseband-platform",
        "url": "https://github.com/gunnchOS3k/gunnchos-gpu-nr-baseband-platform",
        "intended_branch": "main",
        "required": True,
        "role": "nvidia_aerial_track",
        "visibility": "private",
    },
    {
        "name": "gunnchos-hardware-industrial-design",
        "path": "gunnchos-hardware-industrial-design",
        "url": "https://github.com/gunnchOS3k/gunnchos-hardware-industrial-design",
        "intended_branch": "main",
        "required": True,
        "role": "hardware_harness",
        "visibility": "private",
    },
    {
        "name": "gunnchos-device-os",
        "path": "gunnchos-device-os",
        "url": "https://github.com/gunnchOS3k/gunnchos-device-os",
        "intended_branch": "main",
        "required": True,
        "role": "device_os_harness",
        "visibility": "private",
    },
]


def _git(path: Path, *args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), *args],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def write_lock(
    repos_root: Path,
    *,
    mode: str = "corrective_depth_gates_4_6",
    include_self: bool = True,
    allow_dirty: bool = False,
) -> dict:
    locked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    components: dict = {}
    for spec in DEFAULT_SPEC:
        repo_path = repos_root / spec["path"]
        if not repo_path.is_dir():
            raise SystemExit(f"required path missing for lock write: {repo_path}")
        commit = _git(repo_path, "rev-parse", "HEAD")
        branch = _git(repo_path, "rev-parse", "--abbrev-ref", "HEAD")
        dirty = bool(_git(repo_path, "status", "--porcelain"))
        if not commit or commit == "0" * 40:
            raise SystemExit(f"empty/invalid commit for {spec['name']}")
        if dirty and not allow_dirty:
            raise SystemExit(f"dirty tree blocks lock write: {spec['name']} ({repo_path})")
        components[spec["name"]] = {
            "repository_name": spec["name"],
            "repository_url": spec["url"],
            "repository": spec["url"],
            "local_path_hint": spec["path"],
            # Always use sibling-relative path so Gate 2 pipeline can resolve repos_root/name.
            "path": spec["path"],
            "intended_branch": spec["intended_branch"],
            "default_branch": spec["intended_branch"],
            "checked_out_branch": branch,
            "branch": branch,
            "commit": commit,
            "required": bool(spec["required"]),
            "repository_role": spec["role"],
            "visibility": spec["visibility"],
            "dirty_tree_prohibition": True,
            "dirty_at_lock_write": dirty,
        }
    control_plane = {
        "repository_name": "gunnchos-7gc-ai-ran-field-kit",
        "repository_url": "https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit",
        "local_path_hint": "gunnchos-7gc-ai-ran-field-kit",
        "intended_branch": "main",
        "checked_out_branch": _git(ROOT, "rev-parse", "--abbrev-ref", "HEAD"),
        "commit_at_lock_write": _git(ROOT, "rev-parse", "HEAD"),
        "repository_role": "control_plane",
        "visibility": "private",
        "note": (
            "Control-plane commit is informational metadata. Embedding it as a "
            "required component SHA cannot be self-consistent in the same commit "
            "that updates the lock file; sibling components are the hard pin."
        ),
    }
    if not include_self:
        control_plane["included"] = False
    lock = {
        "schema_version": SCHEMA_VERSION,
        "locked_at": locked_at,
        "lock_timestamp": locked_at,
        "verification_date": locked_at[:10],
        "mode": mode,
        "dirty_tree_prohibition": True,
        "control_plane": control_plane,
        "components": components,
        "notes": (
            "Written only by write_repo_lock.py / make write-repo-lock. "
            "verify_repo_lock never mutates this file."
        ),
    }
    return lock


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repos-root", default=str(ROOT.parent))
    p.add_argument("--output", default=str(DEFAULT_LOCK))
    p.add_argument("--mode", default="corrective_depth_gates_4_6")
    p.add_argument("--allow-dirty", action="store_true")
    p.add_argument("--exclude-self", action="store_true")
    args = p.parse_args(argv)
    lock = write_lock(
        Path(args.repos_root),
        mode=args.mode,
        include_self=not args.exclude_self,
        allow_dirty=args.allow_dirty,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(out), "locked_at": lock["locked_at"], "n": len(lock["components"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
