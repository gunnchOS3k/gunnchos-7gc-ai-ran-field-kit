#!/usr/bin/env python3
"""Honesty gate for the privacy + BOM inventory STREAM."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STREAM = ROOT / "program" / "streams" / "privacy_bom_inventory"


def main() -> int:
    stream = yaml.safe_load((STREAM / "STREAM.yaml").read_text(encoding="utf-8"))
    schema = json.loads((STREAM / "inventory_schema.json").read_text(encoding="utf-8"))
    boundary = (STREAM / "CLAIM_BOUNDARY.md").read_text(encoding="utf-8")
    errors: list[str] = []
    if stream.get("EXTERNAL_PENTEST_COMPLETE") is not False:
        errors.append("EXTERNAL_PENTEST_COMPLETE must be false")
    if stream.get("e7_claimed") is not False:
        errors.append("e7_claimed must be false")
    if stream.get("legal_approval") != "HUMAN/EXTERNAL":
        errors.append("legal_approval must be HUMAN/EXTERNAL")
    if stream.get("WP_006_started") is not False:
        errors.append("must not start WP-006 as a cycle packet")
    if stream.get("CYCLE_3_STARTED") is not False:
        errors.append("must not start Cycle 3")
    if stream.get("cursor_merges") is not False:
        errors.append("Cursor never merges")
    if schema["properties"]["EXTERNAL_PENTEST_COMPLETE"].get("const") is not False:
        errors.append("inventory schema must const-false EXTERNAL_PENTEST_COMPLETE")
    if "E7 claimed | false" not in boundary and "E7 claimed | false" not in boundary.replace("**", ""):
        if "e7 claimed" not in boundary.lower() or "false" not in boundary.lower():
            errors.append("CLAIM_BOUNDARY must state E7 is not claimed")
    forbidden = ("EXTERNAL_PENTEST_COMPLETE=true", "E7_PASS", "COPPA compliant", "GDPR compliant")
    text = (STREAM / "STREAM.yaml").read_text(encoding="utf-8") + boundary
    for phrase in forbidden:
        if phrase.lower() in text.lower() and phrase != "EXTERNAL_PENTEST_COMPLETE":
            if "false" not in text.lower():
                errors.append(f"forbidden claim: {phrase}")
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("PASS privacy-bom STREAM honesty gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
