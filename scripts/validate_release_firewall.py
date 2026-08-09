#!/usr/bin/env python3
"""Cont VII release firewall — digital release / pre-manufacturing claim guard.

Companion to validate_claim_firewall.py. Fails when release-facing tokens exceed
accepted-main digital evidence:

- PRE_MANUFACTURING_RELEASE_COMPLETE / DIGITAL_RELEASE_TOTALITY while backlog > 0
- FULL_* release tokens while Cont VII digitally executable backlog remains
- Treating Cont VII sibling draft tips as accepted mains
- Opening the true final umbrella while DIGITAL_BACKLOG is non-zero
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
FP = ROOT / "program" / "full_product"
CONT_VII = FP / "continuation_vii"
BACKLOG = CONT_VII / "DIGITAL_BACKLOG.json"
BASELINE = CONT_VII / "ACCEPTED_MAIN_BASELINE.json"
DRAFTS = CONT_VII / "continuation_vii_sibling_draft_registry.yaml"
SOFT = FP / "software_integration_matrix.yaml"
HW = FP / "hardware_release_matrix.yaml"
MASTER = FP / "reports" / "FULL_PRODUCT_MASTER_STATUS.md"

FORBIDDEN_RELEASE = [
    r"\bPRE_MANUFACTURING_RELEASE_COMPLETE\b",
    r"\bDIGITAL_RELEASE_TOTALITY\b",
    r"\bFULL_PRODUCT_DIGITAL_TOTALITY\b",
    r"\bTRUE_FINAL_UMBRELLA_OPEN\b",
    r"\bMANUFACTURING_ORDER_AUTHORIZED\b",
]

ALLOW = re.compile(
    r"(?i)(not |never |forbidden|pending|do not|without claiming|must not|reject|"
    r"false|: false|:false|not earned|not claimed|not opened|blocked until|"
    r"draft tip|not accepted|not final umbrella)"
)


def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> Any:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def backlog_remaining() -> int:
    data = load_json(BACKLOG)
    return int(
        int(data.get("DIGITALLY_EXECUTABLE_SCHEMA_ONLY") or 0)
        + int(data.get("DIGITALLY_EXECUTABLE_STUB_ONLY") or 0)
        + int(data.get("DIGITALLY_EXECUTABLE_SIMULATION_ONLY") or 0)
        + int(data.get("DIGITALLY_EXECUTABLE_MOCK_ONLY") or 0)
    )


def main() -> int:
    hits: list[str] = []
    if not CONT_VII.exists():
        print("RELEASE_FIREWALL_FAIL")
        print("missing program/full_product/continuation_vii/")
        return 1
    for name in (
        "ACCEPTED_MAIN_BASELINE.json",
        "REQUIREMENT_PROOF.json",
        "REQUIREMENT_COUNTS.json",
        "REQUIREMENT_PROMOTION_LEDGER.json",
        "DIGITAL_BACKLOG.json",
        "PHYSICAL_IRREDUCIBILITY_AUDIT.json",
        "EXTERNAL_IRREDUCIBILITY_AUDIT.json",
    ):
        if not (CONT_VII / name).exists():
            hits.append(f"missing Cont VII artifact: {name}")

    remaining = backlog_remaining()
    baseline = load_json(BASELINE)
    if baseline.get("final_umbrella") is True and remaining > 0:
        hits.append("ACCEPTED_MAIN_BASELINE.final_umbrella=true while digital backlog remains")
    if baseline.get("continuation") != "VII":
        hits.append("ACCEPTED_MAIN_BASELINE.continuation must be VII")

    drafts = load_yaml(DRAFTS)
    if drafts.get("final_umbrella") is True and remaining > 0:
        hits.append("sibling draft registry marks final_umbrella=true while backlog remains")
    if drafts.get("policy") != "DRAFT_TIPS_NOT_ACCEPTED_MAIN_NOT_FINAL_UMBRELLA":
        hits.append("sibling draft registry policy must declare draft tips are not accepted mains")

    # Draft tips must not silently replace accepted mains.
    # Equal SHAs are allowed when the draft is still branched_from_accepted_main
    # (no Cont VII commits yet) or explicitly MERGED_TO_MAIN.
    accepted = (baseline.get("accepted_mains") or {}) if isinstance(baseline, dict) else {}
    for key, entry in (drafts.get("drafts") or {}).items():
        if not isinstance(entry, dict):
            continue
        repo = entry.get("repo")
        sha = entry.get("sha")
        if not repo or not sha or repo not in accepted:
            continue
        if sha != accepted[repo]:
            continue
        status = str(entry.get("status") or "")
        note = str(entry.get("note") or "").lower()
        allowed = (
            key == "field_kit_accepted_main_reproof"
            or status in {"MERGED_TO_MAIN", "BRANCHED_FROM_ACCEPTED_MAIN_PENDING_COMMITS"}
            or "not accepted main" in note
            or "draft tip not accepted" in note
            or entry.get("base_accepted_main") == sha
        )
        if not allowed:
            hits.append(
                f"draft {key}: tip SHA equals accepted main for {repo} without "
                "MERGED_TO_MAIN / pending-commits marker"
            )

    soft = load_yaml(SOFT)
    if soft.get("final_umbrella") is True and remaining > 0:
        hits.append("software_integration_matrix.final_umbrella=true while backlog remains")
    hw = load_yaml(HW)
    if hw.get("full_complete_claimed") is True:
        hits.append("hardware_release_matrix.full_complete_claimed=true forbidden under Cont VII")

    pat = re.compile("|".join(f"({p})" for p in FORBIDDEN_RELEASE))
    for path in (SOFT, HW, MASTER, BACKLOG, BASELINE):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for i, line in enumerate(text.splitlines(), 1):
            if not pat.search(line):
                continue
            if ALLOW.search(line):
                continue
            if remaining > 0:
                hits.append(
                    f"{path}:{i}: release token asserted while Cont VII digital backlog={remaining}"
                )

    if hits:
        print("RELEASE_FIREWALL_FAIL")
        for h in hits[:80]:
            print(h)
        return 1
    print("RELEASE_FIREWALL_PASS")
    print(f"digitally_executable_backlog_remaining={remaining}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
