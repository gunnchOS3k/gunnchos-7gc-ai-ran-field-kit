#!/usr/bin/env python3
"""Write/update CROSS_REPO_VERSION_LOCK.json from current checkouts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gates_4_6_common import REPOS_ROOT, ROOT, git_branch, git_rev, utc_now, write_json  # noqa: E402

REPOS = [
    "gunnchos-7gc-ai-ran-field-kit",
    "gunnchos-emergent-service-intent-protocols",
    "gunnchos-gpu-nr-baseband-platform",
    "edge-io-measurement-node",
    "7gc-digital-twin",
    "ntn-resilience-sim",
    "spectrumx-ai-ran-gary",
    "readygary-6g-beam-selection",
    "gunnchos-hardware-industrial-design",
    "gunnchos-device-os",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--required-only-core", action="store_true")
    args = parser.parse_args()
    core = {
        "gunnchos-7gc-ai-ran-field-kit",
        "gunnchos-emergent-service-intent-protocols",
        "gunnchos-gpu-nr-baseband-platform",
    }
    components = {}
    for name in REPOS:
        path = REPOS_ROOT / name
        commit = git_rev(path) if path.is_dir() else None
        required = name in core if args.required_only_core else name in core or path.is_dir()
        # New empty repos may lack commits — mark required but commit null until first commit
        if name in core:
            required = True
        components[name] = {
            "path": name,
            "branch": git_branch(path) if path.is_dir() else None,
            "commit": commit,
            "required": required and commit is not None,
            "role": {
                "gunnchos-7gc-ai-ran-field-kit": "control_plane",
                "gunnchos-emergent-service-intent-protocols": "oulu_gate4a",
                "gunnchos-gpu-nr-baseband-platform": "nvidia_gate4b",
            }.get(name, "evidence_source"),
        }
    lock = {
        "schema": "gunnchos.gates_4_6.cross_repo_version_lock.v1",
        "locked_at": utc_now(),
        "mode": "strict_commit_match",
        "dirty_tree_prohibition": False,
        "repos_root_hint": str(REPOS_ROOT),
        "components": components,
        "notes": "Orchestrators fail when required commit does not match checkout.",
    }
    write_json(ROOT / "CROSS_REPO_VERSION_LOCK.json", lock)
    print(json.dumps(lock, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
