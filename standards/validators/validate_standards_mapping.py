#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
STD = ROOT / "standards"
REQUIRED = [STD/"sources.yaml", STD/"requirements"/"imt2030_current_state.yaml",
            STD/"mappings"/"device_subsystem_compatibility.yaml"]
def main() -> int:
    missing=[str(p) for p in REQUIRED if not p.exists()]
    if missing:
        print("STANDARDS_VALIDATE_FAIL missing", missing); return 1
    snaps=list((STD/"source_snapshots").glob("*.md"))
    if len(snaps) < 2:
        print("STANDARDS_VALIDATE_FAIL need snapshots"); return 1
    print("STANDARDS_VALIDATE_PASS"); return 0
if __name__ == "__main__": raise SystemExit(main())
