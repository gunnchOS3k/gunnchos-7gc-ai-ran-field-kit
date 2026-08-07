#!/usr/bin/env python3
"""Validate Gate 3 nonphysical totality artifacts."""
from __future__ import annotations
import sys
from pathlib import Path
try:
    import yaml
except ImportError:
    print("pyyaml required"); raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "gate3/nonphysical/STATUS.yaml"
MODS = [
    "G3_C1_identity_continuity", "G3_C2_multi_device_saves", "G3_C3_connectivity_manager",
    "G3_C4_fleet_observability", "G3_C5_threat_models", "G3_C6_7gc_test_plans",
    "G3_C7_repair_procedures",
]

def main() -> int:
    errors = []
    st = yaml.safe_load(STATUS.read_text(encoding="utf-8"))
    if st.get("pass_status") == "PASS" and st.get("irreducible_blockers"):
        errors.append("GATE_3_PASS with irreducible blockers")
    for m in MODS:
        if not (ROOT / "gate3/nonphysical" / m).exists():
            errors.append(f"missing {m}")
    # NTN non-claim
    cm = (ROOT / "gate3/nonphysical/G3_C3_connectivity_manager/connectivity_manager.py").read_text(encoding="utf-8")
    if "real_ntn_claim" not in cm:
        errors.append("connectivity manager missing NTN claim boundary")
    if errors:
        print("GATE3_NONPHYSICAL_FAIL")
        for e in errors:
            print("-", e)
        return 1
    crit = st.get("criteria") or {}
    if all(v == "NONPHYSICAL_COMPLETE" for v in crit.values()) and len(crit) >= 7:
        print("GATE3_NONPHYSICAL_ARTIFACTS_OK")
        print("claim_allowed=GATE_3_NONPHYSICAL_COMPLETE")
        print("pass_status=", st.get("pass_status"))
        return 0
    print("GATE3_NONPHYSICAL_INCOMPLETE")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
