#!/usr/bin/env python3
"""Phase X/XIV RFQ package digital validator.

Re-proves draft RFQ packages under npi/*/rfq/ and shared PRE-EVT collateral.
Does not send RFQs, purchase, fab, or accept NDAs.

Exit 0 when RFQ_PACKAGE_DIGITAL_DEFECTS == 0.
Writes program/pre_evt/RFQ_PACKAGE_VALIDATION.json and refreshes
PHASE_X_RECOMMENDATION.json tokens (READY_TO_SEND_RFQS vs RFQ_PACKAGE_BLOCKED).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRE_EVT = ROOT / "program" / "pre_evt"
PRODUCTS = [
    "student_14_5",
    "ds_xl_coder",
    "handheld_hybrid",
    "edge_io_rings",
    "first_party_dock",
]
RFQ_LOCAL = [
    "RFQ_COVER_LETTER.md",
    "RFQ_PACKAGE_MANIFEST.json",
    "RFQ_QUESTIONNAIRE.md",
]
PRODUCT_PLAN_FILES = [
    "evt/EVT_PHYSICAL_TEST_BOOK.md",
    "evt/EVT_ACCEPTANCE_MATRIX.md",
    "factory_test/FIXTURE_PLAN.json",
    "dfm/DFM_REVIEW_QUESTIONS.md",
    "dfm/DFM_PRECHECK.md",
    "risk/RISK_REGISTER.json",
    "bom/QUOTE_READY_BOM.csv",
    "bom/SUPPLY_RISK_MATRIX.json",
]
SHARED_REQUIRED = [
    "shared/VENDOR_COLLATERAL_MATRIX.json",
    "shared/PUBLIC_VENDOR_COLLATERAL_INTEGRATED.json",
    "shared/NPI_MANUFACTURER_SHORTLIST.json",
    "shared/EVT_QUANTITY_SCENARIOS.json",
    "shared/QUOTE_COMPARISON_TEMPLATE.md",
    "shared/QUOTE_COMPARISON_WORKBOOK.csv",
    "shared/PROTOTYPE_COST_MODEL_RANGES.json",
    "shared/MANUFACTURER_SELECTION_RUBRIC.md",
    "shared/COMPLIANCE_CARRIER_PRESCAN_PLAN.json",
]
EDMUND_PACKETS = [
    "edmund_packets/A01_ADLINK_COMHPC_REQUEST.md",
    "edmund_packets/A02_INTEL_DOCK_JHL_REQUEST.md",
    "edmund_packets/A03_PANEL_TOUCH_HINGE_INQUIRY.md",
    "edmund_packets/A04_BATTERY_INQUIRY.md",
    "edmund_packets/A05_ANTENNA_RF_INQUIRY.md",
    "edmund_packets/A06_MANUFACTURER_SHORTLIST_SELECTION.md",
    "edmund_packets/A07_RFQ_SEND_APPROVALS.md",
    "edmund_packets/EDMUND_ACTION_INDEX.json",
]
FORBIDDEN_SEND_TOKENS = (
    "READY_TO_PURCHASE",
    "PURCHASE_AUTHORIZED=true",
    "RFQ_EXTERNAL_SEND_AUTHORIZATION=true",
    "RFQ_SENT",
    "PURCHASED",
    "FABRICATING",
)
# Accepted hardware tip (Phase XV #53). Cont IX manufacturing lock remains #52;
# gerber byte hashes are identical at tip (verified WP-004).
ACCEPTED_HARDWARE_TIP = "8705f5a25065e02c7513e990a43e4762967906c5"
CONT_IX_MANUFACTURING_LOCK = "cd1d906c5f08eb26c350851a4faeb05e2bf2e79f"
HANDHELD_STORAGE_DEFECT = "NPI_DEFECT-HANDHELD-STORAGE-HEADROOM-001"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_file(rel: str, defects: list[str], prefix: str = "") -> None:
    path = ROOT / rel
    if not path.is_file():
        defects.append(f"{prefix}missing_file:{rel}")


def validate_product(product: str, defects: list[str]) -> None:
    rfq_dir = ROOT / "npi" / product / "rfq"
    for name in RFQ_LOCAL:
        check_file(f"npi/{product}/rfq/{name}", defects, prefix=f"{product}:")

    man_path = rfq_dir / "RFQ_PACKAGE_MANIFEST.json"
    if not man_path.is_file():
        return
    try:
        man = json.loads(man_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        defects.append(f"{product}:manifest_json_invalid:{exc}")
        return

    if man.get("product") != product:
        defects.append(f"{product}:manifest_product_mismatch:{man.get('product')}")
    if man.get("do_not_send") is not True:
        defects.append(f"{product}:do_not_send_must_be_true")
    if man.get("autoMergeRequest") not in (None,):
        defects.append(f"{product}:autoMergeRequest_must_be_null")
    missing = man.get("missing") or []
    if missing:
        defects.append(f"{product}:manifest_missing_entries:{missing}")

    for label, rel in (man.get("files") or {}).items():
        if not (ROOT / rel).is_file():
            defects.append(f"{product}:manifest_file_absent:{label}:{rel}")

    rel_man_path = ROOT / "npi" / product / "release_manifest" / "RELEASE_MANIFEST.json"
    if rel_man_path.is_file():
        try:
            rel_man = json.loads(rel_man_path.read_text(encoding="utf-8"))
            tip = rel_man.get("accepted_hardware_sha")
            if tip != ACCEPTED_HARDWARE_TIP:
                defects.append(
                    f"{product}:stale_accepted_hardware_sha:{tip}"
                )
            pcb_path = ROOT / "npi" / product / "pcb" / "PCB_PACKAGE_INDEX.json"
            if pcb_path.is_file():
                pcb = json.loads(pcb_path.read_text(encoding="utf-8"))
                if pcb.get("hardware_sha") != ACCEPTED_HARDWARE_TIP:
                    defects.append(
                        f"{product}:pcb_index_stale_hardware_sha:{pcb.get('hardware_sha')}"
                    )
        except json.JSONDecodeError as exc:
            defects.append(f"{product}:release_manifest_json_invalid:{exc}")

    cover = (rfq_dir / "RFQ_COVER_LETTER.md").read_text(encoding="utf-8")
    if "DO NOT SEND" not in cover.upper() and "DRAFT" not in cover.upper():
        defects.append(f"{product}:cover_missing_do_not_send_or_draft")
    if "CONFIDENTIAL" not in cover.upper():
        defects.append(f"{product}:cover_missing_confidential_marking")
    if ACCEPTED_HARDWARE_TIP not in cover:
        defects.append(f"{product}:cover_missing_accepted_hardware_tip_sha")
    for tok in FORBIDDEN_SEND_TOKENS:
        if tok in cover:
            defects.append(f"{product}:forbidden_token_in_cover:{tok}")

    if product == "handheld_hybrid":
        if HANDHELD_STORAGE_DEFECT not in cover:
            defects.append(
                f"{product}:cover_missing_open_npi_defect_disclosure:{HANDHELD_STORAGE_DEFECT}"
            )
        risk_path = ROOT / "npi" / product / "risk" / "RISK_REGISTER.json"
        if risk_path.is_file():
            try:
                risk = json.loads(risk_path.read_text(encoding="utf-8"))
                titles = " ".join(
                    str(r.get("title", "")) + str(r.get("npi_defect", ""))
                    for r in (risk.get("risks") or [])
                )
                if HANDHELD_STORAGE_DEFECT not in titles:
                    defects.append(
                        f"{product}:risk_register_missing:{HANDHELD_STORAGE_DEFECT}"
                    )
            except json.JSONDecodeError as exc:
                defects.append(f"{product}:risk_register_json_invalid:{exc}")

    for rel in PRODUCT_PLAN_FILES:
        check_file(f"npi/{product}/{rel}", defects, prefix=f"{product}:")


def main() -> int:
    defects: list[str] = []
    generator_defects: list[str] = []

    for product in PRODUCTS:
        validate_product(product, defects)

    for rel in SHARED_REQUIRED + EDMUND_PACKETS:
        check_file(f"program/pre_evt/{rel}", defects)

    index_path = PRE_EVT / "edmund_packets" / "EDMUND_ACTION_INDEX.json"
    if index_path.is_file():
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
            expected = [f"A0{i}" for i in range(1, 8)]
            packets = index.get("packets") or []
            if packets != expected:
                defects.append(f"edmund_index_packets_mismatch:{packets}")
            if index.get("do_not_send_from_cursor") is not True:
                defects.append("edmund_index_do_not_send_from_cursor_must_be_true")
        except json.JSONDecodeError as exc:
            defects.append(f"edmund_index_json_invalid:{exc}")

    vendor_ok = (PRE_EVT / "shared" / "VENDOR_COLLATERAL_MATRIX.json").is_file()
    shortlist_ok = (PRE_EVT / "shared" / "NPI_MANUFACTURER_SHORTLIST.json").is_file()
    evt_ok = all(
        (ROOT / "npi" / p / "evt" / "EVT_PHYSICAL_TEST_BOOK.md").is_file() for p in PRODUCTS
    )
    quote_ok = all(
        (PRE_EVT / "shared" / name).is_file()
        for name in (
            "QUOTE_COMPARISON_TEMPLATE.md",
            "QUOTE_COMPARISON_WORKBOOK.csv",
            "MANUFACTURER_SELECTION_RUBRIC.md",
        )
    )

    now = utc_now()
    defect_count = len(defects)
    ready = defect_count == 0
    # READY_TO_SEND_RFQS = digital package coherent for Edmund send-review path.
    # Does NOT authorize external send. READY_FOR_EDMUND_RFQ_SEND_REVIEW is the
    # Cycle-1 review token; RFQ_SENT remains forbidden until human A07.
    recommendation = "READY_TO_SEND_RFQS" if ready else "RFQ_PACKAGE_BLOCKED"
    edmund_review_ready = ready

    validation = {
        "generated_at_utc": now,
        "RFQ_PACKAGE_DIGITAL_DEFECTS": defect_count,
        "defects": defects,
        "generator_defects": generator_defects,
        "products_validated": PRODUCTS,
        "accepted_hardware_tip": ACCEPTED_HARDWARE_TIP,
        "cont_ix_manufacturing_lock": CONT_IX_MANUFACTURING_LOCK,
        "VENDOR_COLLATERAL_REQUESTS_COMPLETE": vendor_ok,
        "NPI_SHORTLIST_COMPLETE": shortlist_ok,
        "EVT_PLAN_COMPLETE": evt_ok,
        "QUOTE_COMPARISON_SYSTEM_COMPLETE": quote_ok,
        "READY_TO_SEND_RFQS": ready,
        "READY_FOR_EDMUND_RFQ_SEND_REVIEW": edmund_review_ready,
        "RFQ_SENT": False,
        "rfq_external_send_authorization": False,
        "purchase_authorized": False,
        "PHYSICAL_EXECUTION_FREEZE": "ACTIVE",
        "validator": "scripts/validate_rfq_packages.py",
    }
    (PRE_EVT / "RFQ_PACKAGE_VALIDATION.json").write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8"
    )

    rec_path = PRE_EVT / "PHASE_X_RECOMMENDATION.json"
    rec = {}
    if rec_path.is_file():
        try:
            rec = json.loads(rec_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            generator_defects.append("PHASE_X_RECOMMENDATION.json_invalid")
    rec.update(
        {
            "generated_at_utc": now,
            "recommendation": recommendation,
            "RFQ_PACKAGE_DIGITAL_DEFECTS": defect_count,
            "READY_TO_SEND_RFQS": ready,
            "READY_FOR_EDMUND_RFQ_SEND_REVIEW": edmund_review_ready,
            "RFQ_SENT": False,
            "purchase_authorized": False,
            "rfq_external_send_authorization": False,
            "phase_xiv_reproof": True,
            "wp004_reproof": True,
            "accepted_hardware_tip": ACCEPTED_HARDWARE_TIP,
        }
    )
    # Never claim purchase readiness or external send
    if rec.get("recommendation") in ("READY_TO_PURCHASE", "RFQ_SENT"):
        rec["recommendation"] = "RFQ_PACKAGE_BLOCKED"
        generator_defects.append("stripped_forbidden_send_or_purchase_token")
    rec_path.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")

    print(f"RFQ_PACKAGE_DIGITAL_DEFECTS={defect_count}")
    print(f"READY_TO_SEND_RFQS={str(ready).upper()}")
    print(f"READY_FOR_EDMUND_RFQ_SEND_REVIEW={str(edmund_review_ready).upper()}")
    print(f"RFQ_SENT=FALSE")
    print(f"recommendation={recommendation}")
    for d in defects:
        print(f"DEFECT {d}")
    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())
