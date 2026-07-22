#!/usr/bin/env python3
"""Audit collection coverage against the 54-cell matrix."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate3_common import EVIDENCE_PHYSICAL, load_json, sha256_file  # noqa: E402


def load_matrix(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def session_docs(session_dir: Path) -> list[tuple[Path, dict]]:
    docs = []
    if not session_dir.is_dir():
        return docs
    for path in sorted(session_dir.glob("*.json")):
        docs.append((path, load_json(path)))
    return docs


def extract_cell_keys(doc: dict) -> dict:
    ctx = doc.get("session_context") or {}
    batch = doc.get("measurement_batch") or doc
    return {
        "collection_day_id": ctx.get("collection_day_id"),
        "zone_id": ctx.get("named_test_zone"),
        "network_condition": ctx.get("network_condition"),
        "workload_profile": ctx.get("workload_profile")
        or (batch.get("workload") or {}).get("profile"),
        "evidence_level": ctx.get("evidence_level") or batch.get("evidence_level"),
        "consent_status": (batch.get("consent") or {}).get("status"),
        "withdrawn": (batch.get("consent") or {}).get("status") == "withdrawn",
        "deleted": bool(doc.get("deleted")),
        "session_hash": None,
    }


def audit(matrix_path: Path, sessions_dir: Path) -> dict:
    matrix = load_matrix(matrix_path)
    required = {r["cell_id"]: r for r in matrix}
    filled: dict[str, list[str]] = {cid: [] for cid in required}
    rejected = []
    hashes: dict[str, list[str]] = {}
    eligible = 0
    physical = 0
    calibration = 0

    for path, doc in session_docs(sessions_dir):
        meta = extract_cell_keys(doc)
        ctx = doc.get("session_context") or {}
        h = sha256_file(path)
        hashes.setdefault(h, []).append(str(path))
        if meta["evidence_level"] != EVIDENCE_PHYSICAL:
            rejected.append({"path": str(path), "reason": "not_physical_evidence"})
            continue
        physical += 1
        # reject synthetic relabel: emulator collector
        batch = doc.get("measurement_batch") or doc
        if (batch.get("provenance") or {}).get("collector") == "deterministic_emulator":
            rejected.append({"path": str(path), "reason": "emulator_provenance"})
            continue
        if meta["withdrawn"] or meta["deleted"]:
            rejected.append({"path": str(path), "reason": "withdrawn_or_deleted"})
            continue
        if meta["consent_status"] != "active":
            rejected.append({"path": str(path), "reason": "consent_not_active"})
            continue
        notes = str(ctx.get("operator_notes") or "")
        deviation = str(ctx.get("protocol_deviation") or "")
        is_calibration = (
            bool(ctx.get("calibration_only"))
            or "calibration_only=true" in notes.replace(" ", "").lower()
            or deviation == "calibration_not_pilot"
        )
        if is_calibration:
            calibration += 1
            rejected.append(
                {
                    "path": str(path),
                    "reason": "calibration_only_excluded_from_pilot_matrix",
                    "counts_toward_pilot": False,
                }
            )
            continue
        cell = f"{meta['collection_day_id']}_{meta['zone_id']}_{meta['network_condition']}_{meta['workload_profile']}"
        if cell not in required:
            rejected.append({"path": str(path), "reason": f"unknown_cell:{cell}"})
            continue
        if len(hashes[h]) > 1:
            rejected.append({"path": str(path), "reason": "duplicate_hash"})
            continue
        filled[cell].append(str(path))
        eligible += 1

    missing = [cid for cid, files in filled.items() if not files]
    days = {r["collection_day_id"] for r in matrix if filled[r["cell_id"]]}
    zones = {r["zone_id"] for r in matrix if filled[r["cell_id"]]}
    nets = {r["network_condition"] for r in matrix if filled[r["cell_id"]]}
    workloads = Counter()
    for r in matrix:
        if filled[r["cell_id"]]:
            workloads[r["workload_profile"]] += 1

    return {
        "required_cells": len(required),
        "filled_cells": len(required) - len(missing),
        "missing_cells": missing,
        "physical_session_count": physical,
        "eligible_physical_session_count": eligible,
        "calibration_session_count": calibration,
        "observed_counts": {
            "locations": len(zones),
            "network_conditions": len(nets),
            "distinct_days": len(days),
            "workload_profiles": dict(workloads),
            "eligible_sessions": eligible,
            "calibration_sessions": calibration,
        },
        "required_counts": {
            "locations": 3,
            "network_conditions": 2,
            "distinct_days": 3,
            "workload_profiles": {"learn": 18, "create": 18, "sense": 18},
            "cells": 54,
            "planned_duration_seconds": 300,
        },
        "rejected": rejected,
        "duplicate_hashes": {h: paths for h, paths in hashes.items() if len(paths) > 1},
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--matrix", required=True)
    p.add_argument("--sessions", required=True)
    p.add_argument("--output", default=None)
    args = p.parse_args(argv)
    result = audit(Path(args.matrix), Path(args.sessions))
    text = json.dumps(result, indent=2)
    print(text)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
