#!/usr/bin/env python3
"""Cont VIII release firewall — digital release / readiness scorecard guard.

Extends Cont VII release firewall:

- PRE_MANUFACTURING_RELEASE_COMPLETE / DIGITAL_RELEASE_TOTALITY while backlog > 0
- FULL_* / DIGITAL_PRE_EVT_RELEASE_READY while Cont VIII digitally executable backlog remains
- Treating Cont VIII sibling draft tips as accepted mains
- Opening the true final umbrella while DIGITAL_BACKLOG is non-zero
- manufacturer_ready / assembly_ready / adopter_ready / recreation_ready /
  student_ready / office_work_ready = true without required artifacts
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
CONT_VIII = FP / "continuation_viii"
CONT_VII = FP / "continuation_vii"
SOFT = FP / "software_integration_matrix.yaml"
HW = FP / "hardware_release_matrix.yaml"
MASTER = FP / "reports" / "FULL_PRODUCT_MASTER_STATUS.md"

FORBIDDEN_RELEASE = [
    r"\bPRE_MANUFACTURING_RELEASE_COMPLETE\b",
    r"\bDIGITAL_RELEASE_TOTALITY\b",
    r"\bFULL_PRODUCT_DIGITAL_TOTALITY\b",
    r"\bTRUE_FINAL_UMBRELLA_OPEN\b",
    r"\bMANUFACTURING_ORDER_AUTHORIZED\b",
    r"\bDIGITAL_PRE_EVT_RELEASE_READY\b",
]

ALLOW = re.compile(
    r"(?i)(not |never |forbidden|pending|do not|without claiming|must not|reject|"
    r"false|: false|:false|not earned|not claimed|not opened|blocked until|"
    r"draft tip|not accepted|not final umbrella|must remain false|is not claimed)"
)

GUARDED_READY_FLAGS = (
    "manufacturer_ready",
    "assembly_ready",
    "adopter_ready",
    "recreation_ready",
    "student_ready",
    "office_work_ready",
)


def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> Any:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def active_cont() -> Path:
    if (CONT_VIII / "DIGITAL_BACKLOG.json").exists():
        return CONT_VIII
    return CONT_VII


def backlog_path() -> Path:
    cont = active_cont()
    return cont / "DIGITAL_BACKLOG.json"


def baseline_path() -> Path:
    cont = active_cont()
    return cont / "ACCEPTED_MAIN_BASELINE.json"


def drafts_path() -> Path:
    if active_cont() == CONT_VIII:
        return CONT_VIII / "continuation_viii_sibling_draft_registry.yaml"
    return CONT_VII / "continuation_vii_sibling_draft_registry.yaml"


def backlog_remaining() -> int:
    data = load_json(backlog_path())
    return int(
        int(data.get("DIGITALLY_EXECUTABLE_SCHEMA_ONLY") or 0)
        + int(data.get("DIGITALLY_EXECUTABLE_STUB_ONLY") or 0)
        + int(data.get("DIGITALLY_EXECUTABLE_SIMULATION_ONLY") or 0)
        + int(data.get("DIGITALLY_EXECUTABLE_MOCK_ONLY") or 0)
    )


def check_scorecard_firewall(hits: list[str]) -> None:
    scorecard = CONT_VIII / "READINESS_SCORECARD.json"
    if not scorecard.exists():
        if (CONT_VIII / "REQUIREMENT_COUNTS.json").exists():
            hits.append("missing Cont VIII READINESS_SCORECARD.json")
        return
    doc = load_json(scorecard)
    if doc.get("continuation") != "VIII":
        hits.append("READINESS_SCORECARD.continuation must be VIII")
    if doc.get("digital_pre_evt_release_ready") is True:
        hits.append(
            "READINESS_SCORECARD.digital_pre_evt_release_ready=true forbidden "
            "without Edmund acceptance pack"
        )
    if doc.get("physical_execution_freeze") is not True:
        hits.append("READINESS_SCORECARD.physical_execution_freeze must be true")

    score = doc.get("scorecard") or {}
    subcriteria = doc.get("subcriteria") or {}
    for flag in GUARDED_READY_FLAGS:
        if score.get(flag) is not True:
            continue
        sub = subcriteria.get(flag) or {}
        arts = list(sub.get("required_artifacts") or [])
        missing = list(sub.get("missing") or [])
        if not arts:
            hits.append(f"{flag}=true without required_artifacts enumeration")
            continue
        if any(a.startswith("FORBIDDEN_UNTIL_") for a in arts):
            hits.append(
                f"{flag}=true while required_artifacts still include FORBIDDEN_UNTIL_*"
            )
        if missing:
            hits.append(f"{flag}=true with missing artifacts: {missing[:8]}")
        if sub.get("satisfied") is not True:
            hits.append(f"{flag}=true while subcriteria.satisfied is not true")
        for rel in arts:
            if rel.startswith("FORBIDDEN_UNTIL_"):
                continue
            if not (ROOT / rel).exists():
                hits.append(f"{flag}=true but missing artifact path: {rel}")


def check_gates_firewall(hits: list[str]) -> None:
    gates_path = CONT_VIII / "READINESS_GATES.json"
    if not gates_path.exists():
        if (CONT_VIII / "REQUIREMENT_COUNTS.json").exists():
            hits.append("missing Cont VIII READINESS_GATES.json")
        return
    doc = load_json(gates_path)
    if doc.get("continuation") != "VIII":
        hits.append("READINESS_GATES.continuation must be VIII")
    if doc.get("digital_pre_evt_release_ready") is True:
        hits.append("READINESS_GATES.digital_pre_evt_release_ready=true forbidden")
    gates = doc.get("gates") or {}
    for gid in ("R1", "R2", "R3", "R4", "R5", "R6"):
        if gid not in gates:
            hits.append(f"READINESS_GATES missing gate {gid}")


def check_blockers_firewall(hits: list[str]) -> None:
    blockers = CONT_VIII / "REMAINING_BLOCKERS.yaml"
    if not blockers.exists():
        if (CONT_VIII / "REQUIREMENT_COUNTS.json").exists():
            hits.append("missing Cont VIII REMAINING_BLOCKERS.yaml")
        return
    data = load_yaml(blockers)
    buckets = data.get("buckets") or {}
    allowed = {"DIGITAL", "PHYSICAL", "EXTERNAL"}
    if set(buckets) != allowed:
        hits.append("REMAINING_BLOCKERS must define exactly DIGITAL|PHYSICAL|EXTERNAL")


def main() -> int:
    hits: list[str] = []
    active = active_cont()
    label = "VIII" if active == CONT_VIII else "VII"
    if not active.exists():
        print("RELEASE_FIREWALL_FAIL")
        print("missing program/full_product/continuation_viii/ (and no Cont VII fallback)")
        return 1

    required = [
        "ACCEPTED_MAIN_BASELINE.json",
        "REQUIREMENT_PROOF.json",
        "REQUIREMENT_COUNTS.json",
        "REQUIREMENT_PROMOTION_LEDGER.json",
        "DIGITAL_BACKLOG.json",
        "PHYSICAL_IRREDUCIBILITY_AUDIT.json",
        "EXTERNAL_IRREDUCIBILITY_AUDIT.json",
    ]
    if active == CONT_VIII:
        required += [
            "READINESS_SCORECARD.json",
            "READINESS_GATES.json",
            "REMAINING_BLOCKERS.yaml",
            "continuation_viii_sibling_draft_registry.yaml",
        ]
    for name in required:
        if not (active / name).exists():
            hits.append(f"missing Cont {label} artifact: {name}")

    remaining = backlog_remaining()
    baseline = load_json(baseline_path())
    if baseline.get("final_umbrella") is True and remaining > 0:
        hits.append("ACCEPTED_MAIN_BASELINE.final_umbrella=true while digital backlog remains")
    expected_cont = "VIII" if active == CONT_VIII else "VII"
    if baseline.get("continuation") != expected_cont:
        hits.append(f"ACCEPTED_MAIN_BASELINE.continuation must be {expected_cont}")

    drafts = load_yaml(drafts_path())
    if drafts.get("final_umbrella") is True and remaining > 0:
        hits.append("sibling draft registry marks final_umbrella=true while backlog remains")
    if drafts.get("policy") != "DRAFT_TIPS_NOT_ACCEPTED_MAIN_NOT_FINAL_UMBRELLA":
        hits.append("sibling draft registry policy must declare draft tips are not accepted mains")
    if drafts.get("digital_pre_evt_release_ready") is True:
        hits.append("sibling draft registry digital_pre_evt_release_ready=true forbidden")

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
            key.startswith("field_kit_")
            or status
            in {
                "MERGED_TO_MAIN",
                "BRANCHED_FROM_ACCEPTED_MAIN_PENDING_COMMITS",
                "DRAFT_TIP_NOT_ACCEPTED_MAIN",
            }
            or "not accepted main" in note
            or "draft tip not accepted" in note
            or entry.get("base_accepted_main") == sha
        )
        if not allowed:
            hits.append(
                f"draft {key}: tip SHA equals accepted main for {repo} without "
                "MERGED_TO_MAIN / pending-commits / draft-tip marker"
            )

    soft = load_yaml(SOFT)
    if soft.get("final_umbrella") is True and remaining > 0:
        hits.append("software_integration_matrix.final_umbrella=true while backlog remains")
    hw = load_yaml(HW)
    if hw.get("full_complete_claimed") is True:
        hits.append("hardware_release_matrix.full_complete_claimed=true forbidden under Cont VIII")

    check_scorecard_firewall(hits)
    check_gates_firewall(hits)
    check_blockers_firewall(hits)

    pat = re.compile("|".join(f"({p})" for p in FORBIDDEN_RELEASE))
    scorecard = CONT_VIII / "READINESS_SCORECARD.json"
    gates = CONT_VIII / "READINESS_GATES.json"
    for path in (SOFT, HW, MASTER, backlog_path(), baseline_path(), scorecard, gates):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for i, line in enumerate(text.splitlines(), 1):
            if not pat.search(line):
                continue
            if ALLOW.search(line):
                continue
            if remaining > 0 or re.search(r"\bDIGITAL_PRE_EVT_RELEASE_READY\b", line):
                hits.append(
                    f"{path}:{i}: release token asserted while Cont {label} "
                    f"digital backlog={remaining}"
                )

    if hits:
        print("RELEASE_FIREWALL_FAIL")
        for h in hits[:80]:
            print(h)
        return 1
    print("RELEASE_FIREWALL_PASS")
    print(f"digitally_executable_backlog_remaining={remaining}")
    print(f"active_continuation={label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
