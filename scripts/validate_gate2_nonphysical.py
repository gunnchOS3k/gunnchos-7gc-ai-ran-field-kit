#!/usr/bin/env python3
"""Validate Gate 2 nonphysical totality artifacts."""
from __future__ import annotations
import json, sys
from pathlib import Path
try:
    import yaml
except ImportError:
    print("pyyaml required"); raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "gate2/nonphysical/STATUS.yaml"
DESIGNS = ROOT / "device_designs"
REQUIRED_DEVICES = ["student_14_5", "handheld_hybrid", "ds_xl_coder", "edge_io_rings"]
REQUIRED_FILES = [
    "requirements.yaml", "architecture.md", "block_diagram.md", "block_diagram.mmd",
    "interface_control_document.md", "component_bom.csv",
]
REQUIRED_DIRS = ["electrical", "mechanical", "firmware", "os", "manufacturing", "validation"]
PHYSICAL_PENDING_OK = {
    "REPRESENTATIVE_ENCLOSURE_PHYSICAL_PENDING",
    "REAL_MEASUREMENT_PENDING",
    "PHYSICAL_PENDING",
    "PHYSICAL_EVIDENCE_PENDING",
}

def main() -> int:
    errors = []
    st = yaml.safe_load(STATUS.read_text(encoding="utf-8"))
    if st.get("claim_forbidden") != "GATE_2_PASS":
        errors.append("STATUS must forbid GATE_2_PASS")
    if st.get("pass_status") == "PASS":
        errors.append("GATE_2_PASS must not be set from nonphysical package")
    for did in REQUIRED_DEVICES:
        base = DESIGNS / did
        if not base.exists():
            errors.append(f"missing device_designs/{did}")
            continue
        for f in REQUIRED_FILES:
            if not (base / f).exists():
                errors.append(f"{did}: missing {f}")
        for d in REQUIRED_DIRS:
            if not (base / d).is_dir():
                errors.append(f"{did}: missing dir {d}")
        req = yaml.safe_load((base / "requirements.yaml").read_text(encoding="utf-8"))
        if req.get("physical_status") not in PHYSICAL_PENDING_OK:
            errors.append(f"{did}: physical_status must be PHYSICAL_PENDING token")
    # criterion modules
    for mod in [
        "G2_C2_display_controls", "G2_C3_battery_thermal", "G2_C4_secure_boot",
        "G2_C5_signed_update", "G2_C6_device_game_ux", "G2_C7_ring_calibration",
        "G2_C1_enclosure",
    ]:
        if not (ROOT / "gate2/nonphysical" / mod).exists():
            errors.append(f"missing {mod}")
    # PHYSICAL_PENDING is valid nonphysical status (not red)
    for token in PHYSICAL_PENDING_OK:
        if token.startswith("GATE_") and token.endswith("_PASS"):
            errors.append("PASS token incorrectly in pending set")
    if errors:
        print("GATE2_NONPHYSICAL_FAIL")
        for e in errors:
            print("-", e)
        return 1
    # Mark complete if criteria all NONPHYSICAL_COMPLETE
    crit = st.get("criteria") or {}
    if all(v == "NONPHYSICAL_COMPLETE" for v in crit.values()) and len(crit) >= 7:
        print("GATE2_NONPHYSICAL_ARTIFACTS_OK")
        print("claim_allowed=GATE_2_NONPHYSICAL_COMPLETE")
        print("claim_forbidden=GATE_2_PASS")
        return 0
    print("GATE2_NONPHYSICAL_INCOMPLETE")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
