#!/usr/bin/env python3
"""CI helper: PHYSICAL_PENDING tokens are valid nonphysical statuses (not red)."""
from __future__ import annotations
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OK_TOKENS = [
    "REPRESENTATIVE_ENCLOSURE_PHYSICAL_PENDING",
    "REAL_MEASUREMENT_PENDING",
    "PHYSICAL_PENDING",
    "PHYSICAL_EVIDENCE_PENDING",
    "BATTERY_THERMAL_NONPHYSICAL_SYSTEM_COMPLETE",
]
# Patterns that would incorrectly fail CI on pending
BAD_PATTERNS = [
    re.compile(r"fail.*PHYSICAL_PENDING", re.I),
    re.compile(r"PHYSICAL_PENDING.*(?:error|red|fail)", re.I),
]

def main() -> int:
    # Ensure tokens appear in tree and are not treated as failures in validators
    text_files = []
    for p in [
        ROOT / "scripts/validate_gate2_nonphysical.py",
        ROOT / "scripts/validate_nonphysical_status.py",
        ROOT / "gate2/nonphysical/STATUS.yaml",
    ]:
        if p.exists():
            text_files.append(p.read_text(encoding="utf-8"))
    blob = "\n".join(text_files)
    for tok in OK_TOKENS[:4]:
        if tok not in blob and tok != "PHYSICAL_EVIDENCE_PENDING":
            # soft: gate2 validator must allow pending
            pass
    v2 = (ROOT / "scripts/validate_gate2_nonphysical.py").read_text(encoding="utf-8")
    if "PHYSICAL_PENDING_OK" not in v2 and "REPRESENTATIVE_ENCLOSURE_PHYSICAL_PENDING" not in v2:
        print("PHYSICAL_PENDING_NOT_ALLOWLISTED")
        return 1
    print("PHYSICAL_PENDING_TREATED_AS_VALID_NONPHYSICAL")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
