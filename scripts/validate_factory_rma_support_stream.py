#!/usr/bin/env python3
"""Honesty gate for the factory / RMA / support STREAM."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STREAM = ROOT / "program" / "streams" / "factory_rma_support"

FORBIDDEN_CLAIMS = (
    "PRODUCTION_RELEASE_CLAIMED: true",
    "production_keys: true",
    "production_ca: true",
    "commercial_warranty: ACTIVE",
    "rfq_purchase_fab: COMPLETE",
)


def main() -> int:
    stream = yaml.safe_load((STREAM / "STREAM.yaml").read_text(encoding="utf-8"))
    schema = json.loads((STREAM / "ops_schema.json").read_text(encoding="utf-8"))
    boundary = (STREAM / "CLAIM_BOUNDARY.md").read_text(encoding="utf-8")
    errors: list[str] = []
    if stream.get("PRODUCTION_RELEASE_CLAIMED") is not False:
        errors.append("PRODUCTION_RELEASE_CLAIMED must be false")
    if stream.get("cursor_merges") is not False:
        errors.append("Cursor never merges")
    if stream.get("commercial_warranty") != "EXTERNAL":
        errors.append("commercial_warranty must be EXTERNAL")
    if stream.get("rfq_purchase_fab") != "NOT_THIS_STREAM":
        errors.append("rfq_purchase_fab must be NOT_THIS_STREAM")
    if stream.get("production_keys") is not False:
        errors.append("production_keys must be false")
    if stream.get("production_ca") is not False:
        errors.append("production_ca must be false")
    if stream.get("status") != "DIGITAL_PREPARATION":
        errors.append("status must be DIGITAL_PREPARATION")
    if schema["properties"]["PRODUCTION_RELEASE_CLAIMED"].get("const") is not False:
        errors.append("schema must const-false PRODUCTION_RELEASE_CLAIMED")
    if "EXTERNAL" not in boundary or "false" not in boundary.lower():
        errors.append("CLAIM_BOUNDARY must state EXTERNAL and false tokens")
    text = (STREAM / "STREAM.yaml").read_text(encoding="utf-8") + boundary
    for phrase in FORBIDDEN_CLAIMS:
        if phrase.lower() in text.lower():
            errors.append(f"forbidden claim: {phrase}")
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("PASS factory-rma-support STREAM honesty gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
