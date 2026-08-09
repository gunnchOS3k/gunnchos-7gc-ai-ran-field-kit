#!/usr/bin/env python3
"""Cont IX release firewall — digital release lock / pre-EVT handoff guard.

Extends Cont VIII release firewall:

- DIGITAL_RELEASE_LOCK_COMPLETE / READY_FOR_NPI_* while DIGITAL blockers > 0
- PRODUCTION_READY / MASS_PRODUCTION / CERTIFIED / CARRIER_APPROVED /
  FULL_OPERATIONAL / 6G_CERTIFIED / GATE_8_PASS / EVT_VALIDATED
- Treating Cont IX sibling draft tips as accepted mains
- manufacturer_ready=true without required artifacts (unchanged Cont VIII rule)
- Allow CONDITIONAL_VENDOR_COLLATERAL manufacturer tokens when evidence present
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
CONT_IX = FP / "continuation_ix"
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
    r"\bDIGITAL_RELEASE_LOCK_COMPLETE\b",
    r"\bREADY_FOR_NPI_DFM_AND_EVT_QUOTATION\b",
    r"\bREADY_FOR_NPI\b",
    r"\bPRODUCTION_READY\b",
    r"\bMASS_PRODUCTION\b",
    r"\bCARRIER_APPROVED\b",
    r"\bFULL_OPERATIONAL\b",
    r"\b6G_CERTIFIED\b",
    r"\bGATE_8_PASS\b",
    r"\bEVT_VALIDATED\b",
    r"\bCERTIFIED\b",
]

ALLOW = re.compile(
    r"(?i)(not |never |forbidden|pending|do not|without claiming|must not|reject|"
    r"false|: false|:false|not earned|not claimed|not opened|blocked until|"
    r"draft tip|not accepted|not final umbrella|must remain false|is not claimed|"
    r"forbidden_assertions|forbidden_tokens|forbidden_until|"
    r"explicitly_not_authorized|do not fake|keep .*false)"
)

# CONDITIONAL_VENDOR_COLLATERAL is allowed when evidence enumeration is present.
CONDITIONAL_VENDOR_OK = re.compile(
    r"(?i)CONDITIONAL_VENDOR_COLLATERAL"
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
    if (CONT_IX / "BLOCKER_BURNDOWN.json").exists() or (
        CONT_IX / "ACCEPTED_MAIN_LOCK.json"
    ).exists():
        return CONT_IX
    if (CONT_VIII / "DIGITAL_BACKLOG.json").exists():
        return CONT_VIII
    return CONT_VII


def cont_label(cont: Path) -> str:
    if cont == CONT_IX:
        return "IX"
    if cont == CONT_VIII:
        return "VIII"
    return "VII"


def digital_blocker_remaining() -> int:
    """Cont IX DIGITAL open count, else Cont VIII schema backlog."""
    if active_cont() == CONT_IX:
        burndown = load_json(CONT_IX / "BLOCKER_BURNDOWN.json")
        counts = burndown.get("counts") or {}
        if "DIGITAL_OPEN" in counts:
            return int(counts["DIGITAL_OPEN"] or 0)
        return int(counts.get("DIGITAL") or 0)
    data = load_json(backlog_path())
    return int(
        int(data.get("DIGITALLY_EXECUTABLE_SCHEMA_ONLY") or 0)
        + int(data.get("DIGITALLY_EXECUTABLE_STUB_ONLY") or 0)
        + int(data.get("DIGITALLY_EXECUTABLE_SIMULATION_ONLY") or 0)
        + int(data.get("DIGITALLY_EXECUTABLE_MOCK_ONLY") or 0)
    )


def backlog_path() -> Path:
    cont = active_cont()
    if cont == CONT_IX:
        # Cont IX uses burndown; schema backlog still referenced from VIII.
        return CONT_VIII / "DIGITAL_BACKLOG.json"
    return cont / "DIGITAL_BACKLOG.json"


def baseline_path() -> Path:
    cont = active_cont()
    if cont == CONT_IX:
        return CONT_IX / "ACCEPTED_MAIN_LOCK.json"
    return cont / "ACCEPTED_MAIN_BASELINE.json"


def drafts_path() -> Path:
    cont = active_cont()
    if cont == CONT_IX:
        return CONT_IX / "continuation_ix_sibling_draft_registry.yaml"
    if cont == CONT_VIII:
        return CONT_VIII / "continuation_viii_sibling_draft_registry.yaml"
    return CONT_VII / "continuation_vii_sibling_draft_registry.yaml"


def check_scorecard_firewall(hits: list[str]) -> None:
    # Cont VIII scorecard rules remain when Cont VIII artifacts present.
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
    if active_cont() == CONT_IX:
        burndown = CONT_IX / "BLOCKER_BURNDOWN.json"
        if not burndown.exists():
            hits.append("missing Cont IX BLOCKER_BURNDOWN.json")
            return
        data = load_json(burndown)
        buckets = data.get("buckets") or {}
        allowed = {"DIGITAL", "PHYSICAL", "EXTERNAL"}
        if set(buckets) != allowed:
            hits.append("BLOCKER_BURNDOWN must define exactly DIGITAL|PHYSICAL|EXTERNAL")
        required = {
            "id",
            "product",
            "readiness_gate",
            "bucket",
            "exact_gap",
            "exact_next_action",
            "owner_repo",
            "owner_file",
            "status",
        }
        for b in data.get("blockers") or []:
            missing = required - set(b)
            if missing:
                hits.append(f"blocker {b.get('id')}: missing {sorted(missing)}")
            if b.get("bucket") not in allowed:
                hits.append(f"blocker {b.get('id')}: invalid bucket {b.get('bucket')}")
        if data.get("digital_release_lock_complete") is True and digital_blocker_remaining() > 0:
            hits.append(
                "BLOCKER_BURNDOWN.digital_release_lock_complete=true while DIGITAL blockers remain"
            )
        return

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


def check_cont_ix_lock_firewall(hits: list[str]) -> None:
    if active_cont() != CONT_IX:
        return
    required = [
        "ACCEPTED_MAIN_LOCK.json",
        "READINESS_REPROOF.json",
        "BLOCKER_BURNDOWN.json",
        "PRODUCT_RELEASE_MATRIX.json",
        "PRE_EVT_HANDOFF_MATRIX.json",
        "VENDOR_COLLATERAL_REQUESTS.json",
        "CONTINUATION_IX_REPORT_A_T.md",
        "continuation_ix_sibling_draft_registry.yaml",
    ]
    for name in required:
        if not (CONT_IX / name).exists():
            hits.append(f"missing Cont IX artifact: {name}")

    lock = load_json(CONT_IX / "ACCEPTED_MAIN_LOCK.json")
    remaining = digital_blocker_remaining()
    if lock.get("continuation") != "IX":
        hits.append("ACCEPTED_MAIN_LOCK.continuation must be IX")
    if lock.get("physical_execution_freeze") is not True:
        hits.append("ACCEPTED_MAIN_LOCK.physical_execution_freeze must be true")
    if lock.get("digital_release_lock_complete") is True and remaining > 0:
        hits.append(
            "ACCEPTED_MAIN_LOCK.digital_release_lock_complete=true while DIGITAL blockers remain"
        )
    if lock.get("ready_for_npi_dfm_and_evt_quotation") is True and remaining > 0:
        hits.append(
            "ACCEPTED_MAIN_LOCK.ready_for_npi_dfm_and_evt_quotation=true while DIGITAL blockers remain"
        )
    if lock.get("final_umbrella") is True and remaining > 0:
        hits.append("ACCEPTED_MAIN_LOCK.final_umbrella=true while DIGITAL blockers remain")

    # Final lock may be claimed when DIGITAL_OPEN=0 with CI-proven accepted-main evidence.
    # device-os #69 may remain an open tree-sync follow-up; committed ok:true JSON on
    # device-os main is not required when digital_lock_ci_run evidence is present.
    if lock.get("digital_release_lock_complete") is True and remaining == 0:
        evidence = lock.get("evidence") or {}
        ci = evidence.get("device_os_digital_lock_ci") or {}
        accepted = lock.get("accepted_mains") or {}
        dos = accepted.get("gunnchos-device-os") or {}
        run_id = ci.get("run_id") or dos.get("digital_lock_ci_run")
        ok = ci.get("ok") is True or dos.get("digital_lock_ok") is True
        if not (ok and run_id):
            hits.append(
                "digital_release_lock_complete=true requires evidence.device_os_digital_lock_ci "
                "ok=true and run_id (CI-proven accepted-main path; #69 tree-sync optional)"
            )
        hw = accepted.get("gunnchos-hardware-industrial-design") or {}
        if isinstance(hw, dict) and hw.get("DIGITAL") not in (None, []):
            hits.append(
                "digital_release_lock_complete=true requires hardware accepted_main DIGITAL=[]"
            )

    # CONDITIONAL_VENDOR_COLLATERAL allowed only with evidence enumeration
    vendor = load_json(CONT_IX / "VENDOR_COLLATERAL_REQUESTS.json")
    matrix = load_json(CONT_IX / "PRODUCT_RELEASE_MATRIX.json")
    for prod, entry in (matrix.get("products") or {}).items():
        if not isinstance(entry, dict):
            continue
        token = entry.get("manufacturer_ready_token")
        if token == "CONDITIONAL_VENDOR_COLLATERAL":
            if entry.get("manufacturer_ready") is True:
                hits.append(
                    f"PRODUCT_RELEASE_MATRIX.{prod}: manufacturer_ready=true with only "
                    "CONDITIONAL_VENDOR_COLLATERAL (must stay false until unconditional pack)"
                )
            if not vendor.get("requests"):
                hits.append(
                    f"PRODUCT_RELEASE_MATRIX.{prod}: CONDITIONAL_VENDOR_COLLATERAL without "
                    "VENDOR_COLLATERAL_REQUESTS evidence"
                )


def line_allows_forbidden(line: str, prev_lines: list[str] | None = None) -> bool:
    if ALLOW.search(line):
        return True
    # Explicit false assignments of lock tokens are OK
    if re.search(
        r"(?i)(digital_release_lock_complete|ready_for_npi|digital_pre_evt_release_ready|"
        r"final_umbrella)\s*[:=]\s*false",
        line,
    ):
        return True
    # Listing as forbidden token / assertion is OK
    if re.search(
        r"(?i)(forbidden|must not|do not claim|never claim|not claimed|"
        r"never claim EVT|do not fake)",
        line,
    ):
        return True
    # JSON/YAML array members under forbidden_* keys (token inventory, not assertion)
    stripped = line.strip().strip(",").strip('"').strip("'")
    if re.fullmatch(
        r"(PRODUCTION_READY|MASS_PRODUCTION|CERTIFIED|CARRIER_APPROVED|"
        r"FULL_OPERATIONAL|6G_CERTIFIED|GATE_8_PASS|EVT_VALIDATED|"
        r"DIGITAL_RELEASE_LOCK_COMPLETE(=true)?|"
        r"READY_FOR_NPI_DFM_AND_EVT_QUOTATION(=true)?|"
        r"READY_FOR_NPI|DIGITAL_PRE_EVT_RELEASE_READY|"
        r"PRE_MANUFACTURING_RELEASE_COMPLETE|DIGITAL_RELEASE_TOTALITY|"
        r"FULL_PRODUCT_DIGITAL_TOTALITY|TRUE_FINAL_UMBRELLA_OPEN|"
        r"MANUFACTURING_ORDER_AUTHORIZED)",
        stripped,
    ):
        ctx = "\n".join((prev_lines or [])[-40:])
        if re.search(
            r"(?i)(forbidden_assertions|forbidden_tokens|forbidden_until|"
            r"explicitly_not_authorized|forbidden_claims)",
            ctx,
        ):
            return True
    # Narrative references that are not true-assertions
    if re.search(
        r"(?i)(before|until|without|not |never ).{0,40}"
        r"(DIGITAL_RELEASE_LOCK_COMPLETE|READY_FOR_NPI|EVT_VALIDATED|PRODUCTION_READY)",
        line,
    ):
        return True
    return False


def main() -> int:
    hits: list[str] = []
    active = active_cont()
    label = cont_label(active)
    if not active.exists():
        print("RELEASE_FIREWALL_FAIL")
        print("missing program/full_product/continuation_ix/ (and no Cont VIII/VII fallback)")
        return 1

    if active == CONT_IX:
        check_cont_ix_lock_firewall(hits)
        # Cont VIII artifacts still required as prior baseline
        for name in (
            "DIGITAL_BACKLOG.json",
            "REQUIREMENT_COUNTS.json",
            "READINESS_SCORECARD.json",
        ):
            if not (CONT_VIII / name).exists():
                hits.append(f"missing Cont VIII baseline artifact for Cont IX: {name}")
    else:
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

    remaining = digital_blocker_remaining()
    baseline = load_json(baseline_path())
    if baseline.get("final_umbrella") is True and remaining > 0:
        hits.append(f"{baseline_path().name}.final_umbrella=true while digital blockers remain")
    expected_cont = label
    if baseline.get("continuation") != expected_cont and active != CONT_IX:
        hits.append(f"baseline.continuation must be {expected_cont}")
    if active == CONT_IX and baseline.get("continuation") != "IX":
        hits.append("ACCEPTED_MAIN_LOCK.continuation must be IX")

    drafts = load_yaml(drafts_path())
    if drafts.get("final_umbrella") is True and remaining > 0:
        hits.append("sibling draft registry marks final_umbrella=true while blockers remain")
    if drafts.get("policy") != "DRAFT_TIPS_NOT_ACCEPTED_MAIN_NOT_FINAL_UMBRELLA":
        hits.append("sibling draft registry policy must declare draft tips are not accepted mains")
    if drafts.get("digital_pre_evt_release_ready") is True:
        hits.append("sibling draft registry digital_pre_evt_release_ready=true forbidden")
    if drafts.get("digital_release_lock_complete") is True and remaining > 0:
        hits.append("sibling draft registry digital_release_lock_complete=true while DIGITAL remain")

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
                "PENDING_OPEN",
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
        hits.append("software_integration_matrix.final_umbrella=true while blockers remain")
    if soft.get("digital_release_lock_complete") is True and remaining > 0:
        hits.append(
            "software_integration_matrix.digital_release_lock_complete=true while DIGITAL remain"
        )
    hw = load_yaml(HW)
    if hw.get("full_complete_claimed") is True:
        hits.append("hardware_release_matrix.full_complete_claimed=true forbidden under Cont IX")

    check_scorecard_firewall(hits)
    check_gates_firewall(hits)
    check_blockers_firewall(hits)

    pat = re.compile("|".join(f"({p})" for p in FORBIDDEN_RELEASE))
    scan_paths = [
        SOFT,
        HW,
        MASTER,
        backlog_path(),
        baseline_path(),
        CONT_VIII / "READINESS_SCORECARD.json",
        CONT_VIII / "READINESS_GATES.json",
    ]
    if active == CONT_IX:
        scan_paths += [
            CONT_IX / "ACCEPTED_MAIN_LOCK.json",
            CONT_IX / "READINESS_REPROOF.json",
            CONT_IX / "BLOCKER_BURNDOWN.json",
            CONT_IX / "PRODUCT_RELEASE_MATRIX.json",
            CONT_IX / "PRE_EVT_HANDOFF_MATRIX.json",
            CONT_IX / "VENDOR_COLLATERAL_REQUESTS.json",
            CONT_IX / "CONTINUATION_IX_REPORT_A_T.md",
        ]
    for path in scan_paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            if not pat.search(line):
                continue
            if line_allows_forbidden(line, lines[: i - 1]):
                continue
            # CONDITIONAL_VENDOR_COLLATERAL mentions are allowed with evidence
            if CONDITIONAL_VENDOR_OK.search(line) and "CONDITIONAL" in line:
                continue
            # When DIGITAL blockers remain: any forbidden token is a hit.
            # When DIGITAL_OPEN=0: DIGITAL_RELEASE_LOCK_COMPLETE / READY_FOR_NPI*=true
            # are allowed; PRODUCTION_READY / EVT / GATE_8 / CERTIFIED* stay forbidden.
            lock_claim_ok = remaining == 0 and bool(
                re.search(
                    r"(?i)(DIGITAL_RELEASE_LOCK_COMPLETE|READY_FOR_NPI_DFM_AND_EVT_QUOTATION|"
                    r"READY_FOR_NPI)\s*[:=]\s*true",
                    line,
                )
            )
            always_forbidden_true = bool(
                re.search(
                    r"(?i)(PRODUCTION_READY|MASS_PRODUCTION|EVT_VALIDATED|GATE_8_PASS|"
                    r"6G_CERTIFIED|CARRIER_APPROVED|FULL_OPERATIONAL|(?<![A-Z_])CERTIFIED|"
                    r"DIGITAL_PRE_EVT_RELEASE_READY)\s*[:=]\s*true",
                    line,
                )
            )
            if lock_claim_ok and not always_forbidden_true:
                continue
            if remaining > 0 or always_forbidden_true or re.search(
                r"(?i)(DIGITAL_RELEASE_LOCK_COMPLETE|READY_FOR_NPI|PRODUCTION_READY|"
                r"MASS_PRODUCTION|EVT_VALIDATED|GATE_8_PASS|6G_CERTIFIED|"
                r"CARRIER_APPROVED|FULL_OPERATIONAL|CERTIFIED|"
                r"DIGITAL_PRE_EVT_RELEASE_READY)\s*[:=]\s*true",
                line,
            ):
                snippet = line.strip()[:120]
                hits.append(
                    f"{path}:{i}: forbidden release token asserted while Cont {label} "
                    f"digital_blockers={remaining}: {snippet}"
                )

    if hits:
        print("RELEASE_FIREWALL_FAIL")
        for h in hits[:80]:
            print(h)
        return 1
    print("RELEASE_FIREWALL_PASS")
    print(f"digital_blockers_remaining={remaining}")
    print(f"active_continuation={label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
