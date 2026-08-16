#!/usr/bin/env python3
"""Generate Charter Engineering Requirement Register V2 (atomic decomposition)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "charter_exhaustion" / "CHARTER_ENGINEERING_REQUIREMENT_REGISTER_V2.json"

SHA = {
    "anime-aggressors": "16df36d0025a6d124817a1800de65abef689d51f",
    "pedestrian-pursuit": "3f4dafd0e455a0cf22523bab48a094a542d3141d",
    "archive-of-life-artifact-world": "64fcf3a73d9a0db4e13523f762cf3fd651d7ddaa",
    "beatlink-party": "4b3970c9bc327ba7a1cec43ff7a905d91cd3070b",
    "gunnchos-device-os": "3858e760295ad35828ff141919681f2bb8685cf0",
    "gunnchos-hardware-industrial-design": "4ba876d42f59f03d4b5c5ef0ca776e1253da814d",
    "gunnchos-7gc-ai-ran-field-kit": "b32fc06191608054921c07cff63725129601e9a6",
    "waike-research-ops": "5c5f6cafb1d60c7d67258b719b75cac42c18d750",
    "gunnchAI3k": "e9d4909e09f8bfaf12802aa16c548993ff0f2c85",
    "multi": "b32fc06191608054921c07cff63725129601e9a6",
}

# Tip SHAs that must never be presented as accepted main.
FORBIDDEN_BRANCH_AS_MAIN = {
    "a320c7c7edf0f6d60f27833a6488fcee8038b3e0",
    "e05d3edb82a978a6e4d6e1481ba20d0d53305b94",
    "82dbbc2d87eb544675b33b0d99b1795712b7d54d",
}

OPEN = "ATOMIC_DIGITAL_IMPLEMENTATION_OPEN"
COMPLETE = "DIGITAL_IMPLEMENTATION_COMPLETE"
EXT = "DIGITAL_PREPARATION_COMPLETE_EXTERNAL_PENDING"
HUM = "DIGITAL_PREPARATION_COMPLETE_HUMAN_PENDING"
PHY = "DIGITAL_PREPARATION_COMPLETE_PHYSICAL_PENDING"
STD = "STANDARD_PENDING"
OWN = "OWNER_DECISION_PENDING"

MISCLASSIFIED_REOPENED = [
    "SUPPLY_CHAIN_LIFECYCLE",
    "RELIABILITY_ENVIRONMENTAL_TESTS",
    "ERGONOMICS_HUMAN_FACTORS",
    "WARRANTY_RMA_REPAIR_SPARES",
    "FACTORY_PROVISIONING",
    "PACKAGING_FIRST_USE_RECYCLING",
    "EVT_CALIBRATION",
    "HIL_CORRELATION",
    "BATTERY_THERMAL_RF",
    "RING_SPATIAL_PHYSICAL",
    "EXTERNAL_PENTEST",
    "CARRIER_APPROVAL",
    "PRIVACY_DATA_GOVERNANCE",
    "LICENSING_IP_MEDIA_MODEL_DATA_RIGHTS",
]


def row(
    rid: str,
    *,
    parent: str | None,
    layer: str,
    product: str,
    owner_repo: str,
    description: str,
    criteria: str,
    state: str,
    digital_possible: bool,
    digital_work: str,
    final_dep: str | None = None,
    next_packet: str | None = None,
    depth: str = "D_INCOMPLETE",
    evidence: str = "E0_or_pending",
    verification: str = "not_accepted_main",
    impl: list[str] | None = None,
    tests: list[str] | None = None,
    runtime: list[str] | None = None,
    s0: int = 0,
    s1: int = 0,
    s2: int = 0,
    reopened: bool = False,
    reopen_reason: str | None = None,
    irreducible: bool = False,
    children_required: bool = False,
) -> dict[str, Any]:
    sha = SHA.get(owner_repo, SHA["multi"])
    if sha in FORBIDDEN_BRANCH_AS_MAIN:
        raise SystemExit(f"forbidden branch SHA as main for {rid}: {sha}")
    return {
        "requirement_id": rid,
        "parent_requirement": parent,
        "layer": layer,
        "product": product,
        "owner_repo": owner_repo,
        "accepted_main_sha": sha,
        "description": description,
        "digital_acceptance_criteria": criteria,
        "real_implementation_files": impl or [],
        "real_test_files": tests or [],
        "real_runtime_evidence": runtime or [],
        "evidence_level": evidence,
        "depth_level": depth,
        "verification_level": verification,
        "S0": s0,
        "S1": s1,
        "S2": s2,
        "digital_work_still_possible": digital_possible,
        "digital_work_description": digital_work,
        "engineering_state": state,
        "final_non_digital_dependency": final_dep,
        "next_packet": next_packet,
        "reopened": reopened,
        "reopen_reason": reopen_reason,
        "irreducible_non_digital": irreducible,
        "children_required_for_parent_complete": children_required,
    }


def open_child(
    rid: str,
    parent: str,
    layer: str,
    product: str,
    owner_repo: str,
    description: str,
    criteria: str,
    work: str,
    next_packet: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    return row(
        rid,
        parent=parent,
        layer=layer,
        product=product,
        owner_repo=owner_repo,
        description=description,
        criteria=criteria,
        state=OPEN,
        digital_possible=True,
        digital_work=work,
        next_packet=next_packet,
        **kwargs,
    )


def pending_irreducible(
    rid: str,
    parent: str | None,
    layer: str,
    product: str,
    owner_repo: str,
    description: str,
    state: str,
    final_dep: str,
    *,
    reopened: bool = False,
    reopen_reason: str | None = None,
) -> dict[str, Any]:
    return row(
        rid,
        parent=parent,
        layer=layer,
        product=product,
        owner_repo=owner_repo,
        description=description,
        criteria="Irreducible non-digital acceptance; digital prep tracked on sibling row.",
        state=state,
        digital_possible=False,
        digital_work="None remaining beyond readiness package tracked separately.",
        final_dep=final_dep,
        depth="D_INCOMPLETE",
        irreducible=True,
        reopened=reopened,
        reopen_reason=reopen_reason,
    )


def build() -> dict[str, Any]:
    reqs: list[dict[str, Any]] = []

    # --- Control-plane parents that remain complete (definition-only) ---
    for rid, desc in [
        ("CHARTER_NARRATIVE", "Product charter narrative on accepted field-kit main"),
        ("REPO_OWNERSHIP_MAP", "Repo ownership map"),
        ("CLAIM_BOUNDARIES", "Claim boundary YAML"),
        ("COMPLETION_REGISTER_V1", "WP-012 completion register (coarse; superseded by V2)"),
    ]:
        reqs.append(
            row(
                rid,
                parent=None,
                layer="charter_control_plane",
                product="ecosystem",
                owner_repo="gunnchos-7gc-ai-ran-field-kit",
                description=desc,
                criteria="Accepted-main charter artifact present and claim-bounded.",
                state=COMPLETE,
                digital_possible=False,
                digital_work="Definition complete; product engineering tracked atomically elsewhere.",
                depth="D2+",
                evidence="E4_independent",
                verification="accepted_main",
                impl=[f"program/charter/{rid.lower()}.md"],
                irreducible=True,
            )
        )

    reqs.append(
        row(
            "CHARTER_REGISTER_V2",
            parent=None,
            layer="charter_control_plane",
            product="ecosystem",
            owner_repo="gunnchos-7gc-ai-ran-field-kit",
            description="Atomic engineering requirement register V2",
            criteria="Register exists; validator PASS; ATOMIC_DIGITAL_IMPLEMENTATION_OPEN truthful.",
            state=OPEN,
            digital_possible=True,
            digital_work="Maintain register + validator as atomic rows close.",
            next_packet="CONTROL-PLANE-V2",
            children_required=True,
            impl=["artifacts/charter_exhaustion/CHARTER_ENGINEERING_REQUIREMENT_REGISTER_V2.json"],
            tests=["scripts/validate_charter_requirement_register_v2.py"],
            evidence="E2_branch",
            depth="D3_register",
            verification="branch_or_open",
        )
    )

    reqs.append(
        row(
            "WP001_START",
            parent=None,
            layer="charter_control_plane",
            product="ecosystem",
            owner_repo="gunnchos-7gc-ai-ran-field-kit",
            description="WP-001 start lock",
            criteria="Owner decision only after ATOMIC_DIGITAL_IMPLEMENTATION_OPEN=0.",
            state=OWN,
            digital_possible=False,
            digital_work="Do not start WP-001.",
            final_dep=OWN,
            irreducible=True,
            next_packet=None,
        )
    )

    # --- Hardware / firmware per device × domain ---
    devices = [
        ("STUDENT", "Student 14.5", "student_14_5"),
        ("DSXL", "DS-XL Coder", "dsxl_coder"),
        ("HANDHELD", "Handheld Hybrid", "handheld_hybrid"),
        ("DOCK", "First-party Dock", "first_party_dock"),
        ("RINGS", "Edge I/O Rings", "edge_io_rings"),
    ]
    hw_domains = [
        "architecture",
        "schematic",
        "pcb",
        "bom_avl",
        "power",
        "battery_charging",
        "display",
        "storage",
        "audio",
        "usb_c_pd",
        "dock_iface",
        "wireless",
        "cellular",
        "rf",
        "thermal",
        "mechanical_cad",
        "serviceability",
        "factory_test",
        "driver_support",
        "boot_firmware",
        "power_firmware",
        "input_firmware",
        "wireless_modem_integration",
        "diagnostics",
        "ota_recovery",
    ]
    # Ring-specific extra
    ring_extra = ["ring_firmware", "ring_spatial_stack"]

    reqs.append(
        row(
            "HW_FIRMWARE_DIGITAL_PACKAGE",
            parent=None,
            layer="hardware_firmware",
            product="all_five_forms",
            owner_repo="gunnchos-hardware-industrial-design",
            description="Overall hardware/firmware digital package",
            criteria="All device/domain digital children complete; package COMPLETE token only then.",
            state=OPEN,
            digital_possible=True,
            digital_work="Close atomic device/domain gaps; keep COMPLETE=false until then.",
            next_packet="HW-002",
            children_required=True,
            impl=["artifacts/charter_exhaustion/HW_FIRMWARE_DIGITAL_TRUTH_AUDIT.json"],
            evidence="E4_independent",
            depth="D_PARTIAL_EDA",
            verification="accepted_main",
            s2=1,
            reopened=True,
            reopen_reason="Truth audit accepted on main; package COMPLETE remains false.",
        )
    )

    for did, dname, product in devices:
        parent = f"HW_{did}"
        reqs.append(
            row(
                parent,
                parent="HW_FIRMWARE_DIGITAL_PACKAGE",
                layer="hardware_firmware",
                product=product,
                owner_repo="gunnchos-hardware-industrial-design",
                description=f"{dname} hardware/firmware digital completeness",
                criteria=f"All {dname} domain children digitally closed or precisely isolated EXTERNAL.",
                state=OPEN,
                digital_possible=True,
                digital_work=f"Advance {dname} EDA/firmware/driver domains.",
                next_packet="HW-002",
                children_required=True,
            )
        )
        domains = list(hw_domains)
        if did == "RINGS":
            domains.extend(ring_extra)
        if did == "HANDHELD":
            domains.append("image_slot_fit")
        for dom in domains:
            pkt = "HW-002"
            work = f"Implement/verify {dname} {dom} digital artifacts with tests."
            if did == "HANDHELD" and dom == "image_slot_fit":
                work = "Close NPI_DEFECT-HANDHELD-IMAGE-SLOT-FIT-001 with real realm sizes/margins."
            if did == "RINGS" and dom == "ring_firmware":
                work = "Complete Zephyr west workspace and real west build (no manifest-only PASS)."
            reqs.append(
                open_child(
                    f"HW_{did}_{dom.upper()}",
                    parent,
                    "hardware_firmware",
                    product,
                    "gunnchos-hardware-industrial-design",
                    f"{dname}: {dom}",
                    f"Real files + tests for {dom}; no fabricated vendor pin maps.",
                    work,
                    next_packet=pkt,
                )
            )

    # --- gunnchOS / middleware services ---
    os_services = [
        "identity",
        "hal",
        "session_ui",
        "input",
        "display",
        "dock",
        "ring",
        "continuity",
        "packaging",
        "permissions",
        "ai_interface",
        "connectivity",
        "offline_sync",
        "encrypted_storage",
        "secure_measured_boot",
        "attestation",
        "ota",
        "rollback",
        "recovery",
        "fleet",
        "sandbox",
        "logs",
        "diagnostics",
        "accessibility",
        "profiles",
        "developer_mode",
        "gunnchsdk",
        "image_realms_evt_factory_recovery",
        "creator_studio_first_party_app",
        "waike_learning_first_party_app",
        "gunnchai_tutor_first_party_app",
    ]
    reqs.append(
        row(
            "GUNNCHOS_MIDDLEWARE",
            parent=None,
            layer="gunnchOS",
            product="gunnchos",
            owner_repo="gunnchos-device-os",
            description="gunnchOS + middleware digital product depth",
            criteria="All service children meet digital acceptance; shipping image still false.",
            state=OPEN,
            digital_possible=True,
            digital_work="Deepen services beyond WP-013 foundation on accepted main 3858e76.",
            next_packet="PLATFORM-001",
            children_required=True,
            evidence="E4_independent",
            depth="D5_foundation",
            verification="accepted_main",
            impl=["sdk/", "artifacts/wp013/"],
        )
    )
    for svc in os_services:
        pkt = "PLATFORM-001"
        if svc in {
            "creator_studio_first_party_app",
            "waike_learning_first_party_app",
            "gunnchai_tutor_first_party_app",
            "gunnchsdk",
        }:
            pkt = "PLATFORM-001"
        reqs.append(
            open_child(
                f"GUNNCHOS_{svc.upper()}",
                "GUNNCHOS_MIDDLEWARE",
                "gunnchOS",
                "gunnchos",
                "gunnchos-device-os",
                f"gunnchOS service: {svc}",
                f"Real implementation + tests + runtime evidence for {svc}.",
                f"Implement/harden {svc} beyond stubs/thin clients.",
                next_packet=pkt,
            )
        )

    # Device Lab digital tokens (still open; #103 HOLD)
    lab_children = [
        ("DEVICE_LAB_10_10_DIGITAL", "Independent 10/10 Device Lab on accepted mains"),
        ("LIVE_GUNNCHOS_VISUAL", "Live gunnchOS visual proof"),
        ("DSXL_DUAL_COMPOSITOR_UX", "DS-XL dual compositor UX"),
        ("RING_APP_STATE_MUTATION", "Ring to real app state mutation"),
        ("FOUR_GAME_PRODUCTION_RUNTIME", "Four-game real runtime Device Lab"),
        ("ECO010_FULL_SOAK", "ECO-010 soak on accepted artifacts"),
    ]
    reqs.append(
        row(
            "DEVICE_LAB",
            parent=None,
            layer="device_lab",
            product="ecosystem",
            owner_repo="gunnchos-device-os",
            description="Device Lab final digital acceptance",
            criteria="All lab children PASS on accepted owner mains (no surrogates).",
            state=OPEN,
            digital_possible=True,
            digital_work="Reconcile #103 after Anime+#104 mains; do not merge historical tip blindly.",
            next_packet="WP-011R.2",
            children_required=True,
        )
    )
    for rid, desc in lab_children:
        reqs.append(
            open_child(
                rid,
                "DEVICE_LAB",
                "device_lab",
                "ecosystem",
                "gunnchos-device-os",
                desc,
                f"{desc} reproducible from accepted mains.",
                "Rebase/reconcile Device Lab evidence onto accepted Anime + device-os mains.",
                next_packet="WP-011R.2",
            )
        )

    # --- Games ---
    game_common = [
        "core_runtime",
        "full_feature_completeness",
        "launch_content_completeness",
        "ai_cpu",
        "input_modes",
        "save_progression",
        "audio",
        "accessibility",
        "performance",
        "crash_recovery",
        "device_lab_integration",
        "human_polish",
    ]

    def add_game(parent_id: str, product: str, repo: str, packet: str, extra: list[tuple[str, str]]) -> None:
        reqs.append(
            row(
                parent_id,
                parent=None,
                layer="games",
                product=product,
                owner_repo=repo,
                description=f"{product} full digital product depth",
                criteria="All facet/fighter/mode children digitally closed; human polish remains HUMAN.",
                state=OPEN,
                digital_possible=True,
                digital_work=f"Exhaust digital facets for {product}.",
                next_packet=packet,
                children_required=True,
                evidence="E4_independent",
                verification="accepted_main",
                depth="D5_production_gate_partial",
            )
        )
        for facet in game_common:
            if facet == "human_polish":
                # digital instrumentation OPEN + human pending sibling
                reqs.append(
                    open_child(
                        f"{parent_id}_HUMAN_POLISH_INSTRUMENTATION",
                        parent_id,
                        "games",
                        product,
                        repo,
                        f"{product}: human polish capture/instrumentation",
                        "Telemetry, review captures, and defect hooks for polish reviews.",
                        "Add experience-review capture hooks and defect linkage.",
                        next_packet=packet,
                    )
                )
                reqs.append(
                    pending_irreducible(
                        f"{parent_id}_HUMAN_POLISH_VALIDATION",
                        parent_id,
                        "games",
                        product,
                        repo,
                        f"{product}: real human polish validation",
                        HUM,
                        HUM,
                    )
                )
                continue
            if facet == "audio":
                reqs.append(
                    open_child(
                        f"{parent_id}_AUDIO_DIGITAL",
                        parent_id,
                        "games",
                        product,
                        repo,
                        f"{product}: digital audio hook/runtime",
                        "Procedural/runtime audio path proven in CI/Device Lab without claiming acoustic physical.",
                        "Complete digital audio path evidence.",
                        next_packet=packet,
                    )
                )
                reqs.append(
                    pending_irreducible(
                        f"{parent_id}_AUDIO_ACOUSTIC_PHYSICAL",
                        parent_id,
                        "games",
                        product,
                        repo,
                        f"{product}: acoustic output physical validation",
                        PHY,
                        PHY,
                    )
                )
                continue
            reqs.append(
                open_child(
                    f"{parent_id}_{facet.upper()}",
                    parent_id,
                    "games",
                    product,
                    repo,
                    f"{product}: {facet}",
                    f"Digital acceptance for {facet}.",
                    f"Implement/verify {facet}.",
                    next_packet=packet,
                )
            )
        for eid, edesc in extra:
            reqs.append(
                open_child(
                    eid,
                    parent_id,
                    "games",
                    product,
                    repo,
                    edesc,
                    f"Differentiated digital evidence for {edesc}.",
                    f"Implement distinct behavior/content for {edesc}.",
                    next_packet=packet,
                )
            )

    fighters = [
        ("EMBER_VALE", "Ember Vale fighter differentiation"),
        ("ROOK_IRONSIDE", "Rook Ironside fighter differentiation"),
        ("JUNO_SPARK", "Juno Spark fighter differentiation"),
        ("KAIA_WINDROW", "Kaia Windrow fighter differentiation"),
        ("NIX_CALDER", "Nix Calder fighter differentiation"),
        ("ORION_VELL", "Orion Vell fighter differentiation"),
        ("VESPER_NYX", "Vesper Nyx fighter differentiation"),
    ]
    add_game(
        "GAME_ANIME",
        "anime-aggressors",
        "anime-aggressors",
        "GAME-001",
        [(f"GAME_ANIME_FIGHTER_{fid}", desc) for fid, desc in fighters]
        + [
            ("GAME_ANIME_CHARACTER_SELECT", "Character select"),
            ("GAME_ANIME_STAGES", "Stages"),
            ("GAME_ANIME_RULES", "Match rules"),
            ("GAME_ANIME_CPU_DIFFICULTY", "CPU difficulty"),
            ("GAME_ANIME_TRAINING", "Training mode"),
            ("GAME_ANIME_LOCAL_VERSUS", "Local versus"),
        ],
    )

    beat_modes = [
        ("BEAT_TAP", "Beat Tap mode"),
        ("CALL_AND_RESPONSE", "Call and Response mode"),
        ("KARAOKE", "Karaoke mode"),
        ("BAND_ROLES", "Band Roles mode"),
        ("PREDICTION_TRIVIA", "Prediction/Trivia mode"),
        ("AUDIENCE_IMPACT", "Audience impact"),
        ("ROOM_LIFECYCLE", "Room lifecycle"),
        ("HOST_MIGRATION", "Host migration"),
        ("MODERATION_PRIVACY", "Moderation/privacy"),
        ("PROVIDER_MEDIA_RIGHTS_ARCH", "Provider/media rights architecture"),
    ]
    add_game(
        "GAME_BEATLINK",
        "beatlink-party",
        "beatlink-party",
        "GAME-002",
        [(f"GAME_BEATLINK_{mid}", desc) for mid, desc in beat_modes],
    )

    archive_facets = [
        ("EXPLORATION", "World exploration"),
        ("REGIONS_ERAS", "Regions/eras"),
        ("SPECIES_INGEST", "Species ingest"),
        ("TAXONOMY", "Taxonomy"),
        ("PROVENANCE", "Provenance"),
        ("ARCHIVEDEX", "ArchiveDex"),
        ("COMPANION_PROGRESSION", "Companion progression"),
        ("COMPANION_CUSTOMIZATION", "Companion customization"),
        ("OFFLINE_DATA", "Offline data"),
        ("SCIENTIFIC_COVERAGE", "Scientific coverage digital pipeline"),
    ]
    add_game(
        "GAME_ARCHIVE",
        "archive-of-life",
        "archive-of-life-artifact-world",
        "GAME-003",
        [(f"GAME_ARCHIVE_{fid}", desc) for fid, desc in archive_facets],
    )
    # scientific coverage external acceptance sibling
    reqs.append(
        pending_irreducible(
            "GAME_ARCHIVE_SCIENTIFIC_DATA_EXTERNAL",
            "GAME_ARCHIVE",
            "games",
            "archive-of-life",
            "archive-of-life-artifact-world",
            "Scientific data rights/coverage external acceptance",
            EXT,
            EXT,
        )
    )

    ped_facets = [
        ("TRACKS", "Tracks"),
        ("CPU", "CPU racers"),
        ("ITEMS_ABILITIES", "Items/abilities"),
        ("RACE_MODES", "Race modes"),
        ("PROGRESSION", "Progression"),
        ("SENSE_OF_SPEED", "Sense-of-speed feel instrumentation"),
        ("TUTORIAL_ONBOARDING", "Tutorial/onboarding"),
    ]
    add_game(
        "GAME_PEDESTRIAN",
        "pedestrian-pursuit",
        "pedestrian-pursuit",
        "GAME-004",
        [(f"GAME_PEDESTRIAN_{fid}", desc) for fid, desc in ped_facets],
    )

    # --- gunnchAI ---
    ai_caps = [
        "model_registry",
        "router",
        "nano",
        "local_fast",
        "local_pro",
        "rag",
        "memory",
        "projects",
        "research_citations",
        "agents",
        "tools",
        "skills",
        "permissions",
        "voice",
        "vision",
        "screen_context",
        "coding",
        "tutoring",
        "office_workflows",
        "network_assistance",
        "game_coaching",
        "translation",
        "accessibility",
        "offline",
        "evals",
        "security_evals",
        "device_lab_integration",
        "waike_integration",
    ]
    reqs.append(
        row(
            "GUNNCHAI",
            parent=None,
            layer="gunnchAI",
            product="gunnchai",
            owner_repo="gunnchAI3k",
            description="gunnchAI product depth",
            criteria="Capability children digitally proven; not generic chatbot shell.",
            state=OPEN,
            digital_possible=True,
            digital_work="Implement capability depth beyond thin tutor client.",
            next_packet="PLATFORM-001",
            children_required=True,
        )
    )
    for cap in ai_caps:
        reqs.append(
            open_child(
                f"GUNNCHAI_{cap.upper()}",
                "GUNNCHAI",
                "gunnchAI",
                "gunnchai",
                "gunnchAI3k",
                f"gunnchAI: {cap}",
                f"Digital acceptance for {cap}.",
                f"Implement/verify {cap}.",
                next_packet="PLATFORM-001",
            )
        )

    # --- WAIKE 18 courses + facets ---
    waike_courses = [
        ("DIGITAL_CONFIDENCE", "Digital Confidence to Computer Operator"),
        ("IT_SUPPORT_HARDWARE", "IT Support and Hardware Foundations"),
        ("SOFTWARE_BUILDER", "Software Builder Zero-to-Hero"),
        ("NETWORKING_INFRA", "Networking and Internet Infrastructure"),
        ("CYBER_SOC", "Cybersecurity Foundations and SOC Readiness"),
        ("DATA_DASHBOARDS", "Data, Databases, and Dashboards"),
        ("AI_ML_EDGE", "AI/ML and Edge AI Foundations"),
        ("EMBEDDED_PROTOTYPING", "Embedded Systems and Device Prototyping"),
        ("WIRELESS_6G", "Wireless, DSP, and 6G Foundations"),
        ("PM_AGILE_LSS", "Project Management, Agile, and Lean Six Sigma"),
        ("GAME_DEV_INTERACTIVE", "Game Development and Interactive Media"),
        ("SEVEN_GC_APPRENTICESHIP", "7GC AI-RAN Research Apprenticeship"),
        ("CLOUD_DEVOPS", "Cloud and DevOps"),
        ("COMM_PD_ETHICS", "Communication, Professional Development, and Ethics"),
        ("ROBOTICS_CONTROL", "Robotics and Control"),
        ("GUNNCHOS_PRODUCT_LAB", "gunnchOS Device OS and Product Lab"),
        ("HARDWARE_ENGINEERING", "Hardware Engineering"),
        ("DATA_VIZ_BI", "Data Visualization and Business Intelligence"),
    ]
    waike_facets = [
        "lessons",
        "assignments",
        "labs",
        "live_repo_linked_labs",
        "group_projects",
        "student_packets",
        "instructor_packets",
        "slide_instruction_media",
        "assessment_mastery",
        "portfolio_outputs",
        "live_gunnchai_tutoring",
        "offline_use",
        "device_lab_use",
    ]
    reqs.append(
        row(
            "WAIKE",
            parent=None,
            layer="waike",
            product="waike",
            owner_repo="waike-research-ops",
            description="WAIKE curriculum + app digital depth",
            criteria="18 courses non-templated; facets + first-party app depth.",
            state=OPEN,
            digital_possible=True,
            digital_work="Detect/remediate shallow templated courses; deepen packets.",
            next_packet="PLATFORM-001",
            children_required=True,
        )
    )
    for cid, cname in waike_courses:
        reqs.append(
            open_child(
                f"WAIKE_COURSE_{cid}",
                "WAIKE",
                "waike",
                "waike",
                "waike-research-ops",
                f"WAIKE course: {cname}",
                "Non-templated lessons/labs/assignments with distinct depth evidence.",
                f"Audit and deepen {cname} beyond template.",
                next_packet="PLATFORM-001",
            )
        )
    for facet in waike_facets:
        reqs.append(
            open_child(
                f"WAIKE_FACET_{facet.upper()}",
                "WAIKE",
                "waike",
                "waike",
                "waike-research-ops",
                f"WAIKE facet: {facet}",
                f"Digital acceptance for {facet} across courses.",
                f"Implement {facet} depth.",
                next_packet="PLATFORM-001",
            )
        )
    reqs.append(
        open_child(
            "WAIKE_STUDENT_VALIDATION_PROTOCOL",
            "WAIKE",
            "waike",
            "waike",
            "waike-research-ops",
            "Student validation protocol/instrumentation",
            "Digital protocol + capture hooks before human validation.",
            "Build student validation protocol kits.",
            next_packet="PLATFORM-001",
            reopened=True,
            reopen_reason="Was collapsed into HUMAN_PENDING without digital prep.",
        )
    )
    reqs.append(
        pending_irreducible(
            "WAIKE_STUDENT_VALIDATION_HUMAN",
            "WAIKE",
            "waike",
            "waike",
            "waike-research-ops",
            "Real student validation",
            HUM,
            HUM,
        )
    )
    reqs.append(
        open_child(
            "WAIKE_INSTRUCTOR_VALIDATION_PROTOCOL",
            "WAIKE",
            "waike",
            "waike",
            "waike-research-ops",
            "Instructor validation protocol/instrumentation",
            "Digital instructor review protocol before human signoff.",
            "Build instructor validation protocol kits.",
            next_packet="PLATFORM-001",
        )
    )
    reqs.append(
        pending_irreducible(
            "WAIKE_INSTRUCTOR_VALIDATION_HUMAN",
            "WAIKE",
            "waike",
            "waike",
            "waike-research-ops",
            "Real instructor validation",
            HUM,
            HUM,
        )
    )

    # --- Networking / 5G-A / NTN / 6G ---
    net_items = [
        "ethernet",
        "wifi",
        "bluetooth",
        "cellular_manager",
        "sim_esim_interface",
        "apn",
        "ipv4_ipv6_dns",
        "bearer_policy",
        "failover",
        "handover",
        "qos_qoe",
        "offline_reconnect",
        "terrestrial_modem",
        "future_ntn_abstraction",
        "simulated_ntn",
        "ai_ran",
        "o_ran_adapters",
        "edge_placement",
        "network_digital_twin",
        "imt2030_evaluation_harness",
        "rel20_rel21_tracking",
        "migration_6g_interfaces",
    ]
    reqs.append(
        row(
            "NETWORKING_5G_NTN_6G",
            parent=None,
            layer="networking",
            product="connectivity",
            owner_repo="gunnchos-device-os",
            description="Networking / 5G-A / NTN / 6G migration digital stack",
            criteria="Digital interfaces/harnesses complete; standardized 6G remains STANDARD_PENDING.",
            state=OPEN,
            digital_possible=True,
            digital_work="Build managers, abstractions, sims, and evaluation harnesses.",
            next_packet="NET-001",
            children_required=True,
        )
    )
    for item in net_items:
        reqs.append(
            open_child(
                f"NET_{item.upper()}",
                "NETWORKING_5G_NTN_6G",
                "networking",
                "connectivity",
                "gunnchos-device-os",
                f"Networking: {item}",
                f"Digital acceptance for {item}.",
                f"Implement {item}.",
                next_packet="NET-001",
            )
        )
    reqs.append(
        pending_irreducible(
            "STANDARDIZED_6G",
            "NETWORKING_5G_NTN_6G",
            "networking",
            "connectivity",
            "multi",
            "Standardized 6G claim",
            STD,
            STD,
        )
    )

    # --- Cloud / online ops ---
    cloud_items = [
        "identity_auth",
        "authorization",
        "sessions",
        "health",
        "rate_limit",
        "abuse",
        "moderation",
        "reports",
        "block_mute",
        "audit_logs",
        "metrics",
        "tracing",
        "alerts",
        "slo",
        "backup",
        "restore",
        "dr",
        "migrations",
        "idempotency",
        "degraded_mode",
    ]
    reqs.append(
        row(
            "CLOUD_ONLINE_OPS",
            parent=None,
            layer="cloud",
            product="online_services",
            owner_repo="gunnchos-7gc-ai-ran-field-kit",
            description="Cloud / online operations digital stack",
            criteria="Ops controls implemented and tested digitally.",
            state=OPEN,
            digital_possible=True,
            digital_work="Implement online service ops stack.",
            next_packet="CLOUD-001",
            children_required=True,
        )
    )
    for item in cloud_items:
        reqs.append(
            open_child(
                f"CLOUD_{item.upper()}",
                "CLOUD_ONLINE_OPS",
                "cloud",
                "online_services",
                "gunnchos-7gc-ai-ran-field-kit",
                f"Cloud ops: {item}",
                f"Digital acceptance for {item}.",
                f"Implement {item}.",
                next_packet="CLOUD-001",
            )
        )

    # --- Security / privacy / rights ---
    sec_items = [
        "secure_boot",
        "measured_boot",
        "attestation",
        "updates",
        "sandbox",
        "permissions",
        "secrets",
        "revocation",
        "sbom",
        "hbom",
        "ai_bom",
        "red_team_harness",
        "privacy_controls",
        "export_delete",
        "retention",
        "minor_student_protections",
        "source_dependency_licensing",
        "media_rights_register",
        "ai_model_rights_register",
        "dataset_rights_register",
        "scientific_data_rights_register",
    ]
    reqs.append(
        row(
            "SECURITY_PRIVACY_RIGHTS",
            parent=None,
            layer="security",
            product="ecosystem",
            owner_repo="gunnchos-device-os",
            description="Security/privacy/rights digital controls",
            criteria="Controls + registers complete; external pentest remains EXTERNAL.",
            state=OPEN,
            digital_possible=True,
            digital_work="Implement controls and rights registers.",
            next_packet="SEC-001",
            children_required=True,
        )
    )
    for item in sec_items:
        reqs.append(
            open_child(
                f"SEC_{item.upper()}",
                "SECURITY_PRIVACY_RIGHTS",
                "security",
                "ecosystem",
                "gunnchos-device-os",
                f"Security/privacy: {item}",
                f"Digital acceptance for {item}.",
                f"Implement {item}.",
                next_packet="SEC-001",
            )
        )

    # --- Manufacturing / support / validation prep ---
    mfg_items = [
        "factory_identity",
        "mac",
        "device_cert_interface",
        "esim_interface",
        "calibration_ingest",
        "flash_orchestration",
        "test_ingest",
        "repair_history",
        "rework",
        "secure_wipe",
        "supply_chain_database",
        "lifecycle_eol",
        "rma_workflow",
        "spares",
        "diagnostic_bundle",
        "replacement_transfer",
        "first_use_software",
        "reliability_test_ingest",
        "ergonomics_digital_model",
        "evt_calibration_framework",
        "hil_adapters",
        "battery_measurement_ingest",
        "thermal_measurement_ingest",
        "rf_measurement_ingest",
        "ring_calibration_ingest",
        "external_pentest_package",
        "carrier_acceptance_package",
        "packaging_first_use_software",
    ]
    reqs.append(
        row(
            "MANUFACTURING_SUPPORT_VALIDATION_PREP",
            parent=None,
            layer="manufacturing_support",
            product="ecosystem",
            owner_repo="gunnchos-hardware-industrial-design",
            description="Manufacturing/support/validation digital preparation",
            criteria="All prep tooling digital children complete before PHYSICAL/EXTERNAL acceptance.",
            state=OPEN,
            digital_possible=True,
            digital_work="Build factory/support/validation prep software.",
            next_packet="MFG-001",
            children_required=True,
            reopened=True,
            reopen_reason="Broad PHYSICAL/EXTERNAL rows hid digital prep work.",
        )
    )
    for item in mfg_items:
        reqs.append(
            open_child(
                f"MFG_{item.upper()}",
                "MANUFACTURING_SUPPORT_VALIDATION_PREP",
                "manufacturing_support",
                "ecosystem",
                "gunnchos-hardware-industrial-design",
                f"Manufacturing/support prep: {item}",
                f"Digital acceptance for {item}.",
                f"Implement {item}.",
                next_packet="MFG-001",
                reopened=item
                in {
                    "supply_chain_database",
                    "reliability_test_ingest",
                    "ergonomics_digital_model",
                    "rma_workflow",
                    "spares",
                    "flash_orchestration",
                    "packaging_first_use_software",
                    "evt_calibration_framework",
                    "hil_adapters",
                    "battery_measurement_ingest",
                    "thermal_measurement_ingest",
                    "rf_measurement_ingest",
                    "ring_calibration_ingest",
                    "external_pentest_package",
                    "carrier_acceptance_package",
                },
                reopen_reason="Split from false pending classification"
                if item
                in {
                    "supply_chain_database",
                    "reliability_test_ingest",
                    "ergonomics_digital_model",
                    "rma_workflow",
                    "spares",
                    "flash_orchestration",
                    "packaging_first_use_software",
                    "evt_calibration_framework",
                    "hil_adapters",
                    "battery_measurement_ingest",
                    "thermal_measurement_ingest",
                    "rf_measurement_ingest",
                    "ring_calibration_ingest",
                    "external_pentest_package",
                    "carrier_acceptance_package",
                }
                else None,
            )
        )

    # Explicit misclassified reopen splits (digital OPEN + irreducible pending)
    splits = [
        (
            "SUPPLY_CHAIN_LIFECYCLE",
            "SUPPLY_CHAIN_DIGITAL_DATABASE",
            "SUPPLY_CHAIN_VENDOR_EXECUTION",
            EXT,
            "Supply-chain digital database/lifecycle tooling",
            "Vendor RFQ/purchase/fab execution",
        ),
        (
            "RELIABILITY_ENVIRONMENTAL_TESTS",
            "RELIABILITY_TEST_INGEST_SOFTWARE",
            "RELIABILITY_PHYSICAL_CHAMBER_EXECUTION",
            PHY,
            "Reliability test plans + ingest automation",
            "Physical environmental chamber execution",
        ),
        (
            "ERGONOMICS_HUMAN_FACTORS",
            "ERGONOMICS_DIGITAL_MODEL",
            "ERGONOMICS_HUMAN_VALIDATION",
            HUM,
            "Ergonomics digital model + protocol",
            "Human factors validation",
        ),
        (
            "WARRANTY_RMA_REPAIR_SPARES",
            "RMA_SPARES_WORKFLOW_SOFTWARE",
            "RMA_SPARES_OPERATIONS_EXTERNAL",
            EXT,
            "RMA/spares/repair workflow software",
            "External ops execution",
        ),
        (
            "FACTORY_PROVISIONING",
            "FACTORY_PROVISIONING_SOFTWARE",
            "FACTORY_PROVISIONING_PHYSICAL_LINE",
            PHY,
            "Factory provisioning orchestration software",
            "Physical factory line execution",
        ),
        (
            "PACKAGING_FIRST_USE_RECYCLING",
            "PACKAGING_FIRST_USE_SOFTWARE",
            "PACKAGING_PHYSICAL_RECYCLING",
            PHY,
            "First-use software + packaging digital assets",
            "Physical packaging/recycling",
        ),
        (
            "EVT_CALIBRATION",
            "EVT_CALIBRATION_FRAMEWORK",
            "EVT_CALIBRATION_PHYSICAL",
            PHY,
            "EVT calibration framework software",
            "Physical EVT calibration",
        ),
        (
            "HIL_CORRELATION",
            "HIL_ADAPTERS_SOFTWARE",
            "HIL_PHYSICAL_CORRELATION",
            PHY,
            "HIL adapter/software correlation harness",
            "Physical HIL correlation",
        ),
        (
            "BATTERY_THERMAL_RF",
            "BATTERY_THERMAL_RF_MEASUREMENT_INGEST",
            "BATTERY_THERMAL_RF_PHYSICAL_MEASUREMENT",
            PHY,
            "Battery/thermal/RF measurement ingest software",
            "Physical battery/thermal/RF measurement",
        ),
        (
            "RING_SPATIAL_PHYSICAL",
            "RING_CALIBRATION_INGEST_SOFTWARE",
            "RING_SPATIAL_PHYSICAL_VALIDATION",
            PHY,
            "Ring calibration ingest + spatial digital stack",
            "Physical Ring spatial validation",
        ),
        (
            "EXTERNAL_PENTEST",
            "EXTERNAL_PENTEST_READINESS_PACKAGE",
            "EXTERNAL_PENTEST_EXECUTION",
            EXT,
            "External pentest readiness package",
            "External pentest execution",
        ),
        (
            "CARRIER_APPROVAL",
            "CARRIER_ACCEPTANCE_PACKAGE",
            "CARRIER_APPROVAL_EXECUTION",
            EXT,
            "Carrier acceptance digital package",
            "Carrier approval execution",
        ),
        (
            "PRIVACY_DATA_GOVERNANCE",
            "PRIVACY_CONTROLS_DIGITAL",
            "PRIVACY_LEGAL_HUMAN_SIGN OFF",
            HUM,
            "Privacy controls + export/delete/retention digital",
            "Legal/human governance signoff",
        ),
        (
            "LICENSING_IP_MEDIA_MODEL_DATA_RIGHTS",
            "RIGHTS_REGISTERS_DIGITAL",
            "RIGHTS_EXTERNAL_CLEARANCE",
            EXT,
            "Licensing/IP/media/model/data rights registers",
            "External clearance/licensing execution",
        ),
    ]
    for old, dig, pend, pend_state, dig_desc, pend_desc in splits:
        securityish = dig in {
            "PRIVACY_CONTROLS_DIGITAL",
            "RIGHTS_REGISTERS_DIGITAL",
            "EXTERNAL_PENTEST_READINESS_PACKAGE",
        }
        parent = "SECURITY_PRIVACY_RIGHTS" if securityish else "MANUFACTURING_SUPPORT_VALIDATION_PREP"
        layer = "security" if securityish else "manufacturing_support"
        owner = (
            "gunnchos-7gc-ai-ran-field-kit"
            if securityish
            else "gunnchos-hardware-industrial-design"
        )
        reqs.append(
            open_child(
                dig,
                parent,
                layer,
                "ecosystem",
                owner,
                dig_desc,
                f"Digital prep complete for former coarse row {old}.",
                f"Complete digital prep previously hidden by {old}.",
                next_packet="SEC-001" if securityish else "MFG-001",
                reopened=True,
                reopen_reason=f"Reopened from false pending classification of {old}.",
            )
        )
        reqs.append(
            pending_irreducible(
                pend,
                dig,
                layer,
                "ecosystem",
                "multi",
                pend_desc,
                pend_state,
                pend_state,
                reopened=True,
                reopen_reason=f"Split irreducible acceptance from {old}.",
            )
        )

    # Owner decisions preserved
    for rid, desc in [
        ("PROFILE_FRONT_DOOR", "GitHub profile front door (frozen)"),
        ("QUOTE_BACKED_ECONOMICS", "Quote-backed economics"),
        ("PRODUCT_CHARTER_APPROVAL", "Product charter owner approval"),
        ("RFQ_SEND", "RFQ send authorization"),
        ("FAB_RELEASE_AUTHORIZATION", "Fab release authorization"),
    ]:
        reqs.append(
            pending_irreducible(
                rid,
                None,
                "charter_control_plane",
                "ecosystem",
                "gunnchos-7gc-ai-ran-field-kit",
                desc,
                OWN,
                OWN,
            )
        )

    # Certifications standard pending (with digital package prep sibling)
    reqs.append(
        open_child(
            "CERTIFICATIONS_READINESS_PACKAGE",
            "SECURITY_PRIVACY_RIGHTS",
            "security",
            "ecosystem",
            "gunnchos-7gc-ai-ran-field-kit",
            "Certifications readiness package",
            "Digital certification evidence package prepared.",
            "Assemble certification readiness artifacts.",
            next_packet="SEC-001",
            reopened=True,
            reopen_reason="STANDARD_PENDING hid digital readiness package work.",
        )
    )
    reqs.append(
        pending_irreducible(
            "CERTIFICATIONS",
            "CERTIFICATIONS_READINESS_PACKAGE",
            "security",
            "ecosystem",
            "multi",
            "Actual certifications",
            STD,
            STD,
        )
    )

    # dedupe by requirement_id (keep first)
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for r in reqs:
        if r["requirement_id"] in seen:
            continue
        seen.add(r["requirement_id"])
        unique.append(r)
    reqs = unique

    open_count = sum(1 for r in reqs if r["engineering_state"] == OPEN)
    counts: dict[str, int] = {}
    for r in reqs:
        counts[r["engineering_state"]] = counts.get(r["engineering_state"], 0) + 1

    return {
        "schema": "gunnchos.charter_exhaustion.engineering_requirement_register.v2",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "policy": {
            "CURSOR_NEVER_MERGES": True,
            "PROFILE_README_EDIT_FREEZE": "ACTIVE",
            "GENERIC_README_PROGRAM": "PAUSED",
            "WP001_START": "DO_NOT_START",
            "WP001_READY_FOR_OWNER_DECISION": False,
            "MAX_MAJOR_ACTIVE_STREAMS": 3,
            "FIELD_KIT_71_MERGE_RECOMMEND": False,
        },
        "accepted_main_verification": {
            "anime-aggressors": {
                "sha": SHA["anime-aggressors"],
                "pr_merged": 72,
                "tip_merged": "a320c7c7edf0f6d60f27833a6488fcee8038b3e0",
                "verified": True,
                "independent_verifier": "PASS",
                "vp_land_pr": 73,
            },
            "gunnchos-device-os": {
                "sha": SHA["gunnchos-device-os"],
                "pr_merged": 104,
                "tip_merged": "e05d3edb82a978a6e4d6e1481ba20d0d53305b94",
                "verified": True,
                "independent_verifier": "PASS",
                "vp_land_pr": 105,
            },
            "gunnchos-hardware-industrial-design": {
                "sha": SHA["gunnchos-hardware-industrial-design"],
                "pr_merged": 60,
                "tip_merged": "82dbbc2d87eb544675b33b0d99b1795712b7d54d",
                "verified": True,
                "independent_verifier": "AUDIT_ACCEPTANCE_PASS",
                "HW_FIRMWARE_DIGITAL_PACKAGE_COMPLETE": False,
                "vp_land_pr": 61,
            },
            "pedestrian-pursuit": {"sha": SHA["pedestrian-pursuit"], "verified": True},
            "archive-of-life-artifact-world": {
                "sha": SHA["archive-of-life-artifact-world"],
                "verified": True,
            },
            "beatlink-party": {"sha": SHA["beatlink-party"], "verified": True},
            "gunnchos-7gc-ai-ran-field-kit": {
                "sha": SHA["gunnchos-7gc-ai-ran-field-kit"],
                "verified": True,
                "note": "#71 DRAFT aggregation LAST; do not merge yet",
            },
            "waike-research-ops": {"sha": SHA["waike-research-ops"], "verified": True},
            "gunnchAI3k": {"sha": SHA["gunnchAI3k"], "verified": True},
        },
        "prior_broad_audit": {
            "DIGITAL_IMPLEMENTATION_OPEN": 13,
            "note": "Coarse V1 audit; not authoritative after V2 atomic decomposition",
        },
        "ATOMIC_DIGITAL_IMPLEMENTATION_OPEN": open_count,
        "summary_counts": counts,
        "misclassified_rows_reopened": MISCLASSIFIED_REOPENED,
        "next_three_packets": [
            "GAME-001 Anime fighter/product depth (Ember Vale…Vesper Nyx differentiation)",
            "PLATFORM-001 Creator/WAIKE/gunnchAI first-party app depth on device-os main 3858e76",
            "HW-002 Handheld image-slot fit + Ring Zephyr west + one high-risk EDA closure",
        ],
        "edmund_merge_order": [
            "Phase A merged: anime#72 @16df36d, device-os#104 @3858e76, hardware#60 @4ba876d",
            "VP land DRAFTs: anime#73, hardware#61, device-os#105 — owner merge optional evidence land",
            "device-os#103 HOLD until Lab reconciliation on accepted mains",
            "field-kit#71 LAST — DO NOT MERGE YET (V2 register work allowed on DRAFT)",
        ],
        "claim_firewall": {
            "PHYSICAL_PRODUCT_VALIDATED": False,
            "HUMAN_VALIDATED": False,
            "EXTERNAL_PENTEST_COMPLETE": False,
            "CERTIFIED": False,
            "CARRIER_ACCEPTED": False,
            "STANDARDIZED_6G": False,
            "SHIPPING_IMAGE_RELEASED": False,
            "PRODUCTION_RELEASE_CLAIMED": False,
            "RFQ_SENT": False,
            "PURCHASE_AUTHORIZED": False,
            "FAB_RELEASE_AUTHORIZED": False,
            "WP001_READY_FOR_OWNER_DECISION": False,
            "PRODUCT_CHARTER_DIGITAL_ENGINEERING_EXHAUSTED": False,
            "HW_FIRMWARE_DIGITAL_PACKAGE_COMPLETE": False,
            "FIELD_KIT_71_MERGE_RECOMMEND": False,
        },
        "forbidden_branch_shas_as_accepted_main": sorted(FORBIDDEN_BRANCH_AS_MAIN),
        "requirements": reqs,
    }


def main() -> None:
    doc = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"requirements={len(doc['requirements'])}")
    print(f"ATOMIC_DIGITAL_IMPLEMENTATION_OPEN={doc['ATOMIC_DIGITAL_IMPLEMENTATION_OPEN']}")
    print(f"summary_counts={doc['summary_counts']}")


if __name__ == "__main__":
    main()
