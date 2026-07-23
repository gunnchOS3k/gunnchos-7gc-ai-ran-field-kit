#!/usr/bin/env python3
"""Controlled pilot operator CLI.

Never pre-fills measurements. Emits assignment contracts, validates sessions,
and imports only eligible controlled-device pilot sessions.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_collection_coverage import audit  # noqa: E402
from assignment_canonical import (  # noqa: E402
    ALGORITHM_V1,
    assignment_hash as canonical_assignment_hash,
    hash_payload,
    stamp_hash,
    verify_hash,
)
from gate3_common import EVIDENCE_PHYSICAL, recursive_privacy_scan, sha256_file  # noqa: E402
from validate_contract import ContractError, validate_document  # noqa: E402
from validate_session import validate_session  # noqa: E402

MATRIX = ROOT / "protocols" / "controlled_pilot_matrix.csv"
SANITIZED = ROOT / "datasets" / "controlled" / "sanitized"
ASSIGNMENTS = ROOT / "datasets" / "controlled" / "assignments"
CONTRACTS = ROOT / "contracts"
PROTOCOL_VERSION = "gate3-pilot-v1"
ASSIGNMENT_LEDGER = ASSIGNMENTS / "used_assignment_ids.json"


def canonical_assignment_bytes(doc: dict) -> bytes:
    _, canonical = hash_payload(doc)
    return canonical


def assignment_hash(doc: dict) -> str:
    return canonical_assignment_hash(doc)


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def utc_iso(dt: datetime | None = None) -> str:
    value = dt or utc_now()
    return value.isoformat().replace("+00:00", "Z")


def load_matrix() -> list[dict[str, str]]:
    with MATRIX.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_doc(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "0" * 40


def expected_transport(network_condition: str) -> str:
    if network_condition.startswith("wifi"):
        return "wifi"
    if network_condition.startswith("cellular"):
        return "cellular"
    if "local_network" in network_condition:
        return "wifi"
    return "unavailable"


def load_used_assignments() -> dict:
    if ASSIGNMENT_LEDGER.is_file():
        return json.loads(ASSIGNMENT_LEDGER.read_text(encoding="utf-8"))
    return {"used_assignment_ids": {}, "used_hashes": {}}


def save_used_assignments(ledger: dict) -> None:
    ASSIGNMENTS.mkdir(parents=True, exist_ok=True)
    ASSIGNMENT_LEDGER.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")


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


def validate_assignment(path: Path) -> dict:
    doc = load_doc(path)
    errors: list[str] = []
    try:
        validate_document(
            doc,
            CONTRACTS,
            expected_schema_name="gunnchos.pilot_assignment",
            enforce_privacy=False,
        )
    except ContractError as exc:
        errors.append(str(exc))
    expected = assignment_hash(doc)
    if doc.get("assignment_hash") != expected:
        errors.append("assignment_hash does not match canonical payload")
    algo = doc.get("assignment_hash_algorithm")
    if algo not in (None, ALGORITHM_V1):
        errors.append(f"unknown assignment_hash_algorithm: {algo}")
    if algo is None:
        # Legacy files without the field remain hash-checkable but are flagged.
        errors.append("assignment_hash_algorithm missing (require gunnchos-canonical-json-sha256-v1)")
    expires = doc.get("expires_at")
    if expires and expires < utc_iso():
        errors.append("assignment expired")
    mode = doc.get("session_mode")
    if mode == "PILOT":
        matrix_cells = {row["cell_id"] for row in load_matrix()}
        if doc.get("matrix_cell_id") not in matrix_cells:
            errors.append(f"matrix_cell_id not in pilot matrix: {doc.get('matrix_cell_id')}")
        if doc.get("calibration_only") is True or doc.get("rehearsal_only") is True:
            errors.append("PILOT assignment cannot be calibration_only or rehearsal_only")
        if float(doc.get("planned_duration_seconds") or 0) < 300:
            errors.append("PILOT assignment duration must be >= 300 seconds")
    if mode == "PILOT_REHEARSAL":
        if doc.get("rehearsal_only") is not True:
            errors.append("PILOT_REHEARSAL requires rehearsal_only=true")
        if doc.get("calibration_only") is True:
            errors.append("PILOT_REHEARSAL cannot be calibration_only")
        if doc.get("collection_day_id") != "rehearsal_day":
            errors.append("PILOT_REHEARSAL requires collection_day_id=rehearsal_day")
    if mode == "CALIBRATION":
        if doc.get("calibration_only") is not True:
            errors.append("CALIBRATION requires calibration_only=true")
    ledger = load_used_assignments()
    asn = doc.get("assignment_id")
    if asn and asn in ledger.get("used_assignment_ids", {}):
        errors.append(f"assignment_id already consumed: {asn}")
    return {"ok": not errors, "path": str(path), "errors": errors, "assignment": doc}


def build_assignment_from_row(
    row: dict[str, str],
    *,
    session_mode: str,
    calibration_only: bool,
    rehearsal_only: bool,
    ttl_hours: int = 24,
) -> dict:
    created = utc_now()
    expires = created + timedelta(hours=ttl_hours)
    assignment_id = f"asn_{uuid.uuid4().hex[:16]}"
    zone = row["zone_id"]
    day = row["collection_day_id"]
    condition = row["network_condition"]
    doc = {
        "schema_name": "gunnchos.pilot_assignment",
        "schema_version": "1.0.0",
        "assignment_id": assignment_id,
        "matrix_cell_id": row["cell_id"],
        "protocol_version": PROTOCOL_VERSION,
        "collection_day_id": day,
        "named_test_zone": zone,
        "location_category": row["location_category"],
        "indoor_outdoor": "indoor"
        if "indoor" in row["location_category"]
        else ("outdoor" if "outdoor" in row["location_category"] else "mixed"),
        "stationary_or_moving": "stationary",
        "network_condition": condition,
        "expected_network_transport": expected_transport(condition),
        "workload_profile": row["workload_profile"],
        "planned_duration_seconds": int(float(row["planned_duration_seconds"])),
        "session_mode": session_mode,
        "calibration_only": calibration_only,
        "rehearsal_only": rehearsal_only,
        "environmental_note_prompt": (
            "Optional notes only. Do not enter street addresses, names, emails, "
            "phone numbers, SSIDs, or other identifiers. Max 280 characters."
        ),
        "created_at": utc_iso(created),
        "expires_at": utc_iso(expires),
        "expiry_policy": f"expires_{ttl_hours}h_after_emit",
        "site_id": "gary",
        "assignment_hash_algorithm": ALGORITHM_V1,
        "producer": {
            "repository": "gunnchos-7gc-ai-ran-field-kit",
            "commit": git_commit(),
        },
    }
    stamped = stamp_hash(doc)
    # Refuse to emit if the stamped hash cannot be reproduced.
    check = verify_hash(stamped)
    if not check["ok"]:
        raise RuntimeError(f"assignment hash failed self-check: {check}")
    return stamped


def emit_assignment(output: Path, cell_id: str | None = None) -> dict:
    rows = {row["cell_id"]: row for row in load_matrix()}
    if cell_id is None:
        nxt = next_cell()
        if not nxt.get("next"):
            return {"ok": False, "errors": ["no missing pilot cells"]}
        cell_id = nxt["next"]["cell_id"]
    if cell_id not in rows:
        return {"ok": False, "errors": [f"unknown cell_id: {cell_id}"]}
    doc = build_assignment_from_row(
        rows[cell_id],
        session_mode="PILOT",
        calibration_only=False,
        rehearsal_only=False,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    roundtrip = verify_roundtrip(output)
    if not roundtrip.get("ok"):
        output.unlink(missing_ok=True)
        return {"ok": False, "errors": roundtrip.get("errors", ["roundtrip failed"]), "roundtrip": roundtrip}
    return {"ok": True, "path": str(output), "assignment": doc, "roundtrip": roundtrip}


def emit_rehearsal(output: Path) -> dict:
    row = {
        "cell_id": "rehearsal_zone_rehearsal_wifi_normal_learn",
        "collection_day_id": "rehearsal_day",
        "zone_id": "zone_rehearsal",
        "location_category": "home_or_private_indoor",
        "network_condition": "wifi_normal",
        "workload_profile": "learn",
        "planned_duration_seconds": "300",
    }
    doc = build_assignment_from_row(
        row,
        session_mode="PILOT_REHEARSAL",
        calibration_only=False,
        rehearsal_only=True,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    roundtrip = verify_roundtrip(output)
    if not roundtrip.get("ok"):
        output.unlink(missing_ok=True)
        return {"ok": False, "errors": roundtrip.get("errors", ["roundtrip failed"]), "roundtrip": roundtrip}
    return {"ok": True, "path": str(output), "assignment": doc, "roundtrip": roundtrip}


def verify_roundtrip(path: Path) -> dict:
    """Parse → canonicalize → hash → rewrite temp → parse again → compare."""
    errors: list[str] = []
    original = load_doc(path)
    check = verify_hash(original)
    if not check["ok"]:
        errors.append(
            f"hash mismatch declared={check.get('declared')} calculated={check.get('calculated')}"
        )
    try:
        validate_document(
            original,
            CONTRACTS,
            expected_schema_name="gunnchos.pilot_assignment",
            enforce_privacy=False,
        )
    except ContractError as exc:
        errors.append(str(exc))
    tmp = path.with_suffix(path.suffix + ".roundtrip.tmp")
    try:
        # Rewrite with sorted keys to prove key order independence of the hash.
        rewritten = {k: original[k] for k in sorted(original.keys())}
        # Nest producer with reversed key insertion order.
        if isinstance(rewritten.get("producer"), dict):
            prod = rewritten["producer"]
            rewritten["producer"] = {k: prod[k] for k in reversed(list(prod.keys()))}
        tmp.write_text(json.dumps(rewritten, indent=2) + "\n", encoding="utf-8")
        again = load_doc(tmp)
        check2 = verify_hash(again)
        if again.get("assignment_hash") != original.get("assignment_hash"):
            errors.append("rewritten file assignment_hash changed")
        if not check2["ok"]:
            errors.append("rewritten file failed hash verification")
        semantic_keys = [
            "assignment_id",
            "matrix_cell_id",
            "session_mode",
            "collection_day_id",
            "named_test_zone",
            "planned_duration_seconds",
            "assignment_hash_algorithm",
        ]
        for key in semantic_keys:
            if again.get(key) != original.get(key):
                errors.append(f"semantic drift on {key}")
        if type(again.get("planned_duration_seconds")) is float:
            # Accept float only if integer-valued; prefer int.
            if not float(again["planned_duration_seconds"]).is_integer():
                errors.append("planned_duration_seconds must be integer-valued")
    finally:
        if tmp.exists():
            tmp.unlink()
    return {
        "ok": not errors,
        "path": str(path),
        "errors": errors,
        "hash_check": check,
        "assignment_id": original.get("assignment_id"),
        "assignment_hash": original.get("assignment_hash"),
    }


def validate_import(path: Path) -> dict:
    result = validate_session(path, CONTRACTS)
    errors = list(result.get("errors") or [])
    doc = load_doc(path)
    batch = doc.get("measurement_batch") or doc
    ctx = doc.get("session_context") or {}
    evidence = ctx.get("evidence_level") or batch.get("evidence_level")
    collector = (batch.get("provenance") or {}).get("collector")
    consent = (batch.get("consent") or {}).get("status")
    mode = ctx.get("session_mode")
    calibration_only = bool(ctx.get("calibration_only"))
    rehearsal_only = bool(ctx.get("rehearsal_only"))
    notes = str(ctx.get("operator_notes") or "")
    deviation = str(ctx.get("protocol_deviation") or "")

    if evidence != EVIDENCE_PHYSICAL:
        errors.append("pilot imports require controlled_device_measurement evidence")
    if collector == "deterministic_emulator":
        errors.append("synthetic/emulator sessions are rejected for pilot counting")
    if evidence in {"synthetic", "calibration_only"}:
        errors.append("synthetic/calibration_only sessions are rejected for pilot counting")
    if (
        calibration_only
        or mode == "CALIBRATION"
        or "calibration_only=true" in notes.replace(" ", "").lower()
        or deviation == "calibration_not_pilot"
    ):
        errors.append("calibration_only sessions are rejected for pilot counting")
    if rehearsal_only or mode == "PILOT_REHEARSAL" or deviation == "rehearsal_not_pilot":
        errors.append("rehearsal_only sessions are rejected for pilot counting")
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

    # Assignment binding required only for explicit PILOT mode (counting path).
    if mode == "PILOT":
        for field in ("assignment_id", "assignment_hash", "matrix_cell_id", "protocol_version"):
            if not ctx.get(field):
                errors.append(f"pilot session missing session_context.{field}")
        asn = ctx.get("assignment_id")
        ledger = load_used_assignments()
        if asn and asn in ledger.get("used_assignment_ids", {}):
            errors.append(f"assignment_id already used: {asn}")
        cell = ctx.get("matrix_cell_id") or session_cell(doc)
        matrix_cells = {row["cell_id"]: row for row in load_matrix()}
        if cell not in matrix_cells:
            errors.append(f"session does not map to pilot matrix cell: {cell}")
        else:
            row = matrix_cells[cell]
            if ctx.get("collection_day_id") != row["collection_day_id"]:
                errors.append("session day differs from assignment/matrix day")
            if ctx.get("named_test_zone") != row["zone_id"]:
                errors.append("session zone differs from assignment/matrix zone")
            if ctx.get("network_condition") != row["network_condition"]:
                if "network_condition_mismatch" not in deviation:
                    errors.append("session network_condition differs without documented deviation")
            if ctx.get("workload_profile") != row["workload_profile"]:
                errors.append("session workload differs from assignment/matrix workload")
        producer_commit = (batch.get("producer") or {}).get("commit")
        if not isinstance(producer_commit, str) or len(producer_commit) != 40:
            errors.append("missing/invalid producer.commit")
        if producer_commit == "unknown_local_build":
            errors.append("unknown_local_build cannot count toward pilot")
        if (batch.get("provenance") or {}).get("build_dirty") is True:
            errors.append("dirty builds cannot count toward pilot")
    else:
        # Non-pilot modes (and legacy fixtures): still map cell id for reporting.
        cell = ctx.get("matrix_cell_id") or session_cell(doc)
        if mode not in {"CALIBRATION", "PILOT_REHEARSAL"} and not calibration_only and not rehearsal_only:
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
        "session_mode": mode,
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
        "note": "Synthetic/calibration_only/rehearsal_only sessions are never counted.",
    }


def next_cell() -> dict:
    coverage = audit(MATRIX, SANITIZED)
    missing = coverage["missing_cells"]
    rows = {row["cell_id"]: row for row in load_matrix()}
    if not missing:
        return {"ok": True, "next": None, "message": "pilot matrix complete"}
    return {
        "ok": True,
        "next": rows[missing[0]],
        "message": "collect this cell; do not prefill measurements",
    }


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
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "# Gate 3 Pilot Status Report\n\n"
        f"- eligible physical sessions: {st['eligible_physical_session_count']}\n"
        f"- filled cells: {st['filled_cells']} / {st['matrix_rows']}\n"
        f"- missing cells: {st['missing_cells']}\n"
        f"- next: `{(nxt.get('next') or {}).get('cell_id')}`\n\n"
        "Synthetic, calibration-only, and rehearsal-only sessions are rejected for pilot counting.\n",
        encoding="utf-8",
    )
    return {"wrote": str(output), "status": st}


def import_session(src: Path) -> dict:
    result = validate_import(src)
    if result["ok"]:
        SANITIZED.mkdir(parents=True, exist_ok=True)
        dest = SANITIZED / src.name
        shutil.copyfile(src, dest)
        result["imported_to"] = str(dest)
        doc = load_doc(src)
        ctx = doc.get("session_context") or {}
        asn = ctx.get("assignment_id")
        if asn:
            ledger = load_used_assignments()
            ledger.setdefault("used_assignment_ids", {})[asn] = {
                "session_file": str(dest),
                "cell_id": result.get("cell_id"),
                "imported_at": utc_iso(),
            }
            if ctx.get("assignment_hash"):
                ledger.setdefault("used_hashes", {})[ctx["assignment_hash"]] = asn
            save_used_assignments(ledger)
    return result


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    nxt = sub.add_parser("next")
    nxt.add_argument("--json", action="store_true", help="machine-readable next cell")
    sub.add_parser("start")
    emit = sub.add_parser("emit-assignment")
    emit.add_argument("--output", required=True)
    emit.add_argument("--cell-id", default=None)
    reh = sub.add_parser("emit-rehearsal")
    reh.add_argument("--output", required=True)
    vasn = sub.add_parser("validate-assignment")
    vasn.add_argument("assignment")
    vrt = sub.add_parser("verify-roundtrip")
    vrt.add_argument("assignment")
    imp = sub.add_parser("import-session")
    imp.add_argument("session")
    day = sub.add_parser("validate-day")
    day.add_argument("day")
    rep = sub.add_parser("report")
    rep.add_argument(
        "--output",
        default=str(ROOT / "results" / "gate3" / "GATE3_PILOT_STATUS_REPORT.md"),
    )
    args = p.parse_args(argv)

    if args.cmd == "status":
        print(json.dumps(status(), indent=2))
        return 0
    if args.cmd == "next":
        print(json.dumps(next_cell(), indent=2))
        return 0
    if args.cmd == "start":
        nxt_payload = next_cell()
        print(
            json.dumps(
                {
                    "ok": True,
                    "cell": nxt_payload.get("next"),
                    "instruction": "collect real measurements per protocol; do not prefill",
                },
                indent=2,
            )
        )
        return 0
    if args.cmd == "emit-assignment":
        result = emit_assignment(Path(args.output), cell_id=args.cell_id)
        print(json.dumps(result, indent=2))
        return 0 if result.get("ok") else 2
    if args.cmd == "emit-rehearsal":
        result = emit_rehearsal(Path(args.output))
        print(json.dumps(result, indent=2))
        return 0 if result.get("ok") else 2
    if args.cmd == "validate-assignment":
        result = validate_assignment(Path(args.assignment))
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 2
    if args.cmd == "verify-roundtrip":
        result = verify_roundtrip(Path(args.assignment))
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 2
    if args.cmd == "validate-day":
        result = validate_day(args.day)
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 2
    if args.cmd == "import-session":
        result = import_session(Path(args.session))
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 2
    if args.cmd == "report":
        print(json.dumps(write_report(Path(args.output)), indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
