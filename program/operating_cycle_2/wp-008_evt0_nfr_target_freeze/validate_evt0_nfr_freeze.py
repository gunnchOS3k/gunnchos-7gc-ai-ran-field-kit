#!/usr/bin/env python3
"""Validate WP-008 EVT0 NFR freeze artifacts (implementer integrity check; not VP-008)."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = [
    "target_id","product","journey_refs","risk_refs","strategy","metric","unit",
    "measurement_method","instrument_or_fixture","threshold","target","stretch",
    "operating_condition","sample_duration","percentile_or_statistic","evidence_level",
    "source_rationale","source_date","confidence","physical_pending",
]
STRATEGIES = {"MUST_MATCH","MUST_EXCEED","NOT_RELEVANT","DIFFERENT_APPROACH"}
EXIT_FILES = [
    "EVT0_NFR_TARGET_REGISTRY.json",
    "EVT0_NFR_SOURCE_LEDGER.md",
    "EVT0_COMPETITOR_TARGET_MATRIX.json",
    "EVT0_TARGET_MEASUREMENT_MAP.json",
    "EVT0_TBD_RESIDUALS.json",
]

def main() -> int:
    errs: list[str] = []
    for name in EXIT_FILES:
        if not (ROOT / name).exists():
            errs.append(f"missing {name}")
    if errs:
        print("FAIL"); [print(e) for e in errs]; return 1
    reg = json.loads((ROOT / "EVT0_NFR_TARGET_REGISTRY.json").read_text())
    comp = json.loads((ROOT / "EVT0_COMPETITOR_TARGET_MATRIX.json").read_text())
    mmap = json.loads((ROOT / "EVT0_TARGET_MEASUREMENT_MAP.json").read_text())
    if not reg.get("freeze", {}).get("EVT0_NFR_TARGET_REGISTRY_FROZEN"):
        errs.append("EVT0_NFR_TARGET_REGISTRY_FROZEN not true")
    if reg.get("doctrine", {}).get("frontier_parity_claimed"):
        errs.append("frontier_parity_claimed must be false")
    for t in reg.get("targets", []):
        tid = t.get("target_id")
        for k in REQUIRED:
            if k not in t:
                errs.append(f"{tid}: missing {k}")
        if t.get("competitor_score") is not None:
            errs.append(f"{tid}: competitor_score must be null")
        if t.get("strategy") not in STRATEGIES:
            errs.append(f"{tid}: invalid strategy")
    if not all(c.get("competitor_score") is None for c in comp.get("capabilities", [])):
        errs.append("competitor matrix contains non-null scores")
    if len(mmap.get("mappings", [])) != len(reg.get("targets", [])):
        errs.append("measurement map size != registry size")
    if errs:
        print("FAIL")
        for e in errs:
            print("-", e)
        return 1
    print("PASS")
    print(f"targets={len(reg['targets'])} competitor_caps={len(comp['capabilities'])}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
