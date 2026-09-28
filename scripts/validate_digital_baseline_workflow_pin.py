#!/usr/bin/env python3
"""Fail if Code Health authenticity pins stale Wave 009 111/51 as current main.

Provenance (already merged closeouts, no human/physical promotion):
  Wave 009 EXPECTED_AFTER: COMPLETE=111 OPEN=51
  Wave 010 GAME-PP-001..015: COMPLETE 111→126, OPEN 51→36
  Wave 011 GAME-AA-001..010: COMPLETE 126→136, OPEN 36→26
Live canonical totals must equal Wave 011 closeout, not Wave 009.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIGITAL = ROOT / "program" / "digital_ecosystem_baseline_v2"
WORKFLOW = ROOT / ".github" / "workflows" / "code-health-authenticity-baseline.yml"
W10 = ROOT / "scripts" / "engineering_wave010" / "run_accepted_main_closeout.py"
W11 = ROOT / "scripts" / "engineering_wave011" / "run_accepted_main_closeout.py"

STALE_CURRENT_TOTAL = re.compile(
    r"""t\[['\"]DIGITAL_IMPLEMENTATION_(COMPLETE|OPEN)['\"]\]\s*==\s*(111|51)"""
)


def _fail(errors: list[str]) -> int:
    print("DIGITAL_BASELINE_WORKFLOW_PIN FAIL")
    for e in errors:
        print(" -", e)
    return 1


def main() -> int:
    errors: list[str] = []
    result_path = DIGITAL / "BASELINE_V2_RESULT.json"
    if not result_path.is_file():
        return _fail([f"missing {result_path.relative_to(ROOT)}"])
    d = json.loads(result_path.read_text())
    t = d.get("totals") or {}
    w9 = ((d.get("ENGINEERING_WAVE_009_TARGETED_CLOSEOUT") or {}).get("EXPECTED_AFTER") or {})
    w10 = d.get("ENGINEERING_WAVE_010_ACCEPTED_MAIN_CLOSEOUT") or {}
    w11 = d.get("ENGINEERING_WAVE_011_ACCEPTED_MAIN_CLOSEOUT") or {}

    if int(t.get("ATOMIC_TOTAL") or 0) != 419:
        errors.append(f"ATOMIC_TOTAL {t.get('ATOMIC_TOTAL')} != 419")
    if int(w9.get("DIGITAL_IMPLEMENTATION_COMPLETE") or 0) != 111:
        errors.append("Wave 009 EXPECTED_AFTER COMPLETE must remain 111 (historical)")
    if int(w9.get("DIGITAL_IMPLEMENTATION_OPEN") or 0) != 51:
        errors.append("Wave 009 EXPECTED_AFTER OPEN must remain 51 (historical)")

    w10_ids = list(w10.get("target_ids") or [])
    w11_ids = list(w11.get("target_ids") or [])
    expect_pp = [f"GAME-PP-{i:03d}" for i in range(1, 16)]
    expect_aa = [f"GAME-AA-{i:03d}" for i in range(1, 11)]
    if w10_ids != expect_pp:
        errors.append(f"Wave 010 target_ids != GAME-PP-001..015 ({w10_ids[:3]}...)")
    if w11_ids != expect_aa:
        errors.append(f"Wave 011 target_ids != GAME-AA-001..010 ({w11_ids[:3]}...)")
    if int(w10.get("COMPLETE") or 0) != 126 or int(w10.get("IMPL_OPEN") or 0) != 36:
        errors.append(f"Wave 010 closeout {w10.get('COMPLETE')}/{w10.get('IMPL_OPEN')} != 126/36")
    if int(w11.get("COMPLETE") or 0) != 136 or int(w11.get("IMPL_OPEN") or 0) != 26:
        errors.append(f"Wave 011 closeout {w11.get('COMPLETE')}/{w11.get('IMPL_OPEN')} != 136/26")

    if int(t.get("DIGITAL_IMPLEMENTATION_COMPLETE") or 0) != int(w11.get("COMPLETE") or 0):
        errors.append("live COMPLETE must equal Wave 011 COMPLETE, not Wave 009 111")
    if int(t.get("DIGITAL_IMPLEMENTATION_OPEN") or 0) != int(w11.get("IMPL_OPEN") or 0):
        errors.append("live OPEN must equal Wave 011 IMPL_OPEN, not Wave 009 51")
    if int(t.get("DIGITAL_VALIDATION_OPEN") or 0) != 0:
        errors.append("DIGITAL_VALIDATION_OPEN must stay 0")
    if int(t.get("EVIDENCE_MAPPING_OPEN") or 0) != 0:
        errors.append("EVIDENCE_MAPPING_OPEN must stay 0")

    moved = int(w11.get("COMPLETE") or 0) - 111
    closed_open = 51 - int(w11.get("IMPL_OPEN") or 0)
    if moved != 25 or closed_open != 25:
        errors.append(f"expected 25-row OPEN→COMPLETE (wave010 15 + wave011 10); got {moved}/{closed_open}")
    if not W10.is_file() or not W11.is_file():
        errors.append("missing wave010/011 accepted-main closeout generators (provenance)")

    for key in (
        "HUMAN_OR_TARGET_HARDWARE_VALIDATED",
        "L4_HUMAN_OR_TARGET_HARDWARE_VALIDATED",
        "PRODUCTION_OR_FIELD",
        "USER_READY_DIGITAL_RC",
        "L3_USER_READY_DIGITAL_RC",
        "L6_PRODUCTION_OR_FIELD",
    ):
        if int(t.get(key) or 0) != 0:
            errors.append(f"{key} must stay 0 (no human/physical promotion)")

    ni = json.loads((DIGITAL / "NEXT_DIGITAL_IMPLEMENTATION_WORK.json").read_text())
    nv = json.loads((DIGITAL / "NEXT_DIGITAL_VALIDATION_WORK.json").read_text())
    if int(nv.get("total_open") if nv.get("total_open") is not None else -1) != 0:
        errors.append(f"NEXT_DIGITAL_VALIDATION_WORK total_open {nv.get('total_open')} != 0")
    live_open = int(t.get("DIGITAL_IMPLEMENTATION_OPEN") if t.get("DIGITAL_IMPLEMENTATION_OPEN") is not None else -1)
    ni_open = int(ni.get("total_open") if ni.get("total_open") is not None else -2)
    if ni_open != live_open:
        errors.append("NEXT_DIGITAL_IMPLEMENTATION_WORK total_open must match live OPEN")

    wf = WORKFLOW.read_text()
    if STALE_CURRENT_TOTAL.search(wf):
        errors.append(
            "workflow still equality-pins live t[DIGITAL_IMPLEMENTATION_*] to 111/51; "
            "those are Wave 009 history only"
        )
    if "validate_digital_baseline_workflow_pin.py" not in wf:
        errors.append("authenticity workflow must invoke this pin script")
    if "ENGINEERING_WAVE_011_ACCEPTED_MAIN_CLOSEOUT" not in wf:
        errors.append("authenticity workflow must bind live totals to Wave 011 provenance")

    if errors:
        return _fail(errors)
    print(
        "DIGITAL_BASELINE_WORKFLOW_PIN OK "
        "wave009=111/51 wave010=GAME-PP-001..015→126/36 "
        "wave011=GAME-AA-001..010→136/26 live=136/26 human=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
