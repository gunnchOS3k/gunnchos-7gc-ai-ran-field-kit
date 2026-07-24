#!/usr/bin/env python3
"""Validate MASTER_STATUS.json: schema + PASS requires evidence files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "research-application-control" / "MASTER_STATUS.json"
SCHEMA_PATH = (
    ROOT / "research-application-control" / "schemas" / "master_status.v1.schema.json"
)

REQUIRED_GATES = [
    "GATE_1_PASS",
    "GATE2_SYSTEM_PASS",
    "PROVENANCE_AND_PROTOCOL_FROZEN",
    "PILOT_DESIGN_APPROVED",
    "GATE_3_PASS",
    "EVALUATION_PREREGISTERED",
    "GATE_4_PASS",
    "GATE_5_PASS",
    "GATE_6_PASS",
    "GATE_7_PASS",
    "GENERALIZATION_EVIDENCE_PASS",
    "EXTERNAL_SCHOLARLY_REVIEW_PASS",
    "TECHNICAL_DEFENSE_READY",
    "PORTFOLIO_REVIEW_READY",
    "APPLICATION_PACKET_READY",
]

ALLOWED_STATUSES = {
    "PASS",
    "AUTOMATION_READY",
    "HUMAN_ACTION_REQUIRED",
    "EXTERNAL_DEPENDENCY",
    "BLOCKED",
    "FAIL",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(status_path: Path = STATUS_PATH, repo_root: Path = ROOT) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not status_path.is_file():
        return {"ok": False, "errors": [f"missing {status_path}"], "warnings": []}

    data = load_json(status_path)
    if data.get("application_complete") is True:
        errors.append("application_complete must remain false until all authentic gates PASS")

    gates = data.get("gates") or {}
    for name in REQUIRED_GATES:
        if name not in gates:
            errors.append(f"missing gate: {name}")
            continue
        g = gates[name]
        status = g.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{name}: invalid status {status!r}")
        evidence = g.get("evidence") or []
        if status == "PASS":
            if not evidence:
                errors.append(f"{name}: PASS without evidence list")
            for rel in evidence:
                p = repo_root / rel
                if not p.exists():
                    errors.append(f"{name}: PASS evidence missing: {rel}")
            unmet = g.get("unmet") or []
            if unmet:
                errors.append(f"{name}: PASS with unmet requirements: {unmet}")

        if name == "GATE_3_PASS":
            eligible = int(g.get("eligible_sessions", data.get("eligible_pilot_sessions", -1)))
            required = int(g.get("required_sessions", data.get("required_pilot_sessions", 54)))
            if status == "PASS" and eligible < required:
                errors.append(
                    f"GATE_3_PASS cannot be PASS with eligible_sessions={eligible} < {required}"
                )
            if eligible > 0 and eligible < required and status == "PASS":
                errors.append("GATE_3_PASS forged while incomplete")

    if data.get("eligible_pilot_sessions", 0) != gates.get("GATE_3_PASS", {}).get(
        "eligible_sessions", data.get("eligible_pilot_sessions", 0)
    ):
        warnings.append("eligible_pilot_sessions top-level vs GATE_3 field mismatch")

    # Optional JSON Schema if jsonschema installed
    if SCHEMA_PATH.is_file():
        try:
            import jsonschema  # type: ignore

            schema = load_json(SCHEMA_PATH)
            jsonschema.validate(data, schema)
        except ImportError:
            warnings.append("jsonschema not installed; skipped schema validation")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"schema validation failed: {exc}")

    return {"ok": not errors, "errors": errors, "warnings": warnings, "gates": list(gates)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--status", default=str(STATUS_PATH))
    p.add_argument("--repo-root", default=str(ROOT))
    args = p.parse_args(argv)
    result = validate(Path(args.status), Path(args.repo_root))
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
