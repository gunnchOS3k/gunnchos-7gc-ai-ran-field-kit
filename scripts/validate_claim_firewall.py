#!/usr/bin/env python3
"""Reject forbidden *assertive* claim phrases in nonphysical/program reports.

Charter criterion titles and backlog item names that merely name a requirement
(e.g. "Gate 7: Production manufacturing") are not treated as claims of achievement.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = [
    ROOT / "program" / "nonphysical",
    ROOT / "program" / "physical",
    ROOT / "program" / "reports",
    ROOT / "program" / "credentials",
    ROOT / "device_designs",
    ROOT / "gate2",
    ROOT / "gate3",
    ROOT / "gate4",
    ROOT / "gate5",
    ROOT / "gate6",
    ROOT / "gate7",
    ROOT / "gate8",
    ROOT / "standards",
]

# Assertive achievement phrasing (not bare criterion titles).
FORBIDDEN = [
    r"\bis carrier-grade deployed\b",
    r"\bis 6G certified\b",
    r"\bis IMT-2030 compliant\b",
    r"\bwe achieved production manufacturing\b",
    r"\bcarrier accepted\b",
    r"\bis FCC/CE certified\b",
    r"\bpilot validated\b",
    r"\bis field proven\b",
    r"\breal battery measurement (complete|pass|accepted)\b",
    r"\breal thermal measurement (complete|pass|accepted)\b",
    r"\bphysical ring validated\b",
    r"\bsecure boot physically validated\b",
    r"\b(earned|achieved|declared|granted)\s+GATE_8_PASS\b",
    r"\bgate\s*8\s*:\s*PASS\b",
]

ALLOW_LINE = re.compile(
    r"(?i)(not |never |forbidden|pending|do not|without claiming|must not|reject|"
    r"criterion|title:|blocked until|NOT_CLAIM|prohibited|token_pass:|"
    r"tokens:|GATE_8_PASS forbidden|pass_axis)"
)


def main() -> int:
    pat = re.compile("|".join(f"({p})" for p in FORBIDDEN), re.I)
    hits: list[str] = []
    for d in SCAN_DIRS:
        if not d.exists():
            continue
        for path in d.rglob("*"):
            if path.suffix.lower() not in {".md", ".yaml", ".yml", ".json", ".txt"}:
                continue
            if "claim_firewall" in path.name or "prohibited_claim" in path.name:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for i, line in enumerate(text.splitlines(), 1):
                if not pat.search(line):
                    continue
                if ALLOW_LINE.search(line):
                    continue
                hits.append(f"{path}:{i}:{line.strip()[:160]}")
    if hits:
        print("CLAIM_FIREWALL_FAIL")
        for h in hits[:50]:
            print(h)
        return 1
    print("CLAIM_FIREWALL_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
