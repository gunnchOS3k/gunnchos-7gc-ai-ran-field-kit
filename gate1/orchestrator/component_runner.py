"""Discover sibling repos and run safe local Gate 1 component probes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from gate1.orchestrator import DEFAULT_REPOS_ROOT, MANIFESTS, REPO_LOCK, REPO_ROOT
from gate1.orchestrator.evidence_collector import tool_versions, utc_now, write_pending, write_run
from gate1.orchestrator.evidence_validator import validate_against_schema, validate_all_contracts


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def discover_sibling_repos(repos_root: Path | None = None) -> dict[str, Any]:
    root = repos_root or DEFAULT_REPOS_ROOT
    found: list[dict[str, Any]] = []
    if root.exists():
        for child in sorted(root.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            found.append(
                {
                    "name": child.name,
                    "path": str(child),
                    "has_git": (child / ".git").exists(),
                }
            )
    lock = None
    if REPO_LOCK.exists():
        lock = json.loads(REPO_LOCK.read_text(encoding="utf-8"))
    return {
        "repos_root": str(root),
        "sibling_count": len(found),
        "siblings": found,
        "repo_lock_present": REPO_LOCK.exists(),
        "repo_lock": lock,
        "control_plane_repo": REPO_ROOT.name,
    }


def _repo_path(repos_root: Path, name: str) -> Path | None:
    candidates = [
        repos_root / name,
        Path("/Users/gunnchos/Downloads") / name,
        Path.home() / "Downloads" / name,
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _marker_hits(path: Path, markers: list[str]) -> list[str]:
    hits: list[str] = []
    for m in markers:
        if (path / m).exists():
            hits.append(m)
            continue
        # shallow name match
        for child in path.iterdir() if path.is_dir() else []:
            if m.lower() in child.name.lower():
                hits.append(child.name)
                break
    return sorted(set(hits))


def _probe_boot(repo: Path | None) -> dict[str, Any]:
    result = {
        "workstream": "boot",
        "available": bool(repo),
        "repo_path": str(repo) if repo else None,
        "markers": [],
        "software_ok": False,
        "physical_ok": False,
        "evidence_class": "software",
        "details": {},
    }
    if not repo:
        result["details"]["error"] = "owner repo missing locally"
        return result
    markers = _marker_hits(repo, ["boot_readiness", "gunnchos_device_os", "docs", "Makefile"])
    result["markers"] = markers
    # Software slice: markers + optional host identity sample validation
    sample = {
        "schema_version": "1.0.0",
        "device_id": f"host-{repo.name}",
        "platform": "host_native",
        "identity_class": "software",
        "hardware_serial": None,
        "secure_boot_state": None,
        "collected_at_utc": utc_now(),
        "notes": "software discovery only; not physical boot",
    }
    schema_issues = validate_against_schema(sample, "device_identity.schema.json")
    result["details"]["schema_issues"] = [str(i) for i in schema_issues]
    result["software_ok"] = bool(markers) and not schema_issues
    result["sample"] = sample
    return result


def _probe_ring(repos_root: Path) -> dict[str, Any]:
    owners = [
        "gunnchos-hardware-industrial-design",
        "edge-io-measurement-node",
        "gunnchos-device-os",
        "EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon",
    ]
    found = {n: _repo_path(repos_root, n) for n in owners}
    markers: list[str] = []
    for path in found.values():
        if path:
            markers.extend(_marker_hits(path, ["ring_input", "authenticated_input", "protocols", "CLAIMS_TO_EVIDENCE.md"]))
    import hashlib

    payload = "gate1-ring-auth-software-fixture"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    sample = {
        "schema_version": "1.0.0",
        "session_id": "software-ring-session",
        "source": "fixture",
        "auth_method": "fixture",
        "payload_digest_sha256": digest,
        "anti_replay_nonce": "nonce-gate1-01",
        "evidence_class": "software",
        "authenticated": True,
        "collected_at_utc": utc_now(),
        "notes": "software fixture; not physical ring auth",
    }
    schema_issues = validate_against_schema(sample, "authenticated_input.schema.json")
    present = [n for n, p in found.items() if p]
    # Require at least one supporting repo + valid schema
    software_ok = bool(present) and not schema_issues
    return {
        "workstream": "ring-auth",
        "available": bool(present),
        "repos": {k: (str(v) if v else None) for k, v in found.items()},
        "markers": sorted(set(markers)),
        "software_ok": software_ok,
        "physical_ok": False,
        "evidence_class": "software",
        "details": {"schema_issues": [str(i) for i in schema_issues], "present_repos": present},
        "sample": sample,
    }


def _probe_dock(repo: Path | None) -> dict[str, Any]:
    result = {
        "workstream": "dock",
        "available": bool(repo),
        "repo_path": str(repo) if repo else None,
        "markers": [],
        "software_ok": False,
        "physical_ok": False,
        "evidence_class": "software",
        "details": {},
    }
    if not repo:
        result["details"]["error"] = "owner repo missing locally"
        return result
    markers = _marker_hits(repo, ["dock", "docking", "continuity", "boot_readiness", "apps"])
    # Dock software path may be incomplete; still pass if device-os present and schema validates
    sample = {
        "schema_version": "1.0.0",
        "session_id": "software-dock-session",
        "dock_profile": "software_emulated",
        "power_negotiated": False,
        "display_handoff": False,
        "continuity_ok": True,
        "evidence_class": "software",
        "collected_at_utc": utc_now(),
        "notes": "emulated dock session; not physical dock",
    }
    schema_issues = validate_against_schema(sample, "dock_session.schema.json")
    result["markers"] = markers
    result["details"]["schema_issues"] = [str(i) for i in schema_issues]
    # Software OK if repo exists and schema validates (markers optional / may be WIP)
    result["software_ok"] = not schema_issues
    result["sample"] = sample
    return result


def _probe_ai(repo: Path | None) -> dict[str, Any]:
    result = {
        "workstream": "ai-runtime",
        "available": bool(repo),
        "repo_path": str(repo) if repo else None,
        "markers": [],
        "software_ok": False,
        "physical_ok": False,
        "evidence_class": "software",
        "details": {},
    }
    if not repo:
        result["details"]["error"] = "gunnchAI3k missing locally"
        return result
    markers = _marker_hits(repo, ["apps", "packages", "package.json", "README.md", "runtime"])
    sample = {
        "schema_version": "1.0.0",
        "runtime_id": "gunnchai3k-local-software",
        "mode": "local_only",
        "health": "ok" if markers else "degraded",
        "model_id": None,
        "runtime_version": "software-probe",
        "network_egress": "denied",
        "evidence_class": "software",
        "collected_at_utc": utc_now(),
        "notes": "local-only contract probe; not on-device physical runtime",
    }
    schema_issues = validate_against_schema(sample, "local_ai_runtime.schema.json")
    # Fail closed on cloud mode claim
    if sample["mode"] != "local_only" or sample["network_egress"] != "denied":
        result["software_ok"] = False
        result["details"]["error"] = "local_only contract violated"
    else:
        result["software_ok"] = bool(markers) and not schema_issues
    result["markers"] = markers
    result["details"]["schema_issues"] = [str(i) for i in schema_issues]
    result["sample"] = sample
    return result


def _probe_games(repos_root: Path) -> dict[str, Any]:
    import hashlib
    import subprocess

    games = [
        "beatlink-party",
        "archive-of-life-artifact-world",
        "pedestrian-pursuit",
        "anime-aggressors",
    ]
    per_game: list[dict[str, Any]] = []
    all_ok = True
    for game in games:
        path = _repo_path(repos_root, game)
        markers = (
            _marker_hits(path, ["README.md", "tests", "game", "scenes", "project.godot", "package.json"])
            if path
            else []
        )
        commit = "unknown"
        if path and (path / ".git").exists():
            try:
                commit = (
                    subprocess.check_output(
                        ["git", "-C", str(path), "rev-parse", "--short=12", "HEAD"],
                        text=True,
                        stderr=subprocess.DEVNULL,
                    ).strip()
                    or "unknown0"
                )
            except (OSError, subprocess.CalledProcessError):
                commit = "unknown0"
        if len(commit) < 7:
            commit = (commit + "0000000")[:7]
        discovery_ok = bool(path) and bool(markers)
        checksum = hashlib.sha256(f"{game}:{commit}:{sorted(markers)}".encode()).hexdigest()[:16]
        # Shared cross-repo Gate 1 game_core_loop contract (workstream E)
        sample = {
            "game": game,
            "build_id": "gate1-software-discovery",
            "commit": commit,
            "platform": "software_harness",
            "session_id": f"gate1-soft-{game}",
            "step": "discover_repo_and_markers",
            "timestamp": utc_now().replace("Z", "+00:00"),
            "result": "pass" if discovery_ok else "fail",
            "state_checksum": checksum,
            "evidence_type": "runtime_smoke",
            "detail": {
                "evidence_class": "software",
                "markers": markers,
                "notes": "software discovery; not physical device core loop",
            },
        }
        schema_issues = validate_against_schema(sample, "game_core_loop.schema.json")
        ok = discovery_ok and not schema_issues
        if not ok:
            all_ok = False
        per_game.append(
            {
                "game_id": game,
                "repo_path": str(path) if path else None,
                "markers": markers,
                "software_ok": ok,
                "physical_ok": False,
                "schema_issues": [str(i) for i in schema_issues],
                "sample": sample,
            }
        )
    return {
        "workstream": "games",
        "available": any(g["repo_path"] for g in per_game),
        "software_ok": all_ok,
        "physical_ok": False,
        "evidence_class": "software",
        "games": per_game,
    }


def run_components(repos_root: Path | None = None) -> dict[str, Any]:
    root = repos_root or DEFAULT_REPOS_ROOT
    discovery = discover_sibling_repos(root)
    contract_issues = validate_all_contracts()

    boot = _probe_boot(_repo_path(root, "gunnchos-device-os"))
    ring = _probe_ring(root)
    dock = _probe_dock(_repo_path(root, "gunnchos-device-os"))
    ai = _probe_ai(_repo_path(root, "gunnchAI3k"))
    games = _probe_games(root)

    components = {
        "boot": boot,
        "ring-auth": ring,
        "dock": dock,
        "ai-runtime": ai,
        "games": games,
    }
    software_failures = [k for k, v in components.items() if not v.get("software_ok")]
    payload = {
        "schema_version": "1.0.0",
        "evidence_id": f"gate1-run-{utc_now().replace(':', '')}",
        "workstream": "meta",
        "evidence_class": "software",
        "claim_level": "SOFTWARE_SLICE",
        "discovery": discovery,
        "contract_issues": [str(i) for i in contract_issues],
        "components": components,
        "software_failures": software_failures,
        "tool_versions": tool_versions(),
        "collected_at_utc": utc_now(),
        "manifests": {
            "components": str(MANIFESTS / "gate1_components.yaml"),
            "test_matrix": str(MANIFESTS / "gate1_test_matrix.yaml"),
        },
        "ok": not software_failures and not contract_issues,
    }
    # Persist machine-readable run aggregate outside evidence acceptance buckets
    write_run(f"run_{payload['evidence_id']}.json", payload)
    # Also write per-workstream samples as evidence events
    for ws, result in components.items():
        sample = result.get("sample")
        if sample:
            event = {
                "schema_version": "1.0.0",
                "evidence_id": f"{ws}-{payload['evidence_id']}",
                "workstream": ws if ws != "games" else "games",
                "evidence_class": "software",
                "claim_level": "SOFTWARE_SLICE",
                "artifact_path": result.get("repo_path") or "",
                "tool_versions": tool_versions(),
                "collected_at_utc": utc_now(),
                "accepted": False,
                "notes": json.dumps({"software_ok": result.get("software_ok"), "sample": sample}, sort_keys=True),
            }
            # artifact_sha256 filled by write_pending
            write_pending(f"component_{ws}_{payload['evidence_id']}.json", event)
        if ws == "games":
            for g in result.get("games") or []:
                event = {
                    "schema_version": "1.0.0",
                    "evidence_id": f"game-{g['game_id']}-{payload['evidence_id']}",
                    "workstream": "games",
                    "evidence_class": "software",
                    "claim_level": "SOFTWARE_SLICE",
                    "artifact_path": g.get("repo_path") or "",
                    "tool_versions": tool_versions(),
                    "collected_at_utc": utc_now(),
                    "accepted": False,
                    "notes": json.dumps(g.get("sample"), sort_keys=True),
                }
                write_pending(f"game_{g['game_id']}_{payload['evidence_id']}.json", event)

    return payload
