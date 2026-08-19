#!/usr/bin/env python3
"""Wave 001 aggregate verifier — parity matrix + FULL-OPS-017 acceptance."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "engineering_wave001"))

from verify_cross_device_contract import (  # noqa: E402
    REQUIRED_PROBE_KEYS,
    contract_is_operationally_valid,
    load_schema,
    probe_summary,
    validate_contract,
)

GAMES = (
    "anime-aggressors",
    "pedestrian-pursuit",
    "archive-of-life-artifact-world",
    "beatlink-party",
)
ARTIFACT_DIR = ROOT / "artifacts/engineering_wave001"
REQUIREMENTS = (
    "GAME-CROSS-001",
    "GAME-CROSS-002",
    "GAME-CROSS-003",
    "GAME-CROSS-004",
    "GAME-CROSS-005",
    "GAME-CROSS-006",
    "GAME-CROSS-007",
    "GAME-CROSS-008",
    "GAME-CROSS-009",
    "GAME-CROSS-010",
    "GAME-CROSS-011",
    "GATE-1-005",
    "SYS-MISSION-006",
    "FULL-OPS-017",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rules_parity(contracts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    versions = {
        gid: (contracts[gid].get("rules_surface") or {}).get("rules_version")
        for gid in contracts
    }
    unique = {v for v in versions.values() if v}
    per_game_ruleset = {
        gid: (contracts[gid].get("rules_surface") or {}).get("ruleset_id")
        for gid in contracts
    }
    return {
        "rules_versions_observed": versions,
        "ruleset_ids_observed": per_game_ruleset,
        "cross_game_rules_version_collisions": len(unique),
        "note": "Per-game rules_version must be stable across device profiles within each game repo",
    }


def build_parity_matrix(contracts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    matrix: dict[str, Any] = {"games": {}, "requirements": {}}
    for gid, doc in contracts.items():
        matrix["games"][gid] = {
            "contract_version": doc.get("contract_version"),
            "runtime_platform": (doc.get("runtime") or {}).get("platform"),
            "probes": probe_summary(doc),
            "operationally_valid": contract_is_operationally_valid(doc),
            "capability_model": doc.get("capability_model"),
        }

    req_map = {
        "GAME-CROSS-001": lambda g, d: d.get("capability_model") is not None,
        "GAME-CROSS-002": lambda g, d: (d.get("rules_surface") or {}).get("canonical_hash"),
        "GAME-CROSS-003": lambda g, d: (d.get("probes") or {}).get("save_roundtrip", {}).get("status") == "pass",
        "GAME-CROSS-004": lambda g, d: (d.get("probes") or {}).get("score", {}).get("status") == "pass",
        "GAME-CROSS-005": lambda g, d: (d.get("probes") or {}).get("deterministic_replay", {}).get("status") in {"pass", "not_applicable"},
        "GAME-CROSS-006": lambda g, d: (d.get("probes") or {}).get("multiplayer", {}).get("status") in {"pass", "blocked_external", "not_applicable"},
        "GAME-CROSS-007": lambda g, d: (d.get("probes") or {}).get("accessibility", {}).get("status") == "pass",
        "GAME-CROSS-008": lambda g, d: (d.get("probes") or {}).get("input", {}).get("status") == "pass",
        "GAME-CROSS-009": lambda g, d: (d.get("probes") or {}).get("presentation", {}).get("status") == "pass",
        "GAME-CROSS-010": lambda g, d: bool((d.get("input_profile") or {}).get("remapping_persisted")),
        "GAME-CROSS-011": lambda g, d: (d.get("probes") or {}).get("quality", {}).get("status") == "pass",
        "GATE-1-005": lambda g, d: (d.get("probes") or {}).get("core_loop", {}).get("status") == "pass",
        "SYS-MISSION-006": lambda g, d: contract_is_operationally_valid(d),
        "FULL-OPS-017": lambda g, d: contract_is_operationally_valid(d),
    }

    for req_id, checker in req_map.items():
        matrix["requirements"][req_id] = {
            gid: bool(checker(gid, contracts[gid])) if gid in contracts else False
            for gid in GAMES
        }

    matrix["rules_parity"] = _rules_parity(contracts)
    return matrix


def run_full_ops_verifier(contract_paths: dict[str, Path]) -> dict[str, Any]:
    schema = load_schema()
    contracts: dict[str, dict[str, Any]] = {}
    for gid, path in contract_paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"missing contract for {gid}: {path}")
        doc = json.loads(path.read_text(encoding="utf-8"))
        validate_contract(doc, schema)
        if doc.get("game_id") != gid:
            raise ValueError(f"game_id mismatch in {path}: expected {gid}, got {doc.get('game_id')}")
        contracts[gid] = doc

    matrix = build_parity_matrix(contracts)
    all_games_present = len(contracts) == len(GAMES)
    all_operational = all(contract_is_operationally_valid(c) for c in contracts.values())
    result = {
        "schema": "gunnchos.engineering_wave001.full_ops_result.v1",
        "generated_at_utc": _utc_now(),
        "wave": "ENGINEERING_WAVE_001",
        "requirements_targeted": list(REQUIREMENTS),
        "games_submitted": sorted(contracts.keys()),
        "games_missing": [g for g in GAMES if g not in contracts],
        "parity_matrix": matrix,
        "full_ops_017": {
            "all_four_games_submitted": all_games_present,
            "all_contracts_schema_valid": True,
            "all_probes_pass_or_na": all_operational,
            "result": "PASS" if all_games_present and all_operational else "PARTIAL",
        },
        "sys_mission_006": {
            "parity_matrix_from_real_probes": True,
            "result": "PASS" if all_operational else "PARTIAL",
        },
    }
    return result


def write_artifacts(result: dict[str, Any]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_DIR / "FULL_OPS_017_RESULT.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    (ARTIFACT_DIR / "PARITY_MATRIX.json").write_text(
        json.dumps(result["parity_matrix"], indent=2) + "\n", encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contracts-dir",
        type=Path,
        required=True,
        help="Directory containing <game_id>.cross_device_contract.json files",
    )
    parser.add_argument("--write-artifacts", action="store_true")
    args = parser.parse_args(argv)

    paths = {
        gid: args.contracts_dir / f"{gid}.cross_device_contract.json"
        for gid in GAMES
    }
    result = run_full_ops_verifier(paths)
    if args.write_artifacts:
        write_artifacts(result)
    print(json.dumps(result["full_ops_017"], indent=2))
    return 0 if result["full_ops_017"]["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
