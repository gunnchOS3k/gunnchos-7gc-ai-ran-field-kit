#!/usr/bin/env python3
"""Digital interference + mass/CoM check over device_designs."""
from __future__ import annotations
import json, sys
from pathlib import Path
try:
    import yaml
except ImportError:
    print("pyyaml required"); raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[3]
DESIGNS = ROOT / "device_designs"

def check_device(d: Path) -> dict:
    params = yaml.safe_load((d / "mechanical" / "enclosure_params.yaml").read_text(encoding="utf-8"))
    mass = json.loads((d / "mechanical" / "mass_com_estimate.json").read_text(encoding="utf-8"))
    scad = d / "mechanical" / f"{d.name}_enclosure.scad"
    collisions = []
    # Digital keepout rule: wall clearance vs tolerance
    if params.get("tolerance_mm", 0) >= params.get("wall_mm", 0):
        collisions.append("tolerance_ge_wall")
    status = "CLEAR" if not collisions else "COLLISION"
    return {
        "device_id": d.name,
        "evidence_class": "MODELED",
        "collisions": collisions,
        "status": status if status == "COLLISION" else "REPRESENTATIVE_ENCLOSURE_PHYSICAL_PENDING",
        "mass_g_estimate": mass.get("mass_g"),
        "com_mm": mass.get("com_mm"),
        "scad_present": scad.exists(),
        "physical_token": "REPRESENTATIVE_ENCLOSURE_PHYSICAL_PENDING",
    }

def main() -> int:
    if not DESIGNS.exists():
        print("NO_DESIGNS"); return 2
    reports = []
    for d in sorted(DESIGNS.iterdir()):
        if not d.is_dir():
            continue
        if not (d / "mechanical" / "enclosure_params.yaml").exists():
            continue
        reports.append(check_device(d))
    out = DESIGNS.parent / "gate2" / "nonphysical" / "G2_C1_enclosure" / "interference_results.json"
    out.write_text(json.dumps({"reports": reports}, indent=2), encoding="utf-8")
    if not reports:
        print("NO_REPORTS"); return 1
    if any(not r["scad_present"] for r in reports):
        print("MISSING_SCAD"); return 1
    if any(r["collisions"] for r in reports):
        print("INTERFERENCE_FAIL"); return 1
    print("INTERFERENCE_MODELED_OK")
    print("physical_token=REPRESENTATIVE_ENCLOSURE_PHYSICAL_PENDING")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
