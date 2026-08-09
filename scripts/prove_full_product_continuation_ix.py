#!/usr/bin/env python3
"""Continuation IX: Final Digital Release Lock + Pre-EVT handoff evidence.

Extends Cont VIII release-readiness control plane. PHYSICAL_EXECUTION_FREEZE
remains active. Does NOT claim DIGITAL_RELEASE_LOCK_COMPLETE or
READY_FOR_NPI_DFM_AND_EVT_QUOTATION while DIGITAL blockers remain > 0 on
accepted mains (hardware packaging + OS prove-gaps pending Cont IX sibling
merges).

Cursor NEVER merges. Draft PR only.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
FP = ROOT / "program" / "full_product"
REPORTS = FP / "reports"
CONT_VIII = FP / "continuation_viii"
CONT_IX = FP / "continuation_ix"

# Cont VIII accepted mains after Edmund merges (#41 field-kit, #51 HW, #67 OS).
ACCEPTED: dict[str, dict[str, Any]] = {
    "gunnchos-7gc-ai-ran-field-kit": {
        "sha": "7c6b955be933e050f81358f25077866f37a493bd",
        "merged_prs": [40, 41],
        "ci": "green",
        "note": "Cont VIII #41 release-readiness closure on main; Cont IX lock base",
    },
    "gunnchos-hardware-industrial-design": {
        "sha": "a710f35559252f36f0e6af7e025a5958df0906e3",
        "merged_prs": [50, 51],
        "ci": "green",
        "note": "#51 Cont VIII manufacturer packages on main; DIGITAL residual (proxy/Radxa/silk)",
        "token": "HARDWARE_DESIGN_RELEASE_CANDIDATE",
        "manufacturer_ready": "CONDITIONAL_VENDOR_COLLATERAL",
    },
    "edge-io-measurement-node": {
        "sha": "a1cd2e95c62eb0eefd507b976158232b83f5b33b",
        "merged_prs": [35],
        "ci": "green",
        "note": "#35 Cont VIII ring E2E digital on main; physical boot still pending",
        "token": "RING_END_TO_END_DIGITAL_INPUT_PASS",
    },
    "gunnchos-device-os": {
        "sha": "06366da047a6938646acb01e016d19318fabab70",
        "merged_prs": [65, 66, 67],
        "ci": "gate1_may_be_red_at_cont_ix_kickoff",
        "note": (
            "#67 Cont VIII release-readiness OS on main; Gate 1 may be red at kickoff; "
            "Cont IX OS PR must prove clean env (manifest-only productivity until then)"
        ),
        "token": "GUNNCHOS_BOOTABLE_REFERENCE_IMAGE_DIGITAL_PASS",
    },
    "gunnchAI3k": {
        "sha": "91a9f135b6423a7627ed61946b16e9ab9d79de6e",
        "merged_prs": [26],
        "ci": "green",
        "note": "#26 Cont VIII platform complete on main",
        "token": "GUNNCHAI_REAL_LOCAL_INFERENCE_PASS",
    },
    "anime-aggressors": {
        "sha": "249270383eab87cf4d1240ea17e66bfff44d4b8c",
        "merged_prs": [70],
        "ci": "green",
        "note": "#70 Path A audit + RC hardening on main",
    },
    "pedestrian-pursuit": {
        "sha": "a2c6da5b4d4635af1281dbb12b8564ba70f994c6",
        "merged_prs": [12],
        "ci": "green",
        "note": "#12 digital RC art/audio on main; physical FPS separate",
    },
    "archive-of-life-artifact-world": {
        "sha": "948ca172bb77b4caf1bd3c2d809d74ee6d4b6c75",
        "merged_prs": [25],
        "ci": "green",
        "note": "#25 Cont VIII release integrity on main",
    },
    "beatlink-party": {
        "sha": "e0c18f3dbb964608271c14611e1068cff9c17205",
        "merged_prs": [16],
        "ci": "green",
        "note": "#16 Cont VIII gunnchOS packaging on main",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def dump_json(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def dump_yaml(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(obj, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def git_tip() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return None


def digital_blockers() -> list[dict[str, Any]]:
    """Seed DIGITAL residuals from Cont VIII hardware truth + OS prove-gaps."""
    return [
        {
            "id": "IX-D-001",
            "product": "all_boards",
            "readiness_gate": "R1_DIGITAL_PACKAGING",
            "bucket": "DIGITAL",
            "exact_gap": "JEDEC/vendor production footprints still proxy packages on accepted hardware main",
            "exact_next_action": "Replace proxy footprints with production JEDEC/vendor packages on Cont IX hardware tip",
            "owner_repo": "gunnchos-hardware-industrial-design",
            "owner_file": "eda/footprints/PROXY_* (Cont VIII #51 residual)",
            "status": "OPEN",
        },
        {
            "id": "IX-D-002",
            "product": "handheld_hybrid",
            "readiness_gate": "R1_DIGITAL_PACKAGING",
            "bucket": "DIGITAL",
            "exact_gap": "Radxa NX5 260-pin hierarchical sheets incomplete on accepted hardware main",
            "exact_next_action": "Finish public pin expansion sheets on Cont IX hardware tip",
            "owner_repo": "gunnchos-hardware-industrial-design",
            "owner_file": "eda/handheld/radxa_nx5_260pin/",
            "status": "OPEN",
        },
        {
            "id": "IX-D-003",
            "product": "all_boards",
            "readiness_gate": "R1_DIGITAL_PACKAGING",
            "bucket": "DIGITAL",
            "exact_gap": "AVL connector silkscreen/courtyard polish incomplete pending MPN freeze",
            "exact_next_action": "Apply silkscreen/courtyard polish after MPN freeze on Cont IX hardware tip",
            "owner_repo": "gunnchos-hardware-industrial-design",
            "owner_file": "eda/*/silkscreen_courtyard_polish.md",
            "status": "OPEN",
        },
        {
            "id": "IX-D-004",
            "product": "gunnchOS",
            "readiness_gate": "R1_OS_PROVE",
            "bucket": "DIGITAL",
            "exact_gap": (
                "Productivity/SDK paths remain manifest-only until Cont IX OS proves clean env; "
                "Gate 1 may be red at Cont VIII #67 kickoff"
            ),
            "exact_next_action": "Open Cont IX device-os prove PR; clear Gate 1 / clean-env proof before DIGITAL lock",
            "owner_repo": "gunnchos-device-os",
            "owner_file": "program/release/PRODUCTIVITY_MANIFEST.yaml",
            "status": "OPEN",
        },
    ]


def physical_blockers() -> list[dict[str, Any]]:
    return [
        {
            "id": "IX-P-001",
            "product": "all",
            "readiness_gate": "R4_PHYSICAL_HONESTY",
            "bucket": "PHYSICAL",
            "exact_gap": "PHYSICAL_EXECUTION_FREEZE active — no fab/assembly/test execution",
            "exact_next_action": "Edmund freeze lift + purchase authority before any EVT build",
            "owner_repo": "gunnchos-7gc-ai-ran-field-kit",
            "owner_file": "program/full_product/continuation_ix/PRE_EVT_HANDOFF_MATRIX.json",
            "status": "OPEN_IRREDUCIBLE",
        },
        {
            "id": "IX-P-002",
            "product": "all_devices",
            "readiness_gate": "R4_PHYSICAL_HONESTY",
            "bucket": "PHYSICAL",
            "exact_gap": "EVT measurements (battery/thermal/dock/ring/boot) not executable under freeze",
            "exact_next_action": "After freeze lift: run EVT measurement pack; do not claim EVT_VALIDATED until measured",
            "owner_repo": "gunnchos-hardware-industrial-design",
            "owner_file": "program/evt/MEASUREMENT_PLAN.md",
            "status": "OPEN_IRREDUCIBLE",
        },
    ]


def external_blockers() -> list[dict[str, Any]]:
    return [
        {
            "id": "IX-E-001",
            "product": "student_dsxl",
            "readiness_gate": "R5_EXTERNAL_HONESTY",
            "bucket": "EXTERNAL",
            "exact_gap": "ADLINK/PICMG COM-HPC Mini 400-pin map under NDA (Option B)",
            "exact_next_action": "Obtain COM-HPC NDA collateral or revisit Option C",
            "owner_repo": "gunnchos-hardware-industrial-design",
            "owner_file": "program/vendor/COM_HPC_NDA_REQUEST.md",
            "status": "OPEN_IRREDUCIBLE",
        },
        {
            "id": "IX-E-002",
            "product": "ds_xl",
            "readiness_gate": "R5_EXTERNAL_HONESTY",
            "bucket": "EXTERNAL",
            "exact_gap": "Dual eDP panel interconnect map not finalized without OEM AVL",
            "exact_next_action": "Request dual eDP pin/timing collateral from panel OEM",
            "owner_repo": "gunnchos-hardware-industrial-design",
            "owner_file": "program/vendor/DUAL_EDP_PANEL_REQUEST.md",
            "status": "OPEN_IRREDUCIBLE",
        },
        {
            "id": "IX-E-003",
            "product": "dock",
            "readiness_gate": "R5_EXTERNAL_HONESTY",
            "bucket": "EXTERNAL",
            "exact_gap": "Intel JHL8440/JHL9040R ball maps blocked without Intel docs/NDA",
            "exact_next_action": "Request Intel ball-map collateral under appropriate NDA",
            "owner_repo": "gunnchos-hardware-industrial-design",
            "owner_file": "program/vendor/INTEL_JHL_BALLMAP_REQUEST.md",
            "status": "OPEN_IRREDUCIBLE",
        },
        {
            "id": "IX-E-004",
            "product": "ds_xl",
            "readiness_gate": "R5_EXTERNAL_HONESTY",
            "bucket": "EXTERNAL",
            "exact_gap": "Panel/hinge OEM AVL + bend specs incomplete",
            "exact_next_action": "Issue panel/hinge OEM AVL RFQ; capture bend/life specs",
            "owner_repo": "gunnchos-hardware-industrial-design",
            "owner_file": "program/vendor/PANEL_HINGE_OEM_REQUEST.md",
            "status": "OPEN_IRREDUCIBLE",
        },
        {
            "id": "IX-E-005",
            "product": "all_devices",
            "readiness_gate": "R5_EXTERNAL_HONESTY",
            "bucket": "EXTERNAL",
            "exact_gap": "Some assembly torque values require OEM fastener/spec sheets",
            "exact_next_action": "Collect OEM torque tables into vendor collateral pack",
            "owner_repo": "gunnchos-hardware-industrial-design",
            "owner_file": "program/vendor/TORQUE_OEM_REQUEST.md",
            "status": "OPEN_IRREDUCIBLE",
        },
    ]


def write_accepted_main_lock(now: str) -> dict[str, Any]:
    doc = {
        "schema_version": "1.0.0",
        "continuation": "IX",
        "wave": "CONTINUATION_IX_DIGITAL_RELEASE_LOCK",
        "generated_at_utc": now,
        "physical_execution_freeze": True,
        "accepted_main_policy": "MERGED_on_main_SHA_only_no_cursor_branch_as_accepted",
        "cont_viii_accepted_field_kit_main": "7c6b955be933e050f81358f25077866f37a493bd",
        "immutable_note": (
            "Cont IX locks Cont VIII accepted sibling mains after #41/#51/#67 merges. "
            "Draft tips are NOT accepted mains. DIGITAL_RELEASE_LOCK_COMPLETE stays false "
            "until DIGITAL blockers=0 on accepted mains after Cont IX sibling merges."
        ),
        "repos": {
            name: {
                "origin_main": meta["sha"],
                "accepted_main_sha": meta["sha"],
                "merged_prs": meta.get("merged_prs", []),
                "ci": meta.get("ci"),
                "note": meta.get("note"),
                **({"token": meta["token"]} if meta.get("token") else {}),
                **(
                    {"manufacturer_ready": meta["manufacturer_ready"]}
                    if meta.get("manufacturer_ready")
                    else {}
                ),
            }
            for name, meta in ACCEPTED.items()
        },
        "accepted_mains": {k: v["sha"] for k, v in ACCEPTED.items()},
        "digital_release_lock_complete": False,
        "ready_for_npi_dfm_and_evt_quotation": False,
        "final_umbrella": False,
        "recommendation": "CONTINUE_DIGITAL_RELEASE_ENGINEERING",
        "pending_edmund_merges": [
            "continuation-ix field-kit DRAFT (this PR)",
            "continuation-ix hardware DIGITAL packaging tip (proxy/Radxa/silk)",
            "continuation-ix device-os clean-env prove tip (Gate 1)",
        ],
    }
    dump_json(doc, CONT_IX / "ACCEPTED_MAIN_LOCK.json")
    return doc


def write_readiness_reproof(now: str) -> dict[str, Any]:
    viii_counts = load_json(CONT_VIII / "REQUIREMENT_COUNTS.json")
    viii_backlog = load_json(CONT_VIII / "DIGITAL_BACKLOG.json")
    dig = digital_blockers()
    doc = {
        "schema_version": "1.0.0",
        "continuation": "IX",
        "generated_at_utc": now,
        "physical_execution_freeze": True,
        "policy": "REPROOF_CONT_VIII_COUNTS_PLUS_CONT_IX_DIGITAL_PACKAGING_RESIDUAL",
        "cont_viii_requirement_counts_reference": {
            "total": viii_counts.get("total"),
            "status_counts": viii_counts.get("status_counts"),
            "SCHEMA_ONLY": (viii_counts.get("status_counts") or {}).get("SCHEMA_ONLY", 0),
            "PHYSICAL_REQUIRED": (viii_counts.get("status_counts") or {}).get(
                "PHYSICAL_REQUIRED", 0
            ),
            "EXTERNAL_REQUIRED": (viii_counts.get("status_counts") or {}).get(
                "EXTERNAL_REQUIRED", 0
            ),
        },
        "cont_viii_digitally_executable_schema_backlog": {
            "DIGITALLY_EXECUTABLE_SCHEMA_ONLY": viii_backlog.get(
                "DIGITALLY_EXECUTABLE_SCHEMA_ONLY", 0
            ),
            "DIGITALLY_EXECUTABLE_STUB_ONLY": viii_backlog.get(
                "DIGITALLY_EXECUTABLE_STUB_ONLY", 0
            ),
            "DIGITALLY_EXECUTABLE_MOCK_ONLY": viii_backlog.get(
                "DIGITALLY_EXECUTABLE_MOCK_ONLY", 0
            ),
            "note": "Cont VIII requirement-graph SCHEMA backlog remains 0; Cont IX DIGITAL residual is packaging/OS prove",
        },
        "cont_ix_digital_packaging_residual_count": len(dig),
        "cont_ix_digital_blocker_ids": [b["id"] for b in dig],
        "gates_reproof": {
            "R1_requirement_schema_backlog": "PASS_SCHEMA_ZERO_CONT_VIII",
            "R1_digital_packaging_lock": "FAIL_OPEN_BLOCKERS",
            "R3_release_firewall": "REQUIRED_PASS",
            "R4_physical_freeze": "PASS_FREEZE_ACTIVE",
            "R5_external_honesty": "PASS_EXTERNAL_IRREDUCIBLE",
        },
        "digital_release_lock_complete": False,
        "forbidden_assertions": [
            "PRODUCTION_READY",
            "MASS_PRODUCTION",
            "CERTIFIED",
            "CARRIER_APPROVED",
            "FULL_OPERATIONAL",
            "6G_CERTIFIED",
            "GATE_8_PASS",
            "EVT_VALIDATED",
            "DIGITAL_RELEASE_LOCK_COMPLETE=true",
            "READY_FOR_NPI_DFM_AND_EVT_QUOTATION=true",
        ],
        "allowed_conditional_tokens": [
            "CONDITIONAL_VENDOR_COLLATERAL",
        ],
        "notes": (
            "Honest Cont IX reproof: Cont VIII SCHEMA backlog=0 on accepted mains, but "
            "DIGITAL packaging/OS prove blockers keep digital_release_lock_complete=false "
            "until Cont IX sibling tips merge and DIGITAL=0."
        ),
    }
    dump_json(doc, CONT_IX / "READINESS_REPROOF.json")
    return doc


def write_blocker_burndown(now: str) -> dict[str, Any]:
    dig = digital_blockers()
    phys = physical_blockers()
    ext = external_blockers()
    blockers = dig + phys + ext
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
    for b in blockers:
        missing = required - set(b)
        if missing:
            raise SystemExit(f"blocker {b.get('id')} missing fields: {sorted(missing)}")
        if b["bucket"] not in {"DIGITAL", "PHYSICAL", "EXTERNAL"}:
            raise SystemExit(f"blocker {b['id']} invalid bucket {b['bucket']}")

    digital_open = sum(1 for b in dig if str(b["status"]).startswith("OPEN"))
    doc = {
        "schema_version": "1.0.0",
        "continuation": "IX",
        "generated_at_utc": now,
        "policy": "ONLY_BUCKETS_DIGITAL_PHYSICAL_EXTERNAL",
        "physical_execution_freeze": True,
        "digital_release_lock_complete": False,
        "counts": {
            "DIGITAL": len(dig),
            "PHYSICAL": len(phys),
            "EXTERNAL": len(ext),
            "DIGITAL_OPEN": digital_open,
            "TOTAL": len(blockers),
        },
        "buckets": {
            "DIGITAL": {
                "count": len(dig),
                "ids": [b["id"] for b in dig],
                "note": "Hardware packaging + OS prove-gaps; must reach 0 before claiming DIGITAL_RELEASE_LOCK_COMPLETE (not claimed while open)",
            },
            "PHYSICAL": {
                "count": len(phys),
                "ids": [b["id"] for b in phys],
                "note": "Irreducible under PHYSICAL_EXECUTION_FREEZE; EVT measurements pending freeze lift",
            },
            "EXTERNAL": {
                "count": len(ext),
                "ids": [b["id"] for b in ext],
                "note": "COM-HPC NDA, dual eDP, Intel balls, panel/hinge OEM, torque OEM",
            },
        },
        "blockers": blockers,
        "forbidden_bucket_labels": ["MIXED", "UNKNOWN", "PROCESS", "DOCS", "NICE_TO_HAVE"],
        "recommendation": "CONTINUE_DIGITAL_RELEASE_ENGINEERING",
        "note": (
            "Pending Edmund merges of Cont IX dependency PRs (hardware DIGITAL packaging, "
            "device-os clean-env prove). Do not fake final lock."
        ),
    }
    dump_json(doc, CONT_IX / "BLOCKER_BURNDOWN.json")
    return doc


def write_product_release_matrix(now: str) -> dict[str, Any]:
    dig_n = len(digital_blockers())
    products = {
        "student_device": {
            "repo": "gunnchos-hardware-industrial-design",
            "accepted_main_sha": ACCEPTED["gunnchos-hardware-industrial-design"]["sha"],
            "eda_release_clean": True,
            "manufacturer_ready": False,
            "manufacturer_ready_token": "CONDITIONAL_VENDOR_COLLATERAL",
            "digital_pre_evt_release_ready": False,
            "digital_blockers_open": dig_n > 0,
            "notes": "Option B COM-HPC; proxy footprints keep manufacturer_ready conditional",
        },
        "ds_xl": {
            "repo": "gunnchos-hardware-industrial-design",
            "accepted_main_sha": ACCEPTED["gunnchos-hardware-industrial-design"]["sha"],
            "eda_release_clean": True,
            "manufacturer_ready": False,
            "manufacturer_ready_token": "CONDITIONAL_VENDOR_COLLATERAL",
            "digital_pre_evt_release_ready": False,
            "external_blockers": ["IX-E-001", "IX-E-002", "IX-E-004"],
            "notes": "Dual eDP + hinge OEM EXTERNAL; not DIGITAL_PRE_EVT",
        },
        "handheld_hybrid": {
            "repo": "gunnchos-hardware-industrial-design",
            "accepted_main_sha": ACCEPTED["gunnchos-hardware-industrial-design"]["sha"],
            "eda_release_clean": True,
            "manufacturer_ready": False,
            "manufacturer_ready_token": "CONDITIONAL_VENDOR_COLLATERAL",
            "digital_blockers": ["IX-D-002"],
            "notes": "Radxa 260-pin sheets residual DIGITAL",
        },
        "dock": {
            "repo": "gunnchos-hardware-industrial-design",
            "accepted_main_sha": ACCEPTED["gunnchos-hardware-industrial-design"]["sha"],
            "eda_release_clean": True,
            "manufacturer_ready": False,
            "manufacturer_ready_token": "CONDITIONAL_VENDOR_COLLATERAL",
            "external_blockers": ["IX-E-003"],
            "notes": "Intel ball-map EXTERNAL",
        },
        "ring": {
            "repo": "edge-io-measurement-node",
            "accepted_main_sha": ACCEPTED["edge-io-measurement-node"]["sha"],
            "digital_e2e_pass": True,
            "physical_boot_pending": True,
            "notes": "Physical ring boot irreducible under freeze",
        },
        "gunnchos": {
            "repo": "gunnchos-device-os",
            "accepted_main_sha": ACCEPTED["gunnchos-device-os"]["sha"],
            "bootable_reference_digital_pass": True,
            "gate1_status": "MAY_BE_RED_AT_KICKOFF",
            "digital_blockers": ["IX-D-004"],
            "notes": "Cont IX OS prove must clear clean-env before DIGITAL lock",
        },
        "gunnchai": {
            "repo": "gunnchAI3k",
            "accepted_main_sha": ACCEPTED["gunnchAI3k"]["sha"],
            "local_inference_pass": True,
            "physical_runtime_pending": True,
        },
        "games": {
            "anime": ACCEPTED["anime-aggressors"]["sha"],
            "pedestrian": ACCEPTED["pedestrian-pursuit"]["sha"],
            "archive": ACCEPTED["archive-of-life-artifact-world"]["sha"],
            "beatlink": ACCEPTED["beatlink-party"]["sha"],
            "digital_rc_on_accepted_mains": True,
            "physical_fps_separate": True,
        },
    }
    doc = {
        "schema_version": "1.0.0",
        "continuation": "IX",
        "generated_at_utc": now,
        "physical_execution_freeze": True,
        "digital_release_lock_complete": False,
        "ready_for_npi_dfm_and_evt_quotation": False,
        "products": products,
        "forbidden_tokens": [
            "PRODUCTION_READY",
            "MASS_PRODUCTION",
            "CERTIFIED",
            "CARRIER_APPROVED",
            "FULL_OPERATIONAL",
            "6G_CERTIFIED",
            "GATE_8_PASS",
            "EVT_VALIDATED",
        ],
        "allowed_conditional_tokens_with_evidence": [
            "CONDITIONAL_VENDOR_COLLATERAL",
        ],
        "recommendation": "CONTINUE_DIGITAL_RELEASE_ENGINEERING",
    }
    dump_json(doc, CONT_IX / "PRODUCT_RELEASE_MATRIX.json")
    return doc


def write_pre_evt_handoff_matrix(now: str) -> dict[str, Any]:
    doc = {
        "schema_version": "1.0.0",
        "continuation": "IX",
        "generated_at_utc": now,
        "physical_execution_freeze": True,
        "purpose": "Pre-EVT handoff evidence pack — digital only; no purchase/order authority",
        "digital_release_lock_complete": False,
        "ready_for_npi_dfm_and_evt_quotation": False,
        "handoff_lanes": {
            "A_eda_packages": {
                "status": "CONDITIONAL",
                "evidence": "hardware accepted main #51 EDA release-clean",
                "blockers": ["IX-D-001", "IX-D-002", "IX-D-003"],
                "next": "Cont IX hardware tip closes proxy/Radxa/silk",
            },
            "B_os_image_prove": {
                "status": "PENDING_CONT_IX_OS",
                "evidence": "device-os #67 on main; Gate 1 may be red",
                "blockers": ["IX-D-004"],
                "next": "Cont IX OS clean-env prove PR",
            },
            "C_vendor_collateral": {
                "status": "REQUESTED",
                "evidence": "VENDOR_COLLATERAL_REQUESTS.json",
                "blockers": ["IX-E-001", "IX-E-002", "IX-E-003", "IX-E-004", "IX-E-005"],
                "next": "Edmund vendor outreach; CONDITIONAL_VENDOR_COLLATERAL only",
            },
            "D_evt_measurement_plan": {
                "status": "DOCUMENTED_NOT_EXECUTABLE",
                "evidence": "PHYSICAL freeze + IX-P-002",
                "blockers": ["IX-P-001", "IX-P-002"],
                "next": "Freeze lift then EVT measurements; never claim EVT_VALIDATED now",
            },
        },
        "edmund_actions_required_before_npi_quote": [
            "Merge Cont IX DIGITAL dependency PRs (hardware + OS) when green",
            "Confirm DIGITAL blockers=0 on accepted mains",
            "Review vendor collateral requests (no automatic purchase)",
            "Keep PHYSICAL_EXECUTION_FREEZE until explicit lift",
        ],
        "explicitly_not_authorized": [
            "purchase_orders",
            "fab_orders",
            "mass_production",
            "carrier_submission",
            "cert_lab_booking_as_certified_claim",
        ],
        "recommendation": "CONTINUE_DIGITAL_RELEASE_ENGINEERING",
    }
    dump_json(doc, CONT_IX / "PRE_EVT_HANDOFF_MATRIX.json")
    return doc


def write_vendor_collateral_requests(now: str) -> dict[str, Any]:
    requests = [
        {
            "id": "VCR-001",
            "blocker_id": "IX-E-001",
            "vendor": "ADLINK/PICMG",
            "request": "COM-HPC Mini 400-pin (+ dual eDP) pin map under NDA",
            "product": "student_dsxl",
            "status": "REQUESTED",
            "allows_token_when_received": "CONDITIONAL_VENDOR_COLLATERAL",
            "owner_repo": "gunnchos-hardware-industrial-design",
            "owner_file": "program/vendor/COM_HPC_NDA_REQUEST.md",
        },
        {
            "id": "VCR-002",
            "blocker_id": "IX-E-002",
            "vendor": "Panel OEM (TBD)",
            "request": "Dual eDP interconnect map + timing/power tables",
            "product": "ds_xl",
            "status": "REQUESTED",
            "allows_token_when_received": "CONDITIONAL_VENDOR_COLLATERAL",
            "owner_repo": "gunnchos-hardware-industrial-design",
            "owner_file": "program/vendor/DUAL_EDP_PANEL_REQUEST.md",
        },
        {
            "id": "VCR-003",
            "blocker_id": "IX-E-003",
            "vendor": "Intel",
            "request": "JHL8440/JHL9040R ball maps",
            "product": "dock",
            "status": "REQUESTED",
            "allows_token_when_received": "CONDITIONAL_VENDOR_COLLATERAL",
            "owner_repo": "gunnchos-hardware-industrial-design",
            "owner_file": "program/vendor/INTEL_JHL_BALLMAP_REQUEST.md",
        },
        {
            "id": "VCR-004",
            "blocker_id": "IX-E-004",
            "vendor": "Panel/hinge OEM (TBD)",
            "request": "AVL + bend/life specs for DS-XL hinge/flex",
            "product": "ds_xl",
            "status": "REQUESTED",
            "allows_token_when_received": "CONDITIONAL_VENDOR_COLLATERAL",
            "owner_repo": "gunnchos-hardware-industrial-design",
            "owner_file": "program/vendor/PANEL_HINGE_OEM_REQUEST.md",
        },
        {
            "id": "VCR-005",
            "blocker_id": "IX-E-005",
            "vendor": "Fastener/OEM (TBD)",
            "request": "Assembly torque tables for enclosure fasteners",
            "product": "all_devices",
            "status": "REQUESTED",
            "allows_token_when_received": "CONDITIONAL_VENDOR_COLLATERAL",
            "owner_repo": "gunnchos-hardware-industrial-design",
            "owner_file": "program/vendor/TORQUE_OEM_REQUEST.md",
        },
    ]
    doc = {
        "schema_version": "1.0.0",
        "continuation": "IX",
        "generated_at_utc": now,
        "policy": "CONDITIONAL_VENDOR_COLLATERAL_ONLY_WHEN_EVIDENCE_PRESENT",
        "physical_execution_freeze": True,
        "purchase_authorized": False,
        "requests": requests,
        "forbidden_until_evidence": [
            "PRODUCTION_READY",
            "MASS_PRODUCTION",
            "CERTIFIED",
            "CARRIER_APPROVED",
            "FULL_OPERATIONAL",
            "6G_CERTIFIED",
            "GATE_8_PASS",
            "EVT_VALIDATED",
        ],
        "notes": (
            "Requests are evidence outreach only. Receipt enables CONDITIONAL_VENDOR_COLLATERAL "
            "manufacturer tokens with evidence paths — never PRODUCTION_READY / MASS_PRODUCTION."
        ),
    }
    dump_json(doc, CONT_IX / "VENDOR_COLLATERAL_REQUESTS.json")
    return doc


def write_sibling_draft_registry(now: str) -> None:
    tip = git_tip()
    payload = {
        "schema_version": "1.0.0",
        "continuation": "IX",
        "generated_at_utc": now,
        "policy": "DRAFT_TIPS_NOT_ACCEPTED_MAIN_NOT_FINAL_UMBRELLA",
        "accepted_mains": {k: v["sha"] for k, v in ACCEPTED.items()},
        "drafts": {
            "field_kit_digital_release_lock": {
                "repo": "gunnchos-7gc-ai-ran-field-kit",
                "branch": "continuation-ix/digital-release-lock",
                "role": "control_plane_digital_release_lock_pre_evt_handoff",
                "pr": None,
                "sha": tip,
                "status": "DRAFT_TIP_NOT_ACCEPTED_MAIN",
                "note": "Cont IX Lane J; NEVER merge from agent; digital_release_lock_complete=false until DIGITAL=0",
            },
            "device_os_clean_env_prove": {
                "repo": "gunnchos-device-os",
                "branch": "continuation-ix/os-clean-env-prove",
                "role": "IX-D-004_gate1_clean_env",
                "pr": None,
                "sha": None,
                "status": "PENDING_OPEN",
                "base_accepted_main": ACCEPTED["gunnchos-device-os"]["sha"],
                "note": "Cont IX OS dependency; Gate 1 may be red at kickoff; draft tip NOT accepted main",
            },
            "hardware_digital_packaging": {
                "repo": "gunnchos-hardware-industrial-design",
                "branch": "continuation-ix/digital-packaging-closure",
                "role": "IX-D-001_002_003_proxy_radxa_silk",
                "pr": None,
                "sha": None,
                "status": "PENDING_OPEN",
                "base_accepted_main": ACCEPTED["gunnchos-hardware-industrial-design"]["sha"],
                "note": "Cont IX hardware DIGITAL packaging; draft tip NOT accepted main",
            },
        },
        "final_umbrella": False,
        "digital_release_lock_complete": False,
        "digital_pre_evt_release_ready": False,
        "recommendation": "CONTINUE_DIGITAL_RELEASE_ENGINEERING",
    }
    dump_yaml(payload, CONT_IX / "continuation_ix_sibling_draft_registry.yaml")


def write_report_scaffold(now: str, burndown: dict[str, Any]) -> None:
    counts = burndown["counts"]
    lines = [
        "# Continuation IX — Report A–T (scaffold)",
        "",
        f"Updated: {now}",
        "",
        "Doctrine: `PHYSICAL_EXECUTION_FREEZE=ACTIVE`; Cursor never merges; DRAFT PR only.",
        "",
        "## A — Wave intent",
        "",
        "Final Digital Release Lock + Pre-EVT handoff evidence. Extends Cont VIII accepted mains.",
        "",
        "## B — Accepted mains (Cont VIII post-merge lock)",
        "",
        "| Repo | Accepted main SHA | Notes |",
        "|------|-------------------|-------|",
    ]
    for name, meta in ACCEPTED.items():
        lines.append(f"| `{name}` | `{meta['sha']}` | {meta.get('note', '')} |")
    lines += [
        "",
        "## C — Digital release lock status",
        "",
        f"- `digital_release_lock_complete`: **false** (DIGITAL open={counts['DIGITAL_OPEN']})",
        "- `ready_for_npi_dfm_and_evt_quotation`: **false**",
        "- Recommendation: `CONTINUE_DIGITAL_RELEASE_ENGINEERING`",
        "",
        "## D–S — Sections pending sibling Cont IX tip registration",
        "",
        "Finalize A–T after sibling Cont IX hardware/OS draft tips are known and registered.",
        "Open dependency DRAFT PRs; do not fake final lock before Edmund merges.",
        "",
        "## T — Burndown summary",
        "",
        f"| Bucket | Count |",
        f"|--------|------:|",
        f"| DIGITAL | {counts['DIGITAL']} |",
        f"| PHYSICAL | {counts['PHYSICAL']} |",
        f"| EXTERNAL | {counts['EXTERNAL']} |",
        f"| TOTAL | {counts['TOTAL']} |",
        "",
        "Machine-readable: `program/full_product/continuation_ix/BLOCKER_BURNDOWN.json`",
        "",
        "```text",
        "CONTINUE_DIGITAL_RELEASE_ENGINEERING",
        "```",
        "",
    ]
    (CONT_IX / "CONTINUATION_IX_REPORT_A_T.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def write_baseline_report(now: str) -> None:
    lines = [
        "# Continuation IX — Accepted Main Lock",
        "",
        f"Updated: {now}",
        "",
        "Doctrine: `FULL_PRODUCT_ENTIRETY` + digital release lock attempt; "
        "`PHYSICAL_EXECUTION_FREEZE=ACTIVE`; Cursor never merges.",
        "",
        "Policy: accepted tips are **merged `origin/main` SHAs only** — never draft tips.",
        "",
        "`digital_release_lock_complete=false` until DIGITAL blockers=0 on accepted mains "
        "after Cont IX sibling merges.",
        "",
        "| Repo | origin/main SHA | Notes |",
        "|------|-----------------|-------|",
    ]
    for name, meta in ACCEPTED.items():
        lines.append(f"| {name} | `{meta['sha']}` | {meta.get('note', '')} |")
    lines += [
        "",
        "Machine-readable: [`ACCEPTED_MAIN_LOCK.json`](../continuation_ix/ACCEPTED_MAIN_LOCK.json)",
        "",
    ]
    (REPORTS / "CONTINUATION_IX_ACCEPTED_MAIN_LOCK.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def patch_soft_matrix(now: str) -> None:
    soft_path = FP / "software_integration_matrix.yaml"
    if not soft_path.exists():
        return
    soft = yaml.safe_load(soft_path.read_text(encoding="utf-8")) or {}
    soft["updated_at_utc"] = now
    soft["continuation"] = "IX"
    soft["accepted_main_policy"] = "MERGED_on_main_SHA_only"
    repos = soft.setdefault("repos", {})
    for name, meta in ACCEPTED.items():
        entry = repos.setdefault(name, {})
        entry["accepted_main_sha"] = meta["sha"]
        entry["merged_prs"] = meta.get("merged_prs", entry.get("merged_prs"))
        entry["status"] = "CONT_IX_ACCEPTED_MAIN_LOCK"
        entry["pr_state"] = "MERGED"
        if meta.get("ci"):
            entry["main_ci"] = meta["ci"]
        entry["note"] = meta.get("note", entry.get("note", ""))
    soft["continuation_ix_drafts"] = (
        "SEE_continuation_ix/continuation_ix_sibling_draft_registry.yaml"
    )
    soft["final_umbrella"] = False
    soft["digital_release_lock_complete"] = False
    dump_yaml(soft, soft_path)


def patch_master_status(now: str, burndown: dict[str, Any]) -> None:
    path = REPORTS / "FULL_PRODUCT_MASTER_STATUS.md"
    counts = burndown["counts"]
    block = [
        "",
        "## Continuation IX — Digital release lock (pre-EVT handoff)",
        "",
        f"Updated: {now}",
        "",
        "Evidence consumer Cont IX — **not** DIGITAL_RELEASE_LOCK_COMPLETE "
        f"(DIGITAL open={counts['DIGITAL_OPEN']}; pending Edmund merges of IX deps).",
        "",
        f"- DIGITAL blockers: **{counts['DIGITAL']}**",
        f"- PHYSICAL blockers: **{counts['PHYSICAL']}** (freeze)",
        f"- EXTERNAL blockers: **{counts['EXTERNAL']}**",
        "- Recommendation: `CONTINUE_DIGITAL_RELEASE_ENGINEERING`",
        "",
        "Artifacts: `program/full_product/continuation_ix/`",
        "",
    ]
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if "## Continuation IX — Digital release lock" in text:
            import re

            text = re.sub(
                r"\n## Continuation IX — Digital release lock \(pre-EVT handoff\)\n.*?(?=\n## |\Z)",
                "\n".join(block) + "\n",
                text,
                flags=re.S,
            )
        else:
            text = text.rstrip() + "\n" + "\n".join(block)
        path.write_text(text, encoding="utf-8")
    else:
        path.write_text("# Full Product Master Status\n" + "\n".join(block), encoding="utf-8")


def write_shared_baseline(now: str) -> None:
    """Refresh program/full_product/_baseline_accepted_mains.json to Cont IX lock."""
    doc = {
        "schema_version": "1.3",
        "continuation": "IX",
        "wave": "CONTINUATION_IX_DIGITAL_RELEASE_LOCK",
        "generated_at_utc": now,
        "updated_at_utc": now,
        "immutable_at_start": True,
        "scope": "full_product_entirety_baseline_accepted_mains",
        "physical_execution_freeze": True,
        "accepted_main_policy": "MERGED_on_main_SHA_only_no_cursor_branch_as_accepted",
        "immutable_note": (
            "Cont IX accepted mains = Cont VIII post-merge tips (#41 field-kit, #51 hardware, "
            "#67 device-os + prior sibling Cont VIII mains). DIGITAL_RELEASE_LOCK_COMPLETE "
            "remains false until DIGITAL packaging/OS blockers=0 after Cont IX sibling merges."
        ),
        "repos": {
            name: {
                "origin_main": meta["sha"],
                "accepted_main_sha": meta["sha"],
                "merged_prs": meta.get("merged_prs", []),
                "ci": meta.get("ci"),
                "note": meta.get("note"),
                **({"token": meta["token"]} if meta.get("token") else {}),
            }
            for name, meta in ACCEPTED.items()
        },
        "accepted_mains": {k: v["sha"] for k, v in ACCEPTED.items()},
        "digital_release_lock_complete": False,
        "final_umbrella": False,
        "final_umbrella_policy": "NOT_FINAL_UMBRELLA_UNTIL_DIGITAL_BLOCKERS_ZERO_ON_ACCEPTED_MAINS",
    }
    dump_json(doc, FP / "_baseline_accepted_mains.json")


def main() -> int:
    now = utc_now()
    CONT_IX.mkdir(parents=True, exist_ok=True)

    write_shared_baseline(now)
    lock = write_accepted_main_lock(now)
    reproof = write_readiness_reproof(now)
    burndown = write_blocker_burndown(now)
    write_product_release_matrix(now)
    write_pre_evt_handoff_matrix(now)
    write_vendor_collateral_requests(now)
    write_sibling_draft_registry(now)
    write_report_scaffold(now, burndown)
    write_baseline_report(now)
    patch_soft_matrix(now)
    patch_master_status(now, burndown)

    print("CONT_IX_PROVE_COMPLETE")
    print(
        json.dumps(
            {
                "digital_release_lock_complete": lock["digital_release_lock_complete"],
                "recommendation": lock["recommendation"],
                "counts": burndown["counts"],
                "reproof_digital_residual": reproof["cont_ix_digital_packaging_residual_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
