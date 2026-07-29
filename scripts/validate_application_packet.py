#!/usr/bin/env python3
"""Validate application packet completeness and reject material unresolved placeholders."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "application"

REQUIRED = [
    "MASTER_APPLICATION_INDEX.md",
    "RESEARCH_PLAN_3_PAGE.md",
    "RESEARCH_PLAN_6_PAGE.md",
    "ABSTRACT_250_WORDS.md",
    "ABSTRACT_LONG.md",
    "SUPERVISION_PLAN.md",
    "FIRST_YEAR_RESEARCH_PLAN.md",
    "THREE_PAPER_ROADMAP.md",
    "SELECTED_PORTFOLIO.md",
    "ACADEMIC_CV_AUDIT.md",
    "CLAIMS_VERIFICATION_MATRIX.csv",
    "ELIGIBILITY_AND_DOCUMENT_CHECKLIST.md",
    "REFEREE_PACKET_CHECKLIST.md",
    "SUBMISSION_READINESS_CHECKLIST.md",
    "APPLICATION_PACKET_STATUS.md",
]

# Material unresolved placeholders that must not appear in "ready" claims.
# Explicit PENDING_* tokens are allowed in status docs when labeled as human actions.
FORBIDDEN_IN_READY_BODY = [
    re.compile(r"\bTODO: fill me\b", re.I),
    re.compile(r"\bTBD_RESULT_NUMBER\b"),
    re.compile(r"\bINSERT_PERFORMANCE\b", re.I),
    re.compile(r"\bFABRICATED\b"),
    re.compile(r"\bDOI:\s*10\.\d+/PENDING_ACTIVE\b", re.I),
]

FORBIDDEN_COMMITMENT = [
    re.compile(r"\b(has agreed to supervise|endorsed by Professor|funding confirmed)\b", re.I),
]


def validate() -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    missing = [f for f in REQUIRED if not (APP / f).is_file()]
    if missing:
        errors.extend(f"missing application/{m}" for m in missing)

    status_path = APP / "APPLICATION_PACKET_STATUS.md"
    packet_ready_claimed = False
    if status_path.is_file():
        text = status_path.read_text(encoding="utf-8")
        if re.search(r"APPLICATION_PACKET_READY\s*[:=]\s*PASS", text, re.I):
            packet_ready_claimed = True
        if re.search(r"\bPASS\b", text) and "HUMAN_ACTION" not in text and "0/54" not in text:
            warnings.append("status doc may under-specify pending gates")

    for path in APP.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".md", ".csv", ".txt"}:
            continue
        body = path.read_text(encoding="utf-8", errors="replace")
        rel = str(path.relative_to(ROOT))
        for pat in FORBIDDEN_IN_READY_BODY:
            if pat.search(body):
                errors.append(f"{rel}: forbidden placeholder {pat.pattern}")
        for pat in FORBIDDEN_COMMITMENT:
            if pat.search(body):
                errors.append(f"{rel}: implies unverified faculty/funding commitment")

    if packet_ready_claimed:
        # Packet cannot be PASS while Gate 3 incomplete.
        master = ROOT / "research-application-control" / "MASTER_STATUS.json"
        if master.is_file():
            data = json.loads(master.read_text(encoding="utf-8"))
            g3 = (data.get("gates") or {}).get("GATE_3_PASS") or {}
            if g3.get("status") != "PASS":
                errors.append(
                    "APPLICATION_PACKET_READY claimed PASS while GATE_3_PASS is not PASS"
                )

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "required_count": len(REQUIRED),
        "present_count": len(REQUIRED) - len(missing),
    }


def main(argv=None) -> int:
    argparse.ArgumentParser().parse_args(argv)
    result = validate()
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
