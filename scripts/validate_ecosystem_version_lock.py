#!/usr/bin/env python3
"""Validate program/repositories/ecosystem_version_lock.yaml structure and pins."""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pyyaml required")
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "program" / "repositories" / "ecosystem_version_lock.yaml"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

REQUIRED_TOP = (
    "schema_version",
    "locked_at_utc",
    "repositories",
)
REQUIRED_REPO = (
    "repo",
    "default_branch",
    "accepted_main_sha",
    "commit",
    "ci_workflow_names",
    "required_apis_and_schema_versions",
)

# Canonical seed from program/repositories/canonical_repository_policy.yaml
EXPECTED_REPOS = {
    "gunnchos-7gc-ai-ran-field-kit",
    "gunnchos-research-portal",
    "gunnchos-device-os",
    "gunnchos-hardware-industrial-design",
    "gunnchAI3k",
    "EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon",
    "edge-io-measurement-node",
    "beatlink-party",
    "archive-of-life-artifact-world",
    "pedestrian-pursuit",
    "anime-aggressors",
    "7gc-digital-twin",
    "spectrumx-ai-ran-gary",
    "ntn-resilience-sim",
    "readygary-6g-beam-selection",
    "waike-research-ops",
    "gunnchos-emergent-service-intent-protocols",
    "gunnchos-gpu-nr-baseband-platform",
}


def main() -> int:
    if not LOCK.is_file():
        print("ECOSYSTEM_VERSION_LOCK_FAIL")
        print("- missing", LOCK.relative_to(ROOT))
        return 1

    data = yaml.safe_load(LOCK.read_text(encoding="utf-8"))
    errors: list[str] = []

    if not isinstance(data, dict):
        print("ECOSYSTEM_VERSION_LOCK_FAIL")
        print("- lock root must be a mapping")
        return 1

    for key in REQUIRED_TOP:
        if key not in data:
            errors.append(f"missing top-level field: {key}")

    repos = data.get("repositories")
    if not isinstance(repos, list) or not repos:
        errors.append("repositories must be a non-empty list")
        print("ECOSYSTEM_VERSION_LOCK_FAIL")
        for e in errors:
            print("-", e)
        return 1

    seen: set[str] = set()
    for i, entry in enumerate(repos):
        if not isinstance(entry, dict):
            errors.append(f"repositories[{i}] must be a mapping")
            continue
        name = entry.get("repo")
        prefix = f"repo[{name or i}]"
        for key in REQUIRED_REPO:
            if key not in entry:
                errors.append(f"{prefix}: missing {key}")
        if not isinstance(name, str) or not name:
            errors.append(f"repositories[{i}]: repo must be non-empty string")
            continue
        if name in seen:
            errors.append(f"duplicate repo entry: {name}")
        seen.add(name)

        for sha_field in ("accepted_main_sha", "commit"):
            sha = entry.get(sha_field)
            if not isinstance(sha, str) or not SHA_RE.match(sha):
                errors.append(f"{prefix}: {sha_field} must be 40-char lowercase hex")

        np_branch = entry.get("nonphysical_branch", None)
        if np_branch is not None and not isinstance(np_branch, str):
            errors.append(f"{prefix}: nonphysical_branch must be string or null")
        if isinstance(np_branch, str) and not np_branch.strip():
            errors.append(f"{prefix}: nonphysical_branch must not be empty string")

        apis = entry.get("required_apis_and_schema_versions")
        if not isinstance(apis, dict) or not apis:
            errors.append(f"{prefix}: required_apis_and_schema_versions must be non-empty mapping")

        workflows = entry.get("ci_workflow_names")
        if not isinstance(workflows, list):
            errors.append(f"{prefix}: ci_workflow_names must be a list")
        elif any(not isinstance(w, str) or not w.strip() for w in workflows):
            errors.append(f"{prefix}: ci_workflow_names entries must be non-empty strings")

        if entry.get("default_branch") != data.get("canonical_default_branch", "main"):
            # Informational consistency: default_branch should match canonical unless noted.
            if entry.get("default_branch") not in ("main", "master"):
                errors.append(f"{prefix}: unexpected default_branch {entry.get('default_branch')!r}")

    missing = EXPECTED_REPOS - seen
    extra = seen - EXPECTED_REPOS
    for name in sorted(missing):
        errors.append(f"missing canonical repo: {name}")
    for name in sorted(extra):
        errors.append(f"unexpected repo not in canonical seed: {name}")

    # Control-plane self consistency: if nonphysical branch set, commit may differ from main.
    for entry in repos:
        if not isinstance(entry, dict):
            continue
        if entry.get("repo") != "gunnchos-7gc-ai-ran-field-kit":
            continue
        if not entry.get("nonphysical_branch"):
            errors.append("control plane must declare nonphysical_branch during NONPHYSICAL_TOTALITY")
        if entry.get("accepted_main_sha") == entry.get("commit") and entry.get("nonphysical_branch"):
            # Allowed if branch tip equals main; not an error.
            pass

    if errors:
        print("ECOSYSTEM_VERSION_LOCK_FAIL")
        for e in errors:
            print("-", e)
        return 1

    print("ECOSYSTEM_VERSION_LOCK_PASS")
    print(f"repos={len(seen)}")
    print(f"locked_at_utc={data.get('locked_at_utc')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
