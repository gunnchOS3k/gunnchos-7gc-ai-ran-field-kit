#!/usr/bin/env python3
"""Controlled pilot operator CLI.

This tool never pre-fills measurements. It only reports matrix state, validates
real session files, and imports eligible controlled-device sessions.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_collection_coverage import audit  # noqa: E402
from gate3_common import EVIDENCE_PHYSICAL, recursive_privacy_scan, sha256_file  # noqa: E402
from validate_session import validate_session  # noqa: E402

MATRIX = ROOT / "protocols" / "controlled_pilot_matrix.csv"
SANITIZED = ROOT / "datasets" / "controlled" / "sanitized"
CONTRACTS = ROOT / "contracts"


def load_matrix() -> list[dict[str, str]]:
    with MATRIX.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_doc(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def session_cell(doc: dict) -> str:
    ctx = doc.get("session_context") or {}
    batch = doc.get("measurement_batch") or doc
    workload = ctx.get("workload_profile") or (batch.get("workload") or {}).get("profile")
    return f"{ctx.get('collection_day_id')}_{ctx.get('named_test_zone')}_{ctx.get('network_condition')}_{workload}"


def existing_hashes() -> dict[str, str]:
    hashes = {}
    if SANITIZED.is_dir():
        for path in SANITIZED.glob("*.json"):
            hashes[sha256_file(path)] = str(path)
    return hashes


def validate_import(path: Path) -> dict:
    result = validate_session(path, CONTRACTS)
    errors = list(result.get("errors") or [])
    doc = load_doc(path)
    batch = doc.get("measurement_batch") or doc
    ctx = doc.get("session_context") or {}
    evidence = ctx.get("evidence_level") or batch.get("evidence_level")
    collector = (batch.get("provenance") or {}).get("collector")
    consent = (batch.get("consent") or {}).get("status")
    if evidence != EVIDENCE_PHYSICAL:
        errors.append("pilot imports require controlled_device_measurement evidence")
    if collector == "deterministic_emulator":
        errors.append("synthetic/emulator sessions are rejected for pilot counting")
    if evidence in {"synthetic", "calibration_only"}:
        errors.append("synthetic/calibration_only sessions are rejected for pilot counting")
    notes = str(ctx.get("operator_notes") or "")
    deviation = str(ctx.get("protocol_deviation") or "")
    if (
        bool(ctx.get("calibration_only"))
        or "calibration_only=true" in notes.replace(" ", "").lower()
        or deviation == "calibration_not_pilot"
    ):
        errors.append("calibration_only sessions are rejected for pilot counting")
    if consent != "active":
        errors.append("consent.status must be active")
    if (batch.get("consent") or {}).get("status") == "withdrawn":
        errors.append("withdrawn sessions are rejected")
    if doc.get("deleted"):
        errors.append("deleted sessions are rejected")
    planned = float(ctx.get("planned_duration_seconds") or 0)
    actual = float(ctx.get("actual_duration_seconds") or 0)
    if planned >= 300 and actual + 1e-6 < 300:
        errors.append("undersized duration relative to 300s pilot protocol")
    findings = recursive_privacy_scan(doc)
    if findings:
        errors.append("privacy findings present")
    cell = session_cell(doc)
    matrix_cells = {row["cell_id"] for row in load_matrix()}
    if cell not in matrix_cells:
        errors.append(f"session does not map to pilot matrix cell: {cell}")
    digest = sha256_file(path)
    if digest in existing_hashes():
        errors.append(f"duplicate hash already imported: {existing_hashes()[digest]}")
    return {
        "ok": not errors and bool(result.get("ok")),
        "path": str(path),
        "cell_id": cell,
        "hash": digest,
        "errors": errors,
        "validation": result,
    }


def status() -> dict:
    coverage = audit(MATRIX, SANITIZED)
    return {
        "schema_name": "gunnchos.pilot_status",
        "schema_version": "1.0.0",
        "matrix_rows": len(load_matrix()),
        "sanitized_dir": str(SANITIZED),
        "eligible_physical_session_count": coverage["eligible_physical_session_count"],
        "physical_session_count": coverage["physical_session_count"],
        "filled_cells": coverage["filled_cells"],
        "missing_cells": len(coverage["missing_cells"]),
        "rejected_count": len(coverage["rejected"]),
        "duplicate_hashes": coverage["duplicate_hashes"],
        "note": "Synthetic/calibration_only sessions are never counted.",
    }


def next_cell() -> dict:
    coverage = audit(MATRIX, SANITIZED)
    missing = coverage["missing_cells"]
    rows = {row["cell_id"]: row for row in load_matrix()}
    if not missing:
        return {"ok": True, "next": None, "message": "pilot matrix complete"}
    return {"ok": True, "next": rows[missing[0]], "message": "collect this cell; do not prefill measurements"}


def validate_day(day: str) -> dict:
    coverage = audit(MATRIX, SANITIZED)
    rows = [row for row in load_matrix() if row["collection_day_id"] == day]
    day_cells = {row["cell_id"] for row in rows}
    missing = [cell for cell in coverage["missing_cells"] if cell in day_cells]
    return {
        "ok": not missing,
        "day": day,
        "required_cells": len(day_cells),
        "missing_cells": missing,
        "eligible_physical_session_count": coverage["eligible_physical_session_count"],
    }


def write_report(output: Path) -> dict:
    st = status()
    nxt = next_cell()
    output.write_text(
        "# Gate 3 Pilot Status Report\n\n"
        f"- eligible physical sessions: {st['eligible_physical_session_count']}\n"
        f"- filled cells: {st['filled_cells']} / {st['matrix_rows']}\n"
        f"- missing cells: {st['missing_cells']}\n"
        f"- next: `{(nxt.get('next') or {}).get('cell_id')}`\n\n"
        "Synthetic and calibration-only sessions are rejected for pilot counting.\n",
        encoding="utf-8",
    )
    return {"wrote": str(output), "status": st}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("next")
    sub.add_parser("start")
    imp = sub.add_parser("import-session")
    imp.add_argument("session")
    day = sub.add_parser("validate-day")
    day.add_argument("day")
    rep = sub.add_parser("report")
    rep.add_argument("--output", default=str(ROOT / "results" / "gate3" / "GATE3_PILOT_STATUS_REPORT.md"))
    args = p.parse_args(argv)

    if args.cmd == "status":
        print(json.dumps(status(), indent=2))
        return 0
    if args.cmd == "next":
        print(json.dumps(next_cell(), indent=2))
        return 0
    if args.cmd == "start":
        nxt = next_cell()
        print(json.dumps({"ok": True, "cell": nxt.get("next"), "instruction": "collect real measurements per protocol; do not prefill"}, indent=2))
        return 0
    if args.cmd == "validate-day":
        result = validate_day(args.day)
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 2
    if args.cmd == "import-session":
        src = Path(args.session)
        result = validate_import(src)
        if result["ok"]:
            SANITIZED.mkdir(parents=True, exist_ok=True)
            dest = SANITIZED / src.name
            shutil.copyfile(src, dest)
            result["imported_to"] = str(dest)
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 2
    if args.cmd == "report":
        print(json.dumps(write_report(Path(args.output)), indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
