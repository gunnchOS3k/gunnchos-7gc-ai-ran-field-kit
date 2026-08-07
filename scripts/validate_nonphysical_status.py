#!/usr/bin/env python3
"""Validate orthogonal nonphysical vs PASS status; reject PASS inferred from NP."""
from __future__ import annotations
import json, sys
from pathlib import Path
try:
    import yaml
except ImportError:
    print("pyyaml required"); raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "program/nonphysical/gate_nonphysical_status.yaml"
SCHEMA = ROOT / "program/nonphysical/gate_nonphysical_status.schema.json"

FORBIDDEN_PASS_FROM_NP = True

def main() -> int:
    data = yaml.safe_load(STATUS.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    try:
        import jsonschema
        jsonschema.validate(data, schema)
    except ImportError:
        pass
    except Exception as exc:
        print("SCHEMA_FAIL", exc)
        return 2
    errors = []
    for gid, g in (data.get("gates") or {}).items():
        np = g.get("nonphysical_status")
        ps = g.get("pass_status")
        if ps == "PASS" and np == "BLOCKED_NONPHYSICAL":
            errors.append(f"gate {gid}: PASS while nonphysical blocked")
        if gid == "8" and ps == "PASS":
            errors.append("GATE_8_PASS forbidden until normative path")
        if np == "NONPHYSICAL_COMPLETE" and ps == "PASS":
            # Allowed only if blockers empty AND not gate 8; still requires authentic evidence process elsewhere
            if g.get("irreducible_blockers"):
                errors.append(f"gate {gid}: PASS claimed with irreducible blockers still listed")
    if data.get("physical_execution_freeze") not in ("ACTIVE", "RELEASED_PENDING_EDMUND_REVIEW", "INACTIVE"):
        errors.append("invalid freeze token")
    if errors:
        print("NONPHYSICAL_STATUS_FAIL")
        for e in errors:
            print("-", e)
        return 1
    print("NONPHYSICAL_STATUS_PASS")
    print("physical_execution_freeze=", data.get("physical_execution_freeze"))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
