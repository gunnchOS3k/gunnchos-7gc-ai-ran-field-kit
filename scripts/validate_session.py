#!/usr/bin/env python3
"""Validate a Gate 3 measurement session (batch + context)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate3_common import (  # noqa: E402
    EVIDENCE_PHYSICAL,
    EVIDENCE_SYNTHETIC,
    load_json,
    recursive_privacy_scan,
)
from validate_contract import ContractError, validate_document  # noqa: E402


def validate_session(path: Path, contracts_dir: Path) -> dict:
    doc = load_json(path)
    errors: list[str] = []
    privacy = recursive_privacy_scan(doc)
    if privacy:
        errors.append("privacy findings: " + "; ".join(f"{f['path']}:{f['kind']}" for f in privacy[:20]))

    # Accept either a full edge batch or a wrapper with batch+context
    batch = doc.get("measurement_batch", doc)
    context = doc.get("session_context")
    try:
        validate_document(
            batch,
            contracts_dir,
            expected_schema_name="gunnchos.edge_measurement_batch",
            enforce_privacy=True,
        )
    except ContractError as exc:
        errors.append(f"edge batch: {exc}")

    if context is not None:
        try:
            validate_document(
                context,
                contracts_dir,
                expected_schema_name="gunnchos.measurement_session_context",
                enforce_privacy=False,
            )
        except ContractError as exc:
            errors.append(f"session context: {exc}")

        # Consent must predate collection when both present
        consent_at = context.get("consent_captured_at") or (batch.get("consent") or {}).get("captured_at")
        start = context.get("start_timestamp")
        if consent_at and start and consent_at > start:
            errors.append("consent_captured_at must predate start_timestamp")

        evidence = context.get("evidence_level") or batch.get("evidence_level")
        collector = (batch.get("provenance") or {}).get("collector")
        if evidence == EVIDENCE_PHYSICAL and collector == "deterministic_emulator":
            errors.append("physical evidence_level conflicts with emulator collector")
        if evidence == EVIDENCE_SYNTHETIC and collector in {"physical_device", "android_client"}:
            errors.append("synthetic evidence_level conflicts with physical collector")

    ok = not errors
    return {
        "ok": ok,
        "path": str(path),
        "errors": errors,
        "privacy_findings": privacy,
        "evidence_level": batch.get("evidence_level"),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--contracts-dir", default=str(ROOT / "contracts"))
    args = p.parse_args(argv)
    result = validate_session(Path(args.input), Path(args.contracts_dir))
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
