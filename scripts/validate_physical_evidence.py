#!/usr/bin/env python3
"""Validate physical evidence records against schema. Never auto-promotes PENDING→PASS."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gates_4_6_common import ROOT, utc_now, write_json  # noqa: E402

try:
    import jsonschema
except ImportError:
    jsonschema = None

SCHEMA_DIR = ROOT / "schemas"
REGISTRY = ROOT / "PHYSICAL_EVIDENCE_REGISTRY.json"

SCHEMA_MAP = {
    "physical_evidence": "physical_evidence.schema.json",
    "lab_instrument": "lab_instrument_manifest.schema.json",
    "user_study": "user_study_session.schema.json",
}


def pick_schema(path: Path, data: dict) -> Path | None:
    name = path.name.lower()
    if "user_study" in name or "participant_id_scheme" in data:
        return SCHEMA_DIR / SCHEMA_MAP["user_study"]
    if "lab_instrument" in name or "instruments" in data:
        return SCHEMA_DIR / SCHEMA_MAP["lab_instrument"]
    if "evidence_id" in data or "field_session" in name:
        return SCHEMA_DIR / SCHEMA_MAP["physical_evidence"]
    if path.name.endswith("_TEMPLATE.json") or "REPLACE" in json.dumps(data):
        return None  # templates are not validated as evidence records
    return SCHEMA_DIR / SCHEMA_MAP["physical_evidence"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, help="Single evidence JSON to validate")
    args = parser.parse_args()
    if jsonschema is None:
        print(json.dumps({"ok": False, "error": "jsonschema missing"}))
        return 1
    paths = []
    if args.path:
        paths = [args.path]
    else:
        paths = list((ROOT / "physical_evidence").rglob("*.json"))
    results = []
    ok = True
    for p in paths:
        if p.name.endswith(".schema.json"):
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if "entries" in data and "evidence_id" not in data:
                results.append({"path": str(p), "skipped": True, "reason": "registry"})
                continue
            schema_path = pick_schema(p, data)
            if schema_path is None:
                results.append({"path": str(p), "skipped": True, "reason": "template"})
                continue
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            jsonschema.validate(instance=data, schema=schema)
            if data.get("status") == "VALID" and data.get("evidence_label") in (
                "SYNTHETIC_EXPERIMENT",
                "BLOCKED_HARDWARE",
            ):
                results.append(
                    {
                        "path": str(p),
                        "ok": False,
                        "error": "VALID status incompatible with synthetic/blocked label",
                    }
                )
                ok = False
            else:
                results.append(
                    {
                        "path": str(p),
                        "ok": True,
                        "status": data.get("status"),
                        "schema": schema_path.name,
                    }
                )
        except Exception as exc:  # noqa: BLE001
            results.append({"path": str(p), "ok": False, "error": str(exc)})
            ok = False
    report = {"checked_at": utc_now(), "ok": ok, "results": results, "registry": str(REGISTRY)}
    write_json(ROOT / "orchestration" / "gates_4_6" / "validate_physical_evidence.json", report)
    print(json.dumps(report, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
