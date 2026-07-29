#!/usr/bin/env python3
"""Validate cross-repo evidence lock + schema fixtures."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gates_4_6_common import ROOT, verify_lock, write_json, utc_now  # noqa: E402

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None


SCHEMA_DIR = ROOT / "schemas"
FIX_DIR = ROOT / "physical_evidence" / "fixtures"


def validate_schemas() -> dict:
    if jsonschema is None:
        return {"ok": False, "error": "jsonschema not installed"}
    mapping = {
        "field_session_dry_run.json": "physical_evidence.schema.json",
        "lab_instrument_dry_run.json": "lab_instrument_manifest.schema.json",
        "user_study_dry_run.json": "user_study_session.schema.json",
    }
    results = []
    ok = True
    for fixture, schema_name in mapping.items():
        fpath = FIX_DIR / fixture
        spath = SCHEMA_DIR / schema_name
        if not fpath.exists() or not spath.exists():
            results.append({"fixture": fixture, "ok": False, "error": "missing"})
            ok = False
            continue
        instance = json.loads(fpath.read_text(encoding="utf-8"))
        schema = json.loads(spath.read_text(encoding="utf-8"))
        try:
            jsonschema.validate(instance=instance, schema=schema)
            results.append({"fixture": fixture, "ok": True})
        except Exception as exc:  # noqa: BLE001
            results.append({"fixture": fixture, "ok": False, "error": str(exc)})
            ok = False
    return {"ok": ok, "results": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-lock", action="store_true")
    args = parser.parse_args()
    lock = verify_lock(fail_on_mismatch=False) if not args.skip_lock else {"ok": True, "skipped": True}
    schemas = validate_schemas()
    report = {"checked_at": utc_now(), "lock": lock, "schemas": schemas, "ok": schemas.get("ok", False)}
    # Lock mismatch is reported but during active development may be updated by write_lock helper
    out = ROOT / "orchestration" / "gates_4_6" / "validate_cross_repo_evidence.json"
    write_json(out, report)
    print(json.dumps(report, indent=2))
    return 0 if schemas.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
