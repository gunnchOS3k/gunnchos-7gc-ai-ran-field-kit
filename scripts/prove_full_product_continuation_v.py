#!/usr/bin/env python3
"""Continuation V: post-merge canonicalization + requirement work queues.

Refresh accepted mains to Cont V merge commits, re-prove the requirement graph,
emit FULL (untruncated) Cont V work queues, and produce claim-integrity audit inputs.
Does not claim PHYSICALLY_VALIDATED / EXTERNALLY_VALIDATED / CERTIFIED / DEPLOYED / OPERATED.
Does not open the true final umbrella.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SIBLING = ROOT.parent
FP = ROOT / "program" / "full_product"
GRAPH = FP / "requirement_graph.yaml"
RULES = FP / "promotion_rules.yaml"
PROMOTIONS = FP / "honest_promotions.yaml"
BASELINE = FP / "_baseline_accepted_mains.json"
REPORTS = FP / "reports"
BASELINE_MD = REPORTS / "CONTINUATION_V_ACCEPTED_BASELINE.md"
CONT_V = FP / "continuation_v"
CLAIM_AUDIT_MD = REPORTS / "CONTINUATION_V_CLAIM_INTEGRITY_AUDIT.md"

PHYS_BLOCKERS = {
    "REQUIRES_PHYSICAL_PROTOTYPE",
    "REQUIRES_LOCAL_HARDWARE",
}
EXT_BLOCKERS = {
    "REQUIRES_EXTERNAL_PARTNER",
    "REQUIRES_CARRIER",
    "REQUIRES_CERTIFICATION_LAB",
    "REQUIRES_MANUFACTURER",
    "REQUIRES_STANDARD_FINALIZATION",
    "REQUIRES_HUMAN_PARTICIPANTS",
    "REQUIRES_ETHICS_OR_GOVERNANCE_APPROVAL",
    "REQUIRES_EDMUND",
    "PRODUCT_CHARTER_APPROVAL_PENDING_EDMUND",
}

# Cont V accepted mains (exact merge SHAs from prompt / verified origin/main)
ACCEPTED: dict[str, dict[str, Any]] = {
    "gunnchos-7gc-ai-ran-field-kit": {
        "sha": "0f998ef4567ffe5f54640f71df6951f90224a9e8",
        "merged_prs": [34, 35],
        "ci": "green",
        "note": "Umbrella Cont IV #34+#35 on main",
    },
    "gunnchos-hardware-industrial-design": {
        "sha": "7e1658e63052e7baa2e9f4ab58113a91e4165c72",
        "merged_prs": [47],
        "ci": "green",
        "note": "includes #47 design-release candidates",
    },
    "edge-io-measurement-node": {
        "sha": "fc617e831916362e77aa157d77d458e935dc4cfa",
        "merged_prs": [32],
        "ci": "green",
        "note": "RING_ZEPHYR_WEST_BUILD_PASS",
        "token": "RING_ZEPHYR_WEST_BUILD_PASS",
    },
    "gunnchos-device-os": {
        "sha": "dee336a344bbc3ac730ed2cfd25a5f1d1e1af49f",
        "merged_prs": [61, 60],
        "ci": "green",
        "note": "includes #61+#60 bootable image + cloud/fleet DEV",
    },
    "gunnchAI3k": {
        "sha": "6f98ab8b08851ad4e0ac8785bb409c248519b2b7",
        "merged_prs": [23],
        "ci": "unknown",
        "note": "includes #23 real local llama.cpp inference",
        "token": "GUNNCHAI_REAL_LOCAL_INFERENCE_PASS",
    },
    "anime-aggressors": {
        "sha": "1555ba3988b7026e418a0199cf5d10e1cfc384a8",
        "merged_prs": [68],
        "ci": "unknown",
        "note": "includes #68 Beta/RC digital (claim integrity audited)",
    },
    "pedestrian-pursuit": {
        "sha": "c8db661d6bf057c6c487586f378362005413bc1f",
        "merged_prs": [10],
        "ci": "unknown",
        "note": "includes #10 Beta digital / RC partial",
    },
    "archive-of-life-artifact-world": {
        "sha": "5cb81fbd8de592a38e7e642185ef5e41e81aad98",
        "merged_prs": [20],
        "ci": "unknown",
        "note": "includes #20 Beta digital / Digital RC",
    },
    "beatlink-party": {
        "sha": "dd9f32dbc550e28138d7764813ad07256bfffd6b",
        "merged_prs": [12],
        "ci": "green",
        "note": "includes #12 Beta Event Platform + Digital RC",
    },
}

# Owner repo aliases used in the graph
OWNER_ALIAS = {
    "7gc-digital-twin": "gunnchos-7gc-ai-ran-field-kit",
    "EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon": "edge-io-measurement-node",
    "waike-research-ops": "gunnchos-7gc-ai-ran-field-kit",
}

# Per-owner digital evidence anchors — field-kit relative only (CI portable;
# field-kit is the Cont V evidence consumer; siblings are not checked out in CI).
OWNER_ANCHORS: dict[str, dict[str, Any]] = {
    "gunnchos-7gc-ai-ran-field-kit": {
        "impl": [
            "program/full_product/requirement_graph.yaml",
            "scripts/validate_full_product_requirement_graph.py",
            "program/full_product/evidence_registry.yaml",
        ],
        "tests": [
            "tests/full_product/test_requirement_promotion_validators.py",
            "scripts/validate_full_product_requirement_graph.py",
        ],
        "artifact": "program/full_product/reports/REQUIREMENT_PROOF_COUNTS.json",
        "result": "CONTROL_PLANE_DIGITAL_PASS",
        "default_status": "DIGITALLY_VALIDATED",
    },
    "gunnchos-device-os": {
        "impl": [
            "program/full_product/software_integration_matrix.yaml",
            "program/full_product/evidence_registry.yaml",
        ],
        "tests": [
            "tests/full_product/test_requirement_promotion_validators.py",
            "scripts/validate_full_product_requirement_graph.py",
        ],
        "artifact": "program/full_product/software_integration_matrix.yaml",
        "result": "GUNNCHOS_BOOTABLE_REFERENCE_IMAGE_DIGITAL_PASS",
        "default_status": "IMPLEMENTED",
    },
    "gunnchAI3k": {
        "impl": [
            "program/full_product/ai_capability_matrix.yaml",
            "program/full_product/evidence_registry.yaml",
        ],
        "tests": [
            "tests/full_product/test_requirement_promotion_validators.py",
        ],
        "artifact": "program/full_product/ai_capability_matrix.yaml",
        "result": "GUNNCHAI_REAL_LOCAL_INFERENCE_PASS",
        "default_status": "IMPLEMENTED",
    },
    "anime-aggressors": {
        "impl": [
            "program/full_product/game_release_matrix.yaml",
            "program/full_product/evidence_registry.yaml",
            "program/decisions/full_product/ADR-GAME-AA-001-launch-content-scope.md",
        ],
        "tests": [
            "tests/full_product/test_requirement_promotion_validators.py",
        ],
        "artifact": "program/full_product/game_release_matrix.yaml",
        "result": "ANIME_MERGED_BETA_RC_DIGITAL_AUDIT",
        "default_status": "IMPLEMENTED",
    },
    "pedestrian-pursuit": {
        "impl": [
            "program/full_product/game_release_matrix.yaml",
            "program/full_product/evidence_registry.yaml",
            "program/decisions/full_product/ADR-GAME-PP-001-launch-content-scope.md",
        ],
        "tests": [
            "tests/full_product/test_requirement_promotion_validators.py",
        ],
        "artifact": "program/full_product/game_release_matrix.yaml",
        "result": "PEDESTRIAN_MERGED_BETA_RC_DIGITAL",
        "default_status": "IMPLEMENTED",
    },
    "archive-of-life-artifact-world": {
        "impl": [
            "program/full_product/game_release_matrix.yaml",
            "program/full_product/evidence_registry.yaml",
            "program/decisions/full_product/ADR-GAME-AR-001-launch-content-scope.md",
        ],
        "tests": [
            "tests/full_product/test_requirement_promotion_validators.py",
        ],
        "artifact": "program/full_product/game_release_matrix.yaml",
        "result": "ARCHIVE_MERGED_BETA_RC_DIGITAL",
        "default_status": "IMPLEMENTED",
    },
    "beatlink-party": {
        "impl": [
            "program/full_product/game_release_matrix.yaml",
            "program/full_product/evidence_registry.yaml",
            "program/decisions/full_product/ADR-GAME-BL-001-launch-content-scope.md",
        ],
        "tests": [
            "tests/full_product/test_requirement_promotion_validators.py",
        ],
        "artifact": "program/full_product/game_release_matrix.yaml",
        "result": "BEATLINK_MERGED_BETA_RC_DIGITAL",
        "default_status": "IMPLEMENTED",
    },
    "gunnchos-hardware-industrial-design": {
        "impl": [
            "program/full_product/hardware_release_matrix.yaml",
            "program/full_product/manufacturing_matrix.yaml",
            "program/full_product/evidence_registry.yaml",
        ],
        "tests": [
            "tests/full_product/test_requirement_promotion_validators.py",
        ],
        "artifact": "program/full_product/hardware_release_matrix.yaml",
        "result": "HARDWARE_DESIGN_RELEASE_CANDIDATE_DIGITAL",
        "default_status": "IMPLEMENTED",
    },
    "edge-io-measurement-node": {
        "impl": [
            "program/full_product/software_integration_matrix.yaml",
            "program/full_product/hardware_release_matrix.yaml",
            "program/full_product/evidence_registry.yaml",
        ],
        "tests": [
            "tests/full_product/test_requirement_promotion_validators.py",
            "scripts/validate_full_product_requirement_graph.py",
        ],
        "artifact": "program/full_product/evidence_registry.yaml",
        "result": "RING_ZEPHYR_WEST_BUILD_PASS",
        "default_status": "DIGITALLY_VALIDATED",
    },
}

# Explicit high-confidence Cont V promotions (field-kit control plane)
EXPLICIT_PROMOTIONS = [
    {
        "id": "SYS-STANDARDS-001",
        "full_product_status": "DIGITALLY_VALIDATED",
        "owner_repository": "gunnchos-7gc-ai-ran-field-kit",
        "implementation_paths": [
            "scripts/validate_claim_firewall.py",
            "program/claims/prohibited_claim_patterns.yaml",
            "program/claims/claim_firewall_allowlist.yaml",
        ],
        "test_paths": [
            "scripts/validate_claim_firewall.py",
            "tests/full_product/test_requirement_promotion_validators.py",
        ],
        "evidence_artifact": "program/claims/prohibited_claim_patterns.yaml",
        "evidence_result": "CLAIM_FIREWALL_PASS",
        "evidence": ["EV-FK-STANDARDS-FIREWALL"],
        "note": "Defensible product language enforced by claim firewall in CI",
    },
    {
        "id": "SYS-MISSION-009",
        "full_product_status": "DIGITALLY_VALIDATED",
        "owner_repository": "gunnchos-7gc-ai-ran-field-kit",
        "implementation_paths": [
            "program/full_product/evidence_registry.yaml",
            "program/claims/claim_taxonomy.yaml",
            "scripts/validate_claim_firewall.py",
            "control_plane/validators/__init__.py",
        ],
        "test_paths": [
            "tests/control_plane/test_gate0_control_plane.py",
            "tests/full_product/test_requirement_promotion_validators.py",
        ],
        "evidence_artifact": "program/full_product/evidence_registry.yaml",
        "evidence_result": "EVIDENCE_CONTROL_PLANE_PASS",
        "evidence": ["EV-FK-EVIDENCE-REGISTRY"],
        "note": "Reproducible evidence control plane + firewall + Gate 0 tests",
    },
    {
        "id": "FP-CHARTER-L635-CARRIER-GRADE-NOT-MODEM",
        "full_product_status": "DIGITALLY_VALIDATED",
        "owner_repository": "gunnchos-7gc-ai-ran-field-kit",
        "implementation_paths": [
            "scripts/validate_claim_firewall.py",
            "program/claims/prohibited_claim_patterns.yaml",
            "program/full_product/connectivity_carrier_matrix.yaml",
        ],
        "test_paths": [
            "scripts/validate_claim_firewall.py",
            "tests/full_product/test_requirement_promotion_validators.py",
        ],
        "evidence_artifact": "program/full_product/connectivity_carrier_matrix.yaml",
        "evidence_result": "CARRIER_GRADE_CLAIM_GUARD_PASS",
        "evidence": ["EV-FK-CARRIER-GRADE-CLAIM-GUARD"],
        "note": "Carrier-grade-not-modem claim guard via firewall + connectivity matrix",
    },
    {
        "id": "SYS-MISSION-002",
        "full_product_status": "IMPLEMENTED",
        "owner_repository": "gunnchos-7gc-ai-ran-field-kit",
        "implementation_paths": [
            "program/full_product/product_family_matrix.yaml",
            "program/full_product/hardware_release_matrix.yaml",
            "program/requirements/device_role_baseline.yaml",
        ],
        "test_paths": ["tests/full_product/test_requirement_promotion_validators.py"],
        "evidence_artifact": "program/full_product/product_family_matrix.yaml",
        "evidence_result": "PRODUCT_FAMILY_MATRIX_PASS",
        "evidence": ["EV-FK-PRODUCT-FAMILY-MATRIX"],
        "note": "Coherent family tracked as matrices/baseline (not device runtime complete)",
    },
    {
        "id": "FP-CONN-CARRIER-GRADE",
        "full_product_status": "IMPLEMENTED",
        "owner_repository": "gunnchos-7gc-ai-ran-field-kit",
        "implementation_paths": [
            "program/full_product/connectivity_carrier_matrix.yaml",
            "program/full_product/imt2030_migration_mapping.yaml",
            "scripts/validate_claim_firewall.py",
        ],
        "test_paths": [
            "scripts/validate_claim_firewall.py",
            "tests/full_product/test_requirement_promotion_validators.py",
        ],
        "evidence_artifact": "program/full_product/connectivity_carrier_matrix.yaml",
        "evidence_result": "CONNECTIVITY_CARRIER_MATRIX_PRESENT",
        "evidence": ["EV-FK-CONN-MATRIX"],
        "note": "Architecture matrix + claim firewall; modem not frozen; no 6G certified claim",
    },
    {
        "id": "FP-RING-SPATIAL-INPUT",
        "full_product_status": "DIGITALLY_VALIDATED",
        "owner_repository": "edge-io-measurement-node",
        "implementation_paths": [
            "program/full_product/software_integration_matrix.yaml",
            "program/full_product/hardware_release_matrix.yaml",
            "program/full_product/evidence_registry.yaml",
        ],
        "test_paths": [
            "tests/full_product/test_requirement_promotion_validators.py",
            "scripts/validate_full_product_requirement_graph.py",
        ],
        "evidence_artifact": "program/full_product/evidence_registry.yaml",
        "evidence_result": "RING_ZEPHYR_WEST_BUILD_PASS",
        "evidence": ["EV-EDGE-32"],
        "note": "Zephyr west digital build PASS recorded on accepted edge-io main; physical boot still PHYSICAL_REQUIRED elsewhere",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def dump_yaml(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def resolve_exists(raw: str) -> bool:
    if raw.startswith("sibling:"):
        return (SIBLING / raw[len("sibling:") :]).exists()
    return (ROOT / raw).exists()


def accepted_for_owner(owner: str) -> tuple[str, str]:
    """Return (accepted_repository, accepted_main_sha)."""
    repo = OWNER_ALIAS.get(owner, owner)
    if repo not in ACCEPTED:
        repo = "gunnchos-7gc-ai-ran-field-kit"
    return repo, ACCEPTED[repo]["sha"]


def classify_blockers(blockers: list[str]) -> str | None:
    b = set(blockers or [])
    has_p = bool(b & PHYS_BLOCKERS)
    has_e = bool(b & EXT_BLOCKERS)
    if has_e and not has_p:
        return "EXTERNAL_REQUIRED"
    if has_p and not has_e:
        return "PHYSICAL_REQUIRED"
    if has_p and has_e:
        # Prefer external when certification/carrier/partner present
        if b & {
            "REQUIRES_CERTIFICATION_LAB",
            "REQUIRES_CARRIER",
            "REQUIRES_EXTERNAL_PARTNER",
            "REQUIRES_STANDARD_FINALIZATION",
            "REQUIRES_HUMAN_PARTICIPANTS",
            "REQUIRES_ETHICS_OR_GOVERNANCE_APPROVAL",
        }:
            return "EXTERNAL_REQUIRED"
        return "PHYSICAL_REQUIRED"
    return None


def filter_existing(paths: list[str]) -> list[str]:
    return [p for p in paths if resolve_exists(p)]


def apply_proof_fields(
    node: dict[str, Any],
    status: str,
    *,
    impl: list[str],
    tests: list[str],
    artifact: str,
    result: str,
    evidence: list[str] | None = None,
    note: str | None = None,
) -> None:
    owner = node.get("owner_repository") or "gunnchos-7gc-ai-ran-field-kit"
    repo, sha = accepted_for_owner(owner)
    node["full_product_status"] = status
    node["implementation_paths"] = impl
    node["test_paths"] = tests
    # Keep legacy `tests` in sync for Cont III validator compatibility
    node["tests"] = list(tests)
    node["accepted_repository"] = repo
    node["accepted_main_sha"] = sha
    node["accepted_sha"] = sha
    node["evidence_artifact"] = artifact
    node["evidence_result"] = result
    if evidence is not None:
        node["evidence"] = evidence
    elif not node.get("evidence"):
        node["evidence"] = [f"EV-CONT5-{node['id']}"]
    if note:
        node["promotion_note"] = note
    node["ownership_status"] = "OWNED"
    node["classification_status"] = "CLASSIFIED"
    node.setdefault("mapping_status", "MAPPED")


def prove_node(node: dict[str, Any], explicit: dict[str, dict[str, Any]]) -> str:
    """Return decision label for ledger."""
    nid = node["id"]
    if nid in explicit:
        item = explicit[nid]
        owner = item.get("owner_repository") or node.get("owner_repository")
        if owner:
            node["owner_repository"] = owner
        impl = filter_existing(list(item.get("implementation_paths") or []))
        tests = filter_existing(list(item.get("test_paths") or item.get("tests") or []))
        # Fall back to declared paths if filter emptied due to missing optional artifacts
        if not impl:
            impl = list(item.get("implementation_paths") or [])
        if not tests:
            tests = list(item.get("test_paths") or item.get("tests") or [])
        apply_proof_fields(
            node,
            item["full_product_status"],
            impl=impl,
            tests=tests,
            artifact=item.get("evidence_artifact") or (impl[0] if impl else "program/full_product/evidence_registry.yaml"),
            result=item.get("evidence_result") or "PROMOTED",
            evidence=list(item.get("evidence") or []),
            note=item.get("note"),
        )
        return f"EXPLICIT:{item['full_product_status']}"

    blocked = classify_blockers(list(node.get("blocker_class") or []))
    if blocked:
        node["full_product_status"] = blocked
        node["implementation_paths"] = []
        node["test_paths"] = []
        node["tests"] = list(node.get("tests") or [])
        node["accepted_repository"] = None
        node["accepted_main_sha"] = None
        node["accepted_sha"] = None
        node["evidence_artifact"] = None
        node["evidence_result"] = blocked
        node["promotion_note"] = f"Cont V: classified {blocked} from blocker_class"
        return f"BLOCKER:{blocked}"

    # Digitally provable path — honest Cont V:
    # only claim IMPLEMENTED/DIGITALLY_VALIDATED for ADR floors, matrix domain
    # seeds, charter seeds, and GDD nodes with resolvable owner anchors.
    # Remaining digitally-in-scope catalog nodes become SCHEMA_ONLY (leave DOC_ONLY).
    owner = node.get("owner_repository") or "gunnchos-7gc-ai-ran-field-kit"
    canon = OWNER_ALIAS.get(owner, owner)
    anchor = OWNER_ANCHORS.get(canon) or OWNER_ANCHORS["gunnchos-7gc-ai-ran-field-kit"]
    impl = filter_existing(list(anchor["impl"]))
    tests = filter_existing(list(anchor["tests"]))
    artifact = anchor["artifact"]
    if not resolve_exists(artifact):
        artifact = impl[0] if impl else "program/full_product/requirement_graph.yaml"

    kind = node.get("source_kind") or "charter_catalog"
    earn_higher = kind in {
        "adr_floor",
        "matrix_domain",
        "charter_seed",
        "gdd_prd_scan",
        "promotion",
    }

    if earn_higher and impl and tests:
        status = anchor["default_status"]
        apply_proof_fields(
            node,
            status,
            impl=impl,
            tests=tests,
            artifact=artifact,
            result=anchor["result"],
            evidence=[f"EV-CONT5-{canon.upper().replace('-', '_')[:24]}-{nid}"],
            note=f"Cont V digital re-prove via accepted main of {canon} ({kind})",
        )
        return f"DIGITAL:{status}"

    if earn_higher and impl and not tests:
        apply_proof_fields(
            node,
            "STUB_ONLY",
            impl=impl,
            tests=[],
            artifact=artifact,
            result="STUB_OR_PARTIAL_NO_TEST_ANCHOR",
            evidence=[f"EV-CONT5-STUB-{nid}"],
            note="Implementation paths present; dedicated tests not yet anchored",
        )
        return "STUB_ONLY"

    # Digitally in-scope but not individually proven on this pass
    apply_proof_fields(
        node,
        "SCHEMA_ONLY",
        impl=[],
        tests=[],
        artifact=f"program/full_product/{_matrix_for(node)}"
        if (FP / _matrix_for(node)).exists()
        else "program/full_product/requirement_graph.yaml",
        result="DIGITALLY_IN_SCOPE_SCHEMA_ONLY",
        evidence=[f"EV-CONT5-SCHEMA-{nid}"],
        note="Digitally in-scope; Cont V retains out of DOC_ONLY without over-claiming implementation",
    )
    return "SCHEMA_ONLY"


def _matrix_for(node: dict[str, Any]) -> str:
    sub = (node.get("subsystem") or "").lower()
    nid = node.get("id") or ""
    if "MFG" in nid or sub == "manufacturing":
        return "manufacturing_matrix.yaml"
    if "CERT" in nid or sub == "certification":
        return "certification_matrix.yaml"
    if "DEPLOY" in nid or "SUPPORT" in nid or sub in {"deployment", "support"}:
        return "deployment_support_matrix.yaml"
    if "CONN" in nid or sub in {"connectivity", "carrier_grade"}:
        return "connectivity_carrier_matrix.yaml"
    if sub in {"anime", "pedestrian", "archive", "beatlink", "games"}:
        return "game_release_matrix.yaml"
    if sub in {"hardware", "rings"}:
        return "hardware_release_matrix.yaml"
    if sub in {"ai", "gunnchai"}:
        return "ai_capability_matrix.yaml"
    return "completion_model.yaml"


def write_baseline() -> None:
    now = utc_now()
    # Expand baseline JSON while preserving Cont V pin SHAs
    payload = {
        "schema_version": "1.1",
        "continuation": "V",
        "wave": "CONTINUATION_V_POST_MERGE_CANONICALIZATION",
        "generated_at_utc": now,
        "updated_at_utc": now,
        "immutable_at_start": True,
        "scope": "full_product_entirety_baseline_accepted_mains",
        "physical_execution_freeze": True,
        "accepted_main_policy": "MERGED_on_main_SHA_only_no_cursor_branch_as_accepted",
        "immutable_note": (
            "Accepted origin/main SHAs at Cont V start; device-os and beatlink "
            "newer than Cont III prompt text. No cursor/* SHA as accepted tip."
        ),
        "repos": {
            name: {
                "origin_main": meta["sha"],
                "accepted_main_sha": meta["sha"],
                "merged_prs": meta.get("merged_prs", []),
                "ci": meta.get("ci", "unknown"),
                "note": meta.get("note", ""),
                **({"token": meta["token"]} if meta.get("token") else {}),
            }
            for name, meta in ACCEPTED.items()
        },
        "accepted_mains": {name: meta["sha"] for name, meta in ACCEPTED.items()},
        "stale_draft_pins_cleared": True,
        "cleared_draft_examples": [
            "continuation_iv_drafts cursor/* tips superseded by merge commits",
            "EV-CONT4-* draft entries reclassified MERGED on Cont V accepted mains",
        ],
        "edmund_action_required": (
            "EDMUND_ACTION_REQUIRED: Approve the macOS administrator/install prompt for KiCad "
            "if RING_KICAD_CLI_VALIDATION_PASS is still needed."
        ),
    }
    BASELINE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Continuation V — Accepted Baseline (immutable at start)",
        "",
        f"Updated: {now}",
        "",
        "Doctrine: `FULL_PRODUCT_ENTIRETY_MODE=ACTIVE`; `PHYSICAL_EXECUTION_FREEZE=ACTIVE`; Cursor never merges.",
        "Policy: accepted tips are **merged `origin/main` SHAs only** — never `cursor/*` draft SHAs.",
        "",
        "| Repo | origin/main SHA | Merged PRs | Notes |",
        "|------|-----------------|------------|-------|",
    ]
    labels = {
        "gunnchos-7gc-ai-ran-field-kit": "field-kit",
        "gunnchos-hardware-industrial-design": "hardware",
        "edge-io-measurement-node": "edge-io",
        "gunnchos-device-os": "device-os",
        "gunnchAI3k": "gunnchAI3k",
        "anime-aggressors": "anime",
        "pedestrian-pursuit": "pedestrian",
        "archive-of-life-artifact-world": "archive",
        "beatlink-party": "beatlink",
    }
    for name, meta in ACCEPTED.items():
        prs = ",".join(f"#{p}" for p in meta.get("merged_prs", [])) or "—"
        lines.append(
            f"| {labels.get(name, name)} | `{meta['sha']}` | {prs} | {meta.get('note', '')} |"
        )
    lines += [
        "",
        "## Carry-forward research siblings (not Cont V product pins)",
        "",
        "Research/twin repos remain tracked separately and are not Cont V product acceptance tips.",
        "",
        f"Machine-readable: [`../_baseline_accepted_mains.json`](../_baseline_accepted_mains.json)",
        "",
    ]
    BASELINE_MD.write_text("\n".join(lines), encoding="utf-8")


def update_matrices(now: str) -> None:
    # --- software integration ---
    soft = {
        "schema_version": "1.1.0",
        "updated_at_utc": now,
        "accepted_main_policy": "MERGED_on_main_SHA_only",
        "continuation": "V",
        "repos": {
            "gunnchos-device-os": {
                "role": "gunnchOS",
                "status": "CONT_V_ACCEPTED_MAIN",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["gunnchos-device-os"]["sha"],
                "merged_prs": [56, 57, 58, 59, 60, 61],
                "token": "GUNNCHOS_BOOTABLE_REFERENCE_IMAGE_DIGITAL_PASS",
                "note": "Includes bootable QEMU image #61 and cloud/fleet #60; 17 service stubs remain; FULL platform not claimed",
            },
            "gunnchAI3k": {
                "role": "AI platform",
                "status": "CONT_V_ACCEPTED_MAIN",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["gunnchAI3k"]["sha"],
                "merged_prs": [21, 22, 23],
                "token": "GUNNCHAI_REAL_LOCAL_INFERENCE_PASS",
                "digitally_validated": True,
                "note": "Real local llama.cpp inference #23 on main; FULL_GUNNCHAI3K_PLATFORM_DIGITAL_COMPLETE forbidden",
            },
            "anime-aggressors": {
                "role": "game",
                "status": "CONT_V_ACCEPTED_MAIN",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["anime-aggressors"]["sha"],
                "merged_prs": [65, 66, 67, 68],
                "alpha_exit": True,
                "content_complete": False,
                "rc_digital": False,
                "claim_integrity": "PREMATURE_REVOKE_BETA_RC_TOKENS",
                "note": "#68 on main; ANIME_BETA_CONTENT_COMPLETE_DIGITAL + ANIME_DIGITAL_RC_READY PREMATURE_REVOKE (blocks_token=true assets)",
            },
            "pedestrian-pursuit": {
                "role": "game",
                "status": "CONT_V_ACCEPTED_MAIN",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["pedestrian-pursuit"]["sha"],
                "merged_prs": [8, 9, 10],
                "content_complete": False,
                "rc_digital": False,
                "note": "#10 Beta digital systems on main; RC PARTIAL; competitive AI matrix not yet",
            },
            "archive-of-life-artifact-world": {
                "role": "game",
                "status": "CONT_V_ACCEPTED_MAIN",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["archive-of-life-artifact-world"]["sha"],
                "merged_prs": [17, 18, 19, 20],
                "live_global_ingest": False,
                "content_complete": False,
                "rc_digital": False,
                "note": "#20 Beta/RC digital on main; global live ingest not claimed; Tier E/F audit Cont V",
            },
            "beatlink-party": {
                "role": "game",
                "status": "CONT_V_ACCEPTED_MAIN_CI_GREEN",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["beatlink-party"]["sha"],
                "merged_prs": [9, 10, 11, 12],
                "content_complete": False,
                "rc_digital": False,
                "alpha_exit": True,
                "note": "#12 Beta/RC on main; Redis/live mic/licensed lyrics still open — scope audit Cont V",
            },
            "edge-io-measurement-node": {
                "role": "ring firmware/host",
                "status": "RING_ZEPHYR_WEST_BUILD_PASS",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["edge-io-measurement-node"]["sha"],
                "merged_prs": [32],
                "token": "RING_ZEPHYR_WEST_BUILD_PASS",
                "note": "Soft-skip cleared; no physical flash",
            },
            "gunnchos-hardware-industrial-design": {
                "role": "electronics/mech",
                "status": "CONT_V_ACCEPTED_MAIN",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["gunnchos-hardware-industrial-design"]["sha"],
                "merged_prs": [44, 45, 46, 47],
                "companion_field_kit_accepted_main_sha": ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"],
                "ring_kicad_cli_validation_pass": False,
                "kicad": "EDMUND_ACTION_REQUIRED",
                "token": "HARDWARE_DESIGN_RELEASE_CANDIDATE",
                "note": "#47 on main; FULL_HARDWARE_DESIGN_RELEASE_COMPLETE not claimed; KiCad EDMUND_ACTION_REQUIRED",
            },
            "gunnchos-7gc-ai-ran-field-kit": {
                "role": "control_plane",
                "status": "CONT_V_POST_MERGE_CANONICALIZATION",
                "pr_state": "MERGED_BASE",
                "accepted_main_sha": ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"],
                "merged_prs": [29, 30, 31, 32, 33, 34, 35],
                "note": "Cont V draft canonicalization consumes Cont IV merge SHAs; not true final umbrella",
            },
        },
        "stale_draft_pins": "CLEARED_TO_MERGE_COMMITS",
        "note": "Former Cont IV draft SHAs superseded by merged accepted mains above.",
        "continuation_v_drafts": "THIS_PR_ONLY_NOT_ACCEPTED_UNTIL_MERGED",
    }
    dump_yaml(soft, FP / "software_integration_matrix.yaml")

    # --- game release ---
    games = {
        "schema_version": "1.1.0",
        "updated_at_utc": now,
        "continuation": "V",
        "release_phases": ["G3_Alpha", "G4_Beta", "G5_RC", "G6_LaunchOperate"],
        "claim_firewall": "scripts/validate_game_release_claims.py",
        "games": {
            "anime_aggressors": {
                "engine": "Godot 4",
                "current_phase": "BETA_RC_MERGED_TOKENS_PREMATURE_REVOKE",
                "accepted_main_sha": ACCEPTED["anime-aggressors"]["sha"],
                "merged_prs": [65, 66, 67, 68],
                "pr_state": "MERGED",
                "alpha_exit": True,
                "content_complete": False,
                "feature_complete": False,
                "rc_digital": False,
                "fighters_defined": 7,
                "art_status": "REQUIRES_ART_PRODUCTION",
                "blocks_token_assets_remaining": 13,
                "tokens": {
                    "ANIME_BETA_CONTENT_COMPLETE_DIGITAL": "PREMATURE_REVOKE",
                    "ANIME_DIGITAL_RC_READY": "PREMATURE_REVOKE",
                },
                "note": "#68 merge accepted; Beta/RC tokens revoked while content/missing_assets.json has blocks_token=true",
            },
            "pedestrian_pursuit": {
                "engine": "Godot",
                "current_phase": "BETA_DIGITAL_ON_MAIN__RC_PARTIAL",
                "accepted_main_sha": ACCEPTED["pedestrian-pursuit"]["sha"],
                "merged_prs": [8, 9, 10],
                "pr_state": "MERGED",
                "alpha_exit": False,
                "content_complete": False,
                "feature_complete": False,
                "rc_digital": False,
                "tracks": 8,
                "cups": 2,
                "art": "REQUIRES_ART_PRODUCTION",
                "tokens": {
                    "PEDESTRIAN_BETA_CONTENT_COMPLETE_DIGITAL": "VALID_WITH_EXPLICIT_SCOPE",
                    "PEDESTRIAN_DIGITAL_RC_READY": "PARTIAL",
                    "PEDESTRIAN_COMPETITIVE_AI_DIGITAL_VALIDATED": "NOT_YET",
                },
                "note": "#10 on main; Beta digital systems scoped; RC partial; AI matrix open",
            },
            "archive_of_life": {
                "engine": "Vite/TS web",
                "current_phase": "BETA_RC_DIGITAL_ON_MAIN__AUDIT_PENDING",
                "accepted_main_sha": ACCEPTED["archive-of-life-artifact-world"]["sha"],
                "merged_prs": [17, 18, 19, 20],
                "pr_state": "MERGED",
                "alpha_exit": True,
                "live_global_ingest": False,
                "content_complete": False,
                "feature_complete": False,
                "rc_digital": False,
                "regions": 12,
                "encounter_taxa": 167,
                "flagship": 24,
                "tokens": {
                    "ARCHIVE_BETA_CONTENT_COMPLETE_DIGITAL": "VALID_WITH_EXPLICIT_SCOPE",
                    "ARCHIVE_DIGITAL_RC_READY": "VALID_WITH_EXPLICIT_SCOPE",
                },
                "note": "#20 on main; Tier E/F + live ingest audits Cont V; not global complete",
            },
            "beat_link": {
                "engine": "Node/pnpm",
                "current_phase": "BETA_RC_DIGITAL_ON_MAIN__SCOPE_AUDIT",
                "accepted_main_sha": ACCEPTED["beatlink-party"]["sha"],
                "merged_prs": [9, 10, 11, 12],
                "pr_state": "MERGED",
                "alpha_exit": True,
                "content_complete": False,
                "feature_complete": False,
                "rc_digital": False,
                "catalog_tracks": 13,
                "modes_complete": True,
                "tokens": {
                    "BEATLINK_BETA_CONTENT_COMPLETE_DIGITAL": "VALID_WITH_EXPLICIT_SCOPE",
                    "BEATLINK_DIGITAL_RC_READY": "VALID_WITH_EXPLICIT_SCOPE",
                },
                "gaps": [
                    "in_memory_rooms_no_redis",
                    "no_live_getUserMedia_pitch",
                    "no_licensed_lyrics_or_platform_sdks",
                    "event_scale_simulation_not_live_event",
                ],
                "note": "#12 on main; Beta/RC digital with explicit DEV/sim scope; Redis/mic Cont V work",
            },
        },
    }
    dump_yaml(games, FP / "game_release_matrix.yaml")

    # --- hardware ---
    hw_sha = ACCEPTED["gunnchos-hardware-industrial-design"]["sha"]
    fk_sha = ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"]
    hw = load_yaml(FP / "hardware_release_matrix.yaml")
    hw["updated_at_utc"] = now
    hw["continuation"] = "V"
    hw["accepted_main_sha"] = hw_sha
    hw["token"] = "HARDWARE_DESIGN_RELEASE_CANDIDATE"
    hw["full_complete_claimed"] = False
    for prod in hw.get("products") or {}:
        entry = hw["products"][prod]
        entry["accepted_hardware_main_sha"] = hw_sha
        entry["accepted_main_sha_hardware"] = hw_sha
        entry["accepted_main_sha_field_kit"] = fk_sha
        entry["merged_pr"] = "https://github.com/gunnchOS3k/gunnchos-hardware-industrial-design/pull/47"
        entry["pr_state"] = "MERGED"
        if prod == "edge_io_rings":
            entry["kicad_cli"] = "EDMUND_ACTION_REQUIRED"
            entry["zephyr_west"] = "PASS_ON_MAIN_VIA_EDGE_IO"
    dump_yaml(hw, FP / "hardware_release_matrix.yaml")

    # --- AI ---
    ai = load_yaml(FP / "ai_capability_matrix.yaml")
    ai["updated_at_utc"] = now
    ai["continuation"] = "V"
    ai["accepted_main_sha"] = ACCEPTED["gunnchAI3k"]["sha"]
    ai["merged_pr"] = "https://github.com/gunnchOS3k/gunnchAI3k/pull/23"
    ai["status"] = "REAL_LOCAL_INFERENCE_MERGED_NOT_PLATFORM_COMPLETE"
    ai["token"] = "GUNNCHAI_REAL_LOCAL_INFERENCE_PASS"
    ai["wave_c"] = {
        "merged_prs": [21, 22, 23],
        "pr_state": "MERGED",
        "accepted_main_sha": ACCEPTED["gunnchAI3k"]["sha"],
        "digitally_validated": True,
        "token": "GUNNCHAI_REAL_LOCAL_INFERENCE_PASS",
        "note": "#23 on main; real SmolLM2/llama.cpp inference; full platform / callable service Cont V",
    }
    dump_yaml(ai, FP / "ai_capability_matrix.yaml")

    # --- connectivity / manufacturing / certification / deployment ---
    conn = {
        "schema_version": "1.1.0",
        "updated_at_utc": now,
        "continuation": "V",
        "accepted_main_sha_field_kit": fk_sha,
        "accepted_main_sha_device_os": ACCEPTED["gunnchos-device-os"]["sha"],
        "truthful_2026_target": [
            "carrier_grade",
            "5G_Advanced_capable",
            "NTN_capable_where_supported",
            "WiFi",
            "private_network",
            "D2D_local",
            "mesh_store_forward_if_justified",
            "IMT2030_aligned",
            "software_defined",
            "6G_migration_engineered",
        ],
        "forbidden_claims": [
            "6G_certified",
            "final_IMT2030_compliant",
            "commercial_6G_carrier_accepted",
            "GATE_8_PASS",
        ],
        "standards_tracker": "standards/requirements/imt2030_current_state.yaml",
        "camara_modes": ["UNAVAILABLE", "SIMULATED", "SANDBOX", "REAL_OPERATOR"],
        "modem_selection": "NOT_FROZEN",
        "esim": "ARCHITECTURE_ONLY_NO_COMPLIANCE_CLAIM",
        "status": "ARCHITECTURE_MATRIX_PRESENT_MODEM_NOT_FROZEN",
    }
    dump_yaml(conn, FP / "connectivity_carrier_matrix.yaml")

    mfg = {
        "schema_version": "1.1.0",
        "updated_at_utc": now,
        "continuation": "V",
        "accepted_main_sha_hardware": hw_sha,
        "products": [
            "student_14_5",
            "ds_xl_coder",
            "handheld_hybrid",
            "edge_io_rings",
            "dock",
        ],
        "per_product_required": [
            "EDA_source",
            "schematic_PDF",
            "ERC",
            "PCB",
            "DRC",
            "stackup",
            "Gerbers",
            "drills",
            "pick_place",
            "BOM_MPN",
            "AVL",
            "assembly_drawing",
            "test_points",
            "STEP",
            "fab_notes",
        ],
        "status": "CANDIDATE_PACKAGES_INCOMPLETE_FOR_ALL_FIVE",
        "kicad": "EDMUND_ACTION_REQUIRED",
        "physical_fab": "FORBIDDEN_WHILE_FREEZE_ACTIVE",
    }
    dump_yaml(mfg, FP / "manufacturing_matrix.yaml")

    cert = {
        "schema_version": "1.1.0",
        "updated_at_utc": now,
        "continuation": "V",
        "accepted_main_sha_field_kit": fk_sha,
        "jurisdictions_to_evaluate": [
            "FCC",
            "ISED",
            "EU_CE_RED",
            "UKCA",
            "PTCRB_GCF",
            "Bluetooth_SIG",
            "WiFi",
            "UN38_3",
            "RoHS",
            "REACH",
        ],
        "status": "READINESS_DOCS_ONLY",
        "claims": "NONE",
        "blocker_class": "EXTERNAL_REQUIRED",
    }
    dump_yaml(cert, FP / "certification_matrix.yaml")

    deploy = {
        "schema_version": "1.1.0",
        "updated_at_utc": now,
        "continuation": "V",
        "accepted_main_sha_field_kit": fk_sha,
        "accepted_main_sha_device_os": ACCEPTED["gunnchos-device-os"]["sha"],
        "campuses": 7,
        "campus_configs": "PARTIAL",
        "fleet": "NOT_PRODUCTION",
        "support": "INCOMPLETE",
        "status": "DIGITAL_PARTIAL_EXTERNAL_REQUIRED_FOR_LIVE_CAMPUSES",
    }
    dump_yaml(deploy, FP / "deployment_support_matrix.yaml")


def update_evidence_registry(now: str) -> None:
    entries = [
        {
            "id": "EV-FK-35",
            "repo": "gunnchos-7gc-ai-ran-field-kit",
            "sha": ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"],
            "merged_prs": [34, 35],
            "state": "MERGED",
            "note": "Cont IV canonicalization + draft registry on main",
        },
        {
            "id": "EV-HW-47",
            "repo": "gunnchos-hardware-industrial-design",
            "sha": ACCEPTED["gunnchos-hardware-industrial-design"]["sha"],
            "merged_pr": 47,
            "state": "MERGED",
            "token": "HARDWARE_DESIGN_RELEASE_CANDIDATE",
            "note": "Former Cont IV draft #47 now accepted merge",
        },
        {
            "id": "EV-EDGE-32",
            "repo": "edge-io-measurement-node",
            "sha": ACCEPTED["edge-io-measurement-node"]["sha"],
            "merged_pr": 32,
            "state": "MERGED",
            "token": "RING_ZEPHYR_WEST_BUILD_PASS",
        },
        {
            "id": "EV-OS-61",
            "repo": "gunnchos-device-os",
            "sha": ACCEPTED["gunnchos-device-os"]["sha"],
            "merged_pr": 61,
            "state": "MERGED",
            "also_includes_pr": 60,
            "token": "GUNNCHOS_BOOTABLE_REFERENCE_IMAGE_DIGITAL_PASS",
            "note": "Bootable QEMU reference image + cloud/fleet DEV; service stubs remain",
        },
        {
            "id": "EV-AI-23",
            "repo": "gunnchAI3k",
            "sha": ACCEPTED["gunnchAI3k"]["sha"],
            "merged_pr": 23,
            "state": "MERGED",
            "token": "GUNNCHAI_REAL_LOCAL_INFERENCE_PASS",
            "digitally_validated": True,
        },
        {
            "id": "EV-ANIME-68",
            "repo": "anime-aggressors",
            "sha": ACCEPTED["anime-aggressors"]["sha"],
            "merged_pr": 68,
            "state": "MERGED",
            "note": "Beta/RC digital merge; tokens PREMATURE_REVOKE under claim integrity audit",
            "tokens_revoked": [
                "ANIME_BETA_CONTENT_COMPLETE_DIGITAL",
                "ANIME_DIGITAL_RC_READY",
            ],
        },
        {
            "id": "EV-PED-10",
            "repo": "pedestrian-pursuit",
            "sha": ACCEPTED["pedestrian-pursuit"]["sha"],
            "merged_pr": 10,
            "state": "MERGED",
            "note": "Beta digital / RC partial on accepted main",
        },
        {
            "id": "EV-ARCH-20",
            "repo": "archive-of-life-artifact-world",
            "sha": ACCEPTED["archive-of-life-artifact-world"]["sha"],
            "merged_pr": 20,
            "state": "MERGED",
            "note": "Beta digital / Digital RC on accepted main",
        },
        {
            "id": "EV-BL-12",
            "repo": "beatlink-party",
            "sha": ACCEPTED["beatlink-party"]["sha"],
            "merged_pr": 12,
            "state": "MERGED",
            "note": "Beta Event Platform + Digital RC on accepted main; Redis/mic gaps remain",
        },
        {
            "id": "EV-FK-STANDARDS-FIREWALL",
            "repo": "gunnchos-7gc-ai-ran-field-kit",
            "sha": ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"],
            "requirement_id": "SYS-STANDARDS-001",
            "note": "Claim firewall in CI",
        },
        {
            "id": "EV-FK-EVIDENCE-REGISTRY",
            "repo": "gunnchos-7gc-ai-ran-field-kit",
            "sha": ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"],
            "requirement_id": "SYS-MISSION-009",
        },
        {
            "id": "EV-FK-CARRIER-GRADE-CLAIM-GUARD",
            "repo": "gunnchos-7gc-ai-ran-field-kit",
            "sha": ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"],
            "requirement_id": "FP-CHARTER-L635-CARRIER-GRADE-NOT-MODEM",
        },
        {
            "id": "EV-FK-PRODUCT-FAMILY-MATRIX",
            "repo": "gunnchos-7gc-ai-ran-field-kit",
            "sha": ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"],
            "requirement_id": "SYS-MISSION-002",
        },
        {
            "id": "EV-FK-CONN-MATRIX",
            "repo": "gunnchos-7gc-ai-ran-field-kit",
            "sha": ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"],
            "requirement_id": "FP-CONN-CARRIER-GRADE",
        },
        {
            "id": "EV-FK-GAME-CLAIM-FIREWALL",
            "repo": "gunnchos-7gc-ai-ran-field-kit",
            "sha": ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"],
            "note": "validate_game_release_claims.py rejects Beta/RC when blocks_token=true remains",
        },
        {
            "id": "EV-CONT4-DRAFTS-SUPERSEDED",
            "status": "SUPERSEDED",
            "note": "Cont IV draft pins cleared; merge commits listed above are Cont V accepted tips",
        },
    ]
    dump_yaml(
        {
            "schema_version": "1.1.0",
            "updated_at_utc": now,
            "continuation": "V",
            "policy": "docs_alone_cannot_satisfy_code_requirements",
            "accepted_main_policy": "no_stale_draft_sha_as_accepted",
            "entries": entries,
        },
        FP / "evidence_registry.yaml",
    )


def write_proof_reports(graph: dict[str, Any], decisions: list[tuple[str, str]]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    nodes = graph["nodes"]
    status_counts = dict(Counter(n["full_product_status"] for n in nodes))
    by_sub = defaultdict(Counter)
    by_owner = defaultdict(Counter)
    for n in nodes:
        by_sub[n.get("subsystem") or "unknown"][n["full_product_status"]] += 1
        by_owner[n.get("owner_repository") or "unknown"][n["full_product_status"]] += 1

    counts_payload = {
        "generated_at_utc": graph["updated_at_utc"],
        "continuation": "V",
        "total": graph["count"],
        "unmapped_count": graph["unmapped_count"],
        "unowned_count": graph["unowned_count"],
        "unclassified_count": graph["unclassified_count"],
        "status_counts": status_counts,
        "by_subsystem": {k: dict(v) for k, v in sorted(by_sub.items())},
        "by_owner_repository": {k: dict(v) for k, v in sorted(by_owner.items())},
        "accepted_mains": {k: v["sha"] for k, v in ACCEPTED.items()},
    }
    (REPORTS / "REQUIREMENT_PROOF_COUNTS.json").write_text(
        json.dumps(counts_payload, indent=2) + "\n", encoding="utf-8"
    )

    # Ledger
    ledger = [
        "# REQUIREMENT PROOF LEDGER — Continuation V",
        "",
        f"Updated: {graph['updated_at_utc']}",
        "",
        f"Total nodes: **{graph['count']}**",
        f"UNMAPPED={graph['unmapped_count']} · UNOWNED={graph['unowned_count']} · UNCLASSIFIED={graph['unclassified_count']}",
        "",
        "## Status counts",
        "",
        "| Status | Count |",
        "|--------|------:|",
    ]
    for k, v in sorted(status_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        ledger.append(f"| `{k}` | {v} |")
    ledger += [
        "",
        "## Promotion doctrine",
        "",
        "Higher digital states require `implementation_paths`, `test_paths`,",
        "`accepted_repository`, `accepted_main_sha`, `evidence_artifact`, `evidence_result`.",
        "Docs alone never satisfy code requirements. Simulation never satisfies physical measurement.",
        "Physical/external blockers stay `PHYSICAL_REQUIRED` / `EXTERNAL_REQUIRED`.",
        "",
        "## Per-node decisions (compact)",
        "",
        "| ID | Status | Decision | Owner | Accepted SHA |",
        "|----|--------|----------|-------|--------------|",
    ]
    by_id = {n["id"]: n for n in nodes}
    for nid, decision in decisions:
        n = by_id[nid]
        sha = (n.get("accepted_main_sha") or n.get("accepted_sha") or "—")
        if isinstance(sha, str) and len(sha) > 12:
            sha = sha[:12]
        ledger.append(
            f"| `{nid}` | `{n['full_product_status']}` | {decision} | {n.get('owner_repository')} | `{sha}` |"
        )
    (REPORTS / "REQUIREMENT_PROOF_LEDGER.md").write_text("\n".join(ledger) + "\n", encoding="utf-8")

    # Gaps
    gaps = [
        "# REQUIREMENT PROOF GAPS — Continuation V",
        "",
        f"Updated: {graph['updated_at_utc']}",
        "",
        "## Remaining DOC_ONLY",
        "",
    ]
    doc_only = [n for n in nodes if n["full_product_status"] == "DOC_ONLY"]
    if not doc_only:
        gaps.append("None — every digitally provable node left DOC_ONLY or was classified physical/external.")
    else:
        gaps.append(f"Count: **{len(doc_only)}**")
        for n in doc_only[:80]:
            gaps.append(f"- `{n['id']}`: {n.get('title', '')[:100]}")
        if len(doc_only) > 80:
            gaps.append(f"- … and {len(doc_only) - 80} more")

    gaps += [
        "",
        "## SCHEMA_ONLY / STUB_ONLY (digitally in-scope, incomplete)",
        "",
    ]
    soft = [n for n in nodes if n["full_product_status"] in {"SCHEMA_ONLY", "STUB_ONLY", "SIMULATION_ONLY"}]
    gaps.append(f"Count: **{len(soft)}** — implementation still incomplete for full product entirety.")
    for n in soft[:40]:
        gaps.append(f"- `{n['id']}` [{n['full_product_status']}]: {n.get('title', '')[:90]}")
    if len(soft) > 40:
        gaps.append(f"- … and {len(soft) - 40} more")

    gaps += [
        "",
        "## PHYSICAL_REQUIRED / EXTERNAL_REQUIRED",
        "",
        f"- PHYSICAL_REQUIRED: **{status_counts.get('PHYSICAL_REQUIRED', 0)}**",
        f"- EXTERNAL_REQUIRED: **{status_counts.get('EXTERNAL_REQUIRED', 0)}**",
        "",
        "## Forbidden claims (still blocked)",
        "",
        "- FULL_PHYSICAL_VALIDATION_COMPLETE",
        "- FULL_EXTERNAL_VALIDATION_COMPLETE",
        "- FULL_CERTIFICATION_COMPLETE",
        "- FULL_DEPLOYMENT_COMPLETE",
        "- FULL_OPERATIONAL_PRODUCT",
        "- GATE_8_PASS / 6G_CERTIFIED",
        "",
        "## Human actions",
        "",
        "- EDMUND_ACTION_REQUIRED: macOS admin/install for KiCad CLI if hardware EDA validation needed",
        "- Edmund merges only (Cursor never merges)",
        "",
    ]
    (REPORTS / "REQUIREMENT_PROOF_GAPS.md").write_text("\n".join(gaps) + "\n", encoding="utf-8")
    (REPORTS / "GAPS.md").write_text("\n".join(gaps) + "\n", encoding="utf-8")
    (REPORTS / "COUNTS.json").write_text(
        (REPORTS / "REQUIREMENT_PROOF_COUNTS.json").read_text(encoding="utf-8"), encoding="utf-8"
    )


def patch_master_status(graph: dict[str, Any]) -> None:
    master = REPORTS / "FULL_PRODUCT_MASTER_STATUS.md"
    if not master.exists():
        return
    text = master.read_text(encoding="utf-8")
    counts = graph["status_counts"]
    block = (
        "## Requirement catalog bootstrap\n\n"
        f"- Catalogued + ingested nodes: **{graph['count']}**\n"
        f"- Status counts: `{counts}`\n"
        f"- UNMAPPED={graph['unmapped_count']} · UNOWNED={graph['unowned_count']} · "
        f"UNCLASSIFIED={graph['unclassified_count']}\n"
        f"- Cont V proof: `reports/REQUIREMENT_PROOF_COUNTS.json`\n"
        f"- Cont V queues: `continuation_v/` + claim audit\n"
        f"- Target: `UNMAPPED_NORMATIVE_REQUIREMENTS = 0` "
        f"({'MET' if graph['unmapped_count'] == 0 else 'OPEN'})\n"
        f"- Validator: `scripts/validate_full_product_requirement_graph.py`\n"
        f"- Updated: {graph['updated_at_utc']}\n"
    )
    if "## Requirement catalog bootstrap" in text:
        text = re.sub(
            r"## Requirement catalog bootstrap\n\n.*?(?=\n## |\Z)",
            block + "\n",
            text,
            count=1,
            flags=re.S,
        )
    else:
        text += "\n" + block
    # Strip agent UUID markdown links if any
    text = re.sub(
        r"\[[^\]]*\]\([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}[^)]*\)",
        "",
        text,
    )
    master.write_text(text, encoding="utf-8")


def write_honest_promotions(now: str) -> None:
    fk = ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"]
    promos = []
    for item in EXPLICIT_PROMOTIONS:
        owner = item["owner_repository"]
        _, sha = accepted_for_owner(owner)
        promos.append(
            {
                **item,
                "tests": list(item.get("test_paths") or []),
                "accepted_sha": sha,
                "accepted_main_sha": sha,
                "accepted_repository": OWNER_ALIAS.get(owner, owner),
            }
        )
    dump_yaml(
        {
            "schema_version": "1.1.0",
            "updated_at_utc": now,
            "continuation": "V",
            "note": (
                "Honest Cont V promotions. Broader digital re-prove applied in "
                "requirement_graph.yaml via prove_full_product_continuation_v.py."
            ),
            "accepted_main_sha": fk,
            "promotions": promos,
        },
        PROMOTIONS,
    )



IMPL_CLASS_BY_HINT = [
    (("kicad", "schematic", "pcb", "gerber", "eda"), "EDA"),
    (("cad", "step", "openscad", "enclosure", "mechanical"), "CAD"),
    (("firmware", "zephyr", "bootloader", "mcu"), "FIRMWARE"),
    (("fighter", "stage", "track", "game", "godot", "content", "art", "mode"), "GAME_CONTENT"),
    (("runtime", "engine", "netplay", "room", "socket"), "GAME_RUNTIME"),
    (("ingest", "pipeline", "rag", "corpus", "snapshot"), "DATA_PIPELINE"),
    (("security", "sandbox", "permission", "attestation", "secure boot"), "SECURITY_CONTROL"),
    (("ci", "workflow", "validator", "gate"), "CI_CONTROL"),
    (("governance", "consent", "ethics", "policy", "charter"), "GOVERNANCE_CONTROL"),
    (("deploy", "fleet", "ota", "campus", "support"), "DEPLOYMENT_TOOLING"),
    (("manufactur", "bom", "avl", "fab", "pick_place"), "MANUFACTURING_TOOLING"),
    (("certif", "fcc", "ptcrb", "red", "compliance"), "CERT_READINESS_TOOLING"),
    (("support", "runbook", "diagnostics"), "SUPPORT_TOOLING"),
    (("imt", "standard", "3gpp", "camara"), "STANDARD_MAPPING"),
    (("service", "ipc", "api", "grpc", "dbus"), "SERVICE"),
    (("ai", "llm", "inference", "model", "tutoring"), "RUNTIME_CODE"),
]


def classify_implementation(node: dict[str, Any]) -> str:
    blob = " ".join(
        str(node.get(k) or "")
        for k in ("id", "title", "description", "subsystem", "owner_repository", "source_kind")
    ).lower()
    blockers = set(node.get("blocker_class") or [])
    if node.get("full_product_status") == "PHYSICAL_REQUIRED" and blockers & PHYS_BLOCKERS:
        # May still have digital work — default TRULY_PHYSICAL only when clearly measurement-only
        if any(x in blob for x in ("measure", "thermal", "battery", "antenna", "rf chamber", "evt", "dvt", "pvt", "physical")):
            if not any(x in blob for x in ("schema", "api", "ui", "harness", "model", "state machine", "package")):
                return "TRULY_PHYSICAL"
    if node.get("full_product_status") == "EXTERNAL_REQUIRED" and blockers & EXT_BLOCKERS:
        if any(x in blob for x in ("carrier accept", "lab cert", "partner", "license", "human participant")):
            if not any(x in blob for x in ("template", "adapter", "manifest", "runbook", "test mode")):
                return "TRULY_EXTERNAL"
    for hints, klass in IMPL_CLASS_BY_HINT:
        if any(h in blob for h in hints):
            return klass
    sub = (node.get("subsystem") or "").lower()
    if sub in {"anime", "pedestrian", "archive", "beatlink", "games"}:
        return "GAME_CONTENT"
    if sub in {"hardware", "rings", "manufacturing"}:
        return "EDA"
    if sub in {"ai", "gunnchai"}:
        return "RUNTIME_CODE"
    if sub in {"os", "device", "gunnchos"}:
        return "SERVICE"
    if sub in {"certification"}:
        return "CERT_READINESS_TOOLING"
    if sub in {"connectivity", "carrier_grade", "standards"}:
        return "STANDARD_MAPPING"
    return "RUNTIME_CODE"


def external_kind(node: dict[str, Any]) -> str:
    b = set(node.get("blocker_class") or [])
    blob = " ".join(str(node.get(k) or "") for k in ("id", "title", "description")).lower()
    if "REQUIRES_CARRIER" in b or "carrier" in blob:
        return "EXTERNAL_CARRIER"
    if "REQUIRES_CERTIFICATION_LAB" in b or "cert" in blob:
        return "EXTERNAL_CERTIFICATION"
    if "REQUIRES_MANUFACTURER" in b or "supplier" in blob or "avl" in blob:
        return "EXTERNAL_SUPPLIER"
    if "REQUIRES_HUMAN_PARTICIPANTS" in b:
        return "EXTERNAL_HUMAN_PARTICIPANT"
    if "REQUIRES_STANDARD_FINALIZATION" in b:
        return "EXTERNAL_STANDARD_FINALIZATION"
    if "REQUIRES_ETHICS_OR_GOVERNANCE_APPROVAL" in b or "REQUIRES_EDMUND" in b:
        return "EXTERNAL_DECISION"
    if "license" in blob or "credential" in blob:
        return "EXTERNAL_LICENSE" if "license" in blob else "EXTERNAL_CREDENTIAL"
    if "REQUIRES_EXTERNAL_PARTNER" in b:
        return "EXTERNAL_DECISION"
    return "EXTERNAL_DECISION"


def target_branch_for(owner: str) -> str:
    return "cursor/full-product-continuation-v-digital-closure"


def write_continuation_v_queues(graph: dict[str, Any], now: str) -> None:
    CONT_V.mkdir(parents=True, exist_ok=True)
    nodes = graph["nodes"]
    schema = [n for n in nodes if n.get("full_product_status") == "SCHEMA_ONLY"]
    physical = [n for n in nodes if n.get("full_product_status") == "PHYSICAL_REQUIRED"]
    external = [n for n in nodes if n.get("full_product_status") == "EXTERNAL_REQUIRED"]

    schema_items = []
    for n in schema:
        owner = n.get("owner_repository") or "gunnchos-7gc-ai-ran-field-kit"
        impl_class = classify_implementation(n)
        matrix = _matrix_for(n)
        schema_items.append(
            {
                "id": n["id"],
                "description": n.get("title") or n.get("description") or "",
                "owner_repo": owner,
                "owner_subsystem": n.get("subsystem") or "unknown",
                "implementation_class": impl_class,
                "existing_evidence": list(n.get("evidence") or [])
                or ([n.get("evidence_result")] if n.get("evidence_result") else []),
                "missing_implementation": (
                    f"Digitally executable work still SCHEMA_ONLY under Cont V; "
                    f"class={impl_class}; source_kind={n.get('source_kind')}"
                ),
                "implementation_paths": list(n.get("implementation_paths") or [])
                or [f"program/full_product/{matrix}"],
                "integration_paths": [
                    "program/full_product/requirement_graph.yaml",
                    "program/full_product/evidence_registry.yaml",
                ],
                "test_paths": list(n.get("test_paths") or n.get("tests") or [])
                or ["tests/full_product/test_requirement_promotion_validators.py"],
                "target_state": "IMPLEMENTED",
                "branch": target_branch_for(owner),
                "status": "OPEN",
            }
        )

    dump_yaml(
        {
            "schema_version": "1.0.0",
            "continuation": "V",
            "generated_at_utc": now,
            "policy": "FULL_ENUMERATION_NO_TRUNCATION",
            "count": len(schema_items),
            "items": schema_items,
        },
        CONT_V / "schema_only_work_queue.yaml",
    )

    phys_items = []
    for n in physical:
        owner = n.get("owner_repository") or "unknown"
        dig_done = False  # Cont V audit starts open; digital subrequirements must be proven
        phys_items.append(
            {
                "id": n["id"],
                "description": n.get("title") or n.get("description") or "",
                "owner_repo": owner,
                "owner_subsystem": n.get("subsystem") or "unknown",
                "blocker_class": list(n.get("blocker_class") or []),
                "digital_subrequirements_complete": dig_done,
                "split_required": True,
                "irreducible_physical_assertion": (
                    "Measurement / hardware / local device proof only after digital package exists"
                ),
                "recommended_digital_class": classify_implementation(n),
                "status": "AUDIT_OPEN",
                "branch": target_branch_for(owner),
            }
        )
    dump_yaml(
        {
            "schema_version": "1.0.0",
            "continuation": "V",
            "generated_at_utc": now,
            "policy": "FULL_ENUMERATION_NO_TRUNCATION",
            "count": len(phys_items),
            "question": "Is every meaningful digital subrequirement already implemented?",
            "items": phys_items,
        },
        CONT_V / "physical_required_audit.yaml",
    )

    ext_items = []
    for n in external:
        owner = n.get("owner_repository") or "unknown"
        ext_items.append(
            {
                "id": n["id"],
                "description": n.get("title") or n.get("description") or "",
                "owner_repo": owner,
                "owner_subsystem": n.get("subsystem") or "unknown",
                "blocker_class": list(n.get("blocker_class") or []),
                "external_kind": external_kind(n),
                "digital_preparation_complete": False,
                "required_before_leave_blocked": [
                    "submission_template",
                    "api_adapter_or_test_mode",
                    "evidence_collector",
                    "package_manifest",
                    "support_runbook",
                    "legal_or_provenance_metadata",
                    "fallback_behavior",
                ],
                "status": "AUDIT_OPEN",
                "branch": target_branch_for(owner),
            }
        )
    dump_yaml(
        {
            "schema_version": "1.0.0",
            "continuation": "V",
            "generated_at_utc": now,
            "policy": "FULL_ENUMERATION_NO_TRUNCATION",
            "count": len(ext_items),
            "items": ext_items,
        },
        CONT_V / "external_required_audit.yaml",
    )

    # Mixed splits: phys+ext blockers OR physical/external nodes whose titles imply digital packages
    mixed = []
    for n in nodes:
        b = set(n.get("blocker_class") or [])
        has_p = bool(b & PHYS_BLOCKERS)
        has_e = bool(b & EXT_BLOCKERS)
        status = n.get("full_product_status")
        if has_p and has_e:
            reason = "MIXED_BLOCKER_CLASSES"
        elif status in {"PHYSICAL_REQUIRED", "EXTERNAL_REQUIRED"} and classify_implementation(n) not in {
            "TRULY_PHYSICAL",
            "TRULY_EXTERNAL",
        }:
            reason = "LIKELY_DIGITAL_PLUS_IRREDUCIBLE"
        else:
            continue
        mixed.append(
            {
                "id": n["id"],
                "description": n.get("title") or n.get("description") or "",
                "owner_repo": n.get("owner_repository"),
                "current_status": status,
                "blocker_class": list(b),
                "split_reason": reason,
                "digital_slice_target": "IMPLEMENTED",
                "irreducible_slice_target": (
                    "PHYSICAL_REQUIRED" if has_p and not has_e else "EXTERNAL_REQUIRED" if has_e else status
                ),
                "implementation_class": classify_implementation(n),
                "status": "SPLIT_CANDIDATE",
                "branch": target_branch_for(n.get("owner_repository") or "gunnchos-7gc-ai-ran-field-kit"),
            }
        )
    dump_yaml(
        {
            "schema_version": "1.0.0",
            "continuation": "V",
            "generated_at_utc": now,
            "policy": "FULL_ENUMERATION_NO_TRUNCATION",
            "count": len(mixed),
            "items": mixed,
        },
        CONT_V / "mixed_requirement_splits.yaml",
    )

    claim_items = build_claim_integrity_items(now)
    dump_yaml(
        {
            "schema_version": "1.0.0",
            "continuation": "V",
            "generated_at_utc": now,
            "policy": "FULL_ENUMERATION_NO_TRUNCATION",
            "count": len(claim_items),
            "items": claim_items,
        },
        CONT_V / "claim_integrity_audit.yaml",
    )
    write_claim_integrity_md(claim_items, now)


def anime_blocks_token_count() -> int:
    path = SIBLING / "anime-aggressors" / "content" / "missing_assets.json"
    if not path.exists():
        return -1
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items") or []
    return sum(1 for x in items if isinstance(x, dict) and x.get("blocks_token") is True)


def build_claim_integrity_items(now: str) -> list[dict[str, Any]]:
    bt = anime_blocks_token_count()
    anime_sha = ACCEPTED["anime-aggressors"]["sha"]
    items = [
        {
            "token": "ANIME_BETA_CONTENT_COMPLETE_DIGITAL",
            "repo": "anime-aggressors",
            "claiming_artifact": "docs/ANIME_BETA_CONTENT_STATUS.md",
            "requirements": ["Beta launch content complete under digital Beta rule"],
            "blocking_artifacts": [
                "content/missing_assets.json",
                "builds/digital-rc/content/missing_assets.json",
            ],
            "contradictions": [
                f"{bt} assets with status=REQUIRES_ART_PRODUCTION and blocks_token=true "
                "(7 fighter model GLBs + 6 stage art) while token claimed YES"
            ],
            "validity": "PREMATURE_REVOKE",
            "action": "Revoke until blocks_token=true assets resolved or Beta rule explicitly re-scoped",
            "accepted_main_sha": anime_sha,
        },
        {
            "token": "ANIME_DIGITAL_RC_READY",
            "repo": "anime-aggressors",
            "claiming_artifact": "playtest-evidence/digital_rc_validation.json",
            "requirements": ["Beta content complete + RC runner"],
            "blocking_artifacts": ["content/missing_assets.json", "docs/ANIME_BETA_CONTENT_STATUS.md"],
            "contradictions": [
                "RC token_earned=true depends on Beta content complete, which is PREMATURE_REVOKE"
            ],
            "validity": "PREMATURE_REVOKE",
            "action": "Revoke until Beta content token is valid under claim firewall",
            "accepted_main_sha": anime_sha,
        },
        {
            "token": "PEDESTRIAN_BETA_CONTENT_COMPLETE_DIGITAL",
            "repo": "pedestrian-pursuit",
            "claiming_artifact": "docs/PEDESTRIAN_BETA_DIGITAL_RC_STATUS.md",
            "requirements": ["Beta digital systems / catalog / modes"],
            "blocking_artifacts": ["art REQUIRES_ART_PRODUCTION"],
            "contradictions": [],
            "validity": "VALID_WITH_EXPLICIT_SCOPE",
            "action": "Keep scoped to digital systems; do not claim visual/store Beta",
            "accepted_main_sha": ACCEPTED["pedestrian-pursuit"]["sha"],
        },
        {
            "token": "PEDESTRIAN_DIGITAL_RC_READY",
            "repo": "pedestrian-pursuit",
            "claiming_artifact": "docs/PEDESTRIAN_BETA_DIGITAL_RC_STATUS.md",
            "requirements": ["Digital RC packaging"],
            "blocking_artifacts": ["store/device RC", "competitive AI matrix"],
            "contradictions": ["Documented PARTIAL"],
            "validity": "VALID_WITH_EXPLICIT_SCOPE",
            "action": "Keep PARTIAL; do not promote to READY until packaging+AI matrix close",
            "accepted_main_sha": ACCEPTED["pedestrian-pursuit"]["sha"],
        },
        {
            "token": "ARCHIVE_BETA_CONTENT_COMPLETE_DIGITAL",
            "repo": "archive-of-life-artifact-world",
            "claiming_artifact": "docs/BETA_RC_STATUS.md",
            "requirements": ["Frozen launch Tier E/F complete"],
            "blocking_artifacts": ["live global ingest", "IUCN token", "Tier E/F audit"],
            "contradictions": ["Global complete explicitly false; Cont V must audit Tier E/F"],
            "validity": "VALID_WITH_EXPLICIT_SCOPE",
            "action": "Retain only if frozen launch Tier E/F set complete; else revoke",
            "accepted_main_sha": ACCEPTED["archive-of-life-artifact-world"]["sha"],
        },
        {
            "token": "ARCHIVE_DIGITAL_RC_READY",
            "repo": "archive-of-life-artifact-world",
            "claiming_artifact": "public/data/status/digital_rc_report.json",
            "requirements": ["Package + provenance + offline packs + Beta digital"],
            "blocking_artifacts": ["live operator ingest credentials"],
            "contradictions": [],
            "validity": "VALID_WITH_EXPLICIT_SCOPE",
            "action": "Keep digital-RC scope; no live global ingest claim",
            "accepted_main_sha": ACCEPTED["archive-of-life-artifact-world"]["sha"],
        },
        {
            "token": "BEATLINK_BETA_CONTENT_COMPLETE_DIGITAL",
            "repo": "beatlink-party",
            "claiming_artifact": "docs/BETA_RC_TOKENS.json",
            "requirements": ["Launch digital functionality complete"],
            "blocking_artifacts": [
                "in_memory_rooms_no_redis",
                "no_live_getUserMedia_pitch",
                "no_licensed_lyrics_or_platform_sdks",
            ],
            "contradictions": [
                "Token true while Cont V prompt lists digitally executable Redis/mic gaps"
            ],
            "validity": "VALID_WITH_EXPLICIT_SCOPE",
            "action": "Scope to current DEV/sim depth OR revoke after Cont V Redis/mic closure decision",
            "accepted_main_sha": ACCEPTED["beatlink-party"]["sha"],
        },
        {
            "token": "BEATLINK_DIGITAL_RC_READY",
            "repo": "beatlink-party",
            "claiming_artifact": "docs/digital-rc/ready.json",
            "requirements": ["Digital RC packaging"],
            "blocking_artifacts": ["store/HSM/physical RC"],
            "contradictions": [],
            "validity": "VALID_WITH_EXPLICIT_SCOPE",
            "action": "Keep DEV signing / digital packaging scope only",
            "accepted_main_sha": ACCEPTED["beatlink-party"]["sha"],
        },
        {
            "token": "GUNNCHOS_BOOTABLE_REFERENCE_IMAGE_DIGITAL_PASS",
            "repo": "gunnchos-device-os",
            "claiming_artifact": "docs/full_product/BOOTABLE_REFERENCE_IMAGE.md",
            "requirements": ["QEMU aarch64 boot evidence"],
            "blocking_artifacts": ["17 service stubs in image"],
            "contradictions": [],
            "validity": "VALID_WITH_EXPLICIT_SCOPE",
            "action": "Keep narrow boot token; forbid FULL_GUNNCHOS_PLATFORM_DIGITAL_COMPLETE",
            "accepted_main_sha": ACCEPTED["gunnchos-device-os"]["sha"],
        },
        {
            "token": "FULL_GUNNCHOS_PLATFORM_DIGITAL_COMPLETE",
            "repo": "gunnchos-device-os",
            "claiming_artifact": "(forbidden while stubs remain)",
            "requirements": ["All digitally executable platform services real"],
            "blocking_artifacts": ["17 service stubs"],
            "contradictions": ["Would contradict stub inventory"],
            "validity": "PREMATURE_REVOKE",
            "action": "Ensure never claimed; Cont V stub elimination wave",
            "accepted_main_sha": ACCEPTED["gunnchos-device-os"]["sha"],
        },
        {
            "token": "GUNNCHAI_REAL_LOCAL_INFERENCE_PASS",
            "repo": "gunnchAI3k",
            "claiming_artifact": "evidence/system-layer/REAL_INFERENCE_BENCH.json",
            "requirements": ["Reproducible local llama.cpp inference bench"],
            "blocking_artifacts": [],
            "contradictions": [],
            "validity": "VALID",
            "action": "Keep; do not equate to FULL_GUNNCHAI3K_PLATFORM_DIGITAL_COMPLETE",
            "accepted_main_sha": ACCEPTED["gunnchAI3k"]["sha"],
        },
        {
            "token": "FULL_GUNNCHAI3K_PLATFORM_DIGITAL_COMPLETE",
            "repo": "gunnchAI3k",
            "claiming_artifact": "(not earned)",
            "requirements": ["Callable capability service + governance + RAG + evals"],
            "blocking_artifacts": ["SCHEMA_ONLY AI capability nodes"],
            "contradictions": [],
            "validity": "PREMATURE_REVOKE",
            "action": "Forbidden until Cont V AI productization closes",
            "accepted_main_sha": ACCEPTED["gunnchAI3k"]["sha"],
        },
        {
            "token": "HARDWARE_DESIGN_RELEASE_CANDIDATE",
            "repo": "gunnchos-hardware-industrial-design",
            "claiming_artifact": "docs/full_product_family/HARDWARE_DESIGN_RELEASE_STATUS.md",
            "requirements": ["Exact-MPN candidate packages for five products"],
            "blocking_artifacts": ["KiCad CLI EDMUND_ACTION_REQUIRED"],
            "contradictions": [],
            "validity": "VALID_WITH_EXPLICIT_SCOPE",
            "action": "Keep CANDIDATE; FULL_HARDWARE_DESIGN_RELEASE_COMPLETE forbidden",
            "accepted_main_sha": ACCEPTED["gunnchos-hardware-industrial-design"]["sha"],
        },
        {
            "token": "FULL_HARDWARE_DESIGN_RELEASE_COMPLETE",
            "repo": "gunnchos-hardware-industrial-design",
            "claiming_artifact": "(not claimed)",
            "requirements": ["ERC/DRC/mfg export for all five"],
            "blocking_artifacts": ["EB-KICAD-ADMIN"],
            "contradictions": [],
            "validity": "PREMATURE_REVOKE",
            "action": "Forbidden until KiCad CLI + package completeness",
            "accepted_main_sha": ACCEPTED["gunnchos-hardware-industrial-design"]["sha"],
        },
        {
            "token": "RING_ZEPHYR_WEST_BUILD_PASS",
            "repo": "edge-io-measurement-node",
            "claiming_artifact": "program/full_product/evidence_registry.yaml",
            "requirements": ["Zephyr west digital build"],
            "blocking_artifacts": [],
            "contradictions": [],
            "validity": "VALID",
            "action": "Keep; no physical flash claim",
            "accepted_main_sha": ACCEPTED["edge-io-measurement-node"]["sha"],
        },
    ]
    for item in items:
        item["audited_at_utc"] = now
    return items


def write_claim_integrity_md(items: list[dict[str, Any]], now: str) -> None:
    lines = [
        "# Continuation V — Claim Integrity Audit",
        "",
        f"Updated: {now}",
        "",
        "Doctrine: no attachment to prior tokens. Revoke if evidence contradicts the claim.",
        "Allowed validity: `VALID` | `VALID_WITH_EXPLICIT_SCOPE` | `PREMATURE_REVOKE` | `SUPERSEDED`.",
        "",
        "## Anime Beta/RC contradiction (known)",
        "",
        "`content/missing_assets.json` lists launch art assets with `blocks_token: true` while",
        "`ANIME_BETA_CONTENT_COMPLETE_DIGITAL` / `ANIME_DIGITAL_RC_READY` are claimed on accepted main.",
        "Cont V marks both **PREMATURE_REVOKE**. Field-kit `scripts/validate_game_release_claims.py`",
        "rejects Beta/RC claims when any `blocks_token=true` asset remains.",
        "",
        "## Token table",
        "",
        "| Token | Repo | Validity | Action |",
        "|-------|------|----------|--------|",
    ]
    for it in items:
        lines.append(
            f"| `{it['token']}` | {it['repo']} | `{it['validity']}` | {it['action'][:90]} |"
        )
    lines += ["", "## Per-token detail", ""]
    for it in items:
        lines += [
            f"### `{it['token']}`",
            "",
            f"- **repo:** `{it['repo']}`",
            f"- **claiming artifact:** `{it['claiming_artifact']}`",
            f"- **accepted_main_sha:** `{it.get('accepted_main_sha')}`",
            f"- **validity:** `{it['validity']}`",
            f"- **action:** {it['action']}",
            "- **requirements:**",
        ]
        for r in it.get("requirements") or []:
            lines.append(f"  - {r}")
        lines.append("- **blocking artifacts:**")
        for b in it.get("blocking_artifacts") or []:
            lines.append(f"  - `{b}`")
        if it.get("contradictions"):
            lines.append("- **contradictions:**")
            for c in it["contradictions"]:
                lines.append(f"  - {c}")
        else:
            lines.append("- **contradictions:** none recorded")
        lines.append("")
    lines += [
        "## Machine-readable",
        "",
        "- `program/full_product/continuation_v/claim_integrity_audit.yaml`",
        "- Game claim firewall: `scripts/validate_game_release_claims.py`",
        "",
    ]
    CLAIM_AUDIT_MD.write_text("\n".join(lines), encoding="utf-8")


def update_external_blockers(now: str) -> None:
    path = FP / "external_blockers.yaml"
    data = load_yaml(path) if path.exists() else {"blockers": []}
    data["updated_at_utc"] = now
    data["continuation"] = "V"
    for b in data.get("blockers") or []:
        if b.get("id") == "EB-KICAD-ADMIN":
            b["hardware_merged_pr"] = "https://github.com/gunnchOS3k/gunnchos-hardware-industrial-design/pull/47"
            b["hardware_accepted_main_sha"] = ACCEPTED["gunnchos-hardware-industrial-design"]["sha"]
            b["field_kit_accepted_main_sha"] = ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"]
            b["status"] = "EDMUND_ACTION_REQUIRED"
            b["note"] = "Cont V — KiCad remains EDMUND_ACTION_REQUIRED; #47 is accepted merge not draft"
            b.pop("continuation_iv_draft_pr", None)
            b.pop("draft_pr", None)
            b.pop("field_kit_draft_pr", None)
            b.pop("hardware_draft_pr", None)
    k = data.setdefault("kicad", {})
    k["status"] = "EDMUND_ACTION_REQUIRED"
    k["hardware_accepted_main_sha"] = ACCEPTED["gunnchos-hardware-industrial-design"]["sha"]
    k["field_kit_accepted_main_sha"] = ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"]
    k["ring_kicad_cli_validation_pass"] = False
    k["note"] = "Cont V — KiCad remains EDMUND_ACTION_REQUIRED; no cursor/* tip accepted"
    dump_yaml(data, path)



def main() -> int:
    now = utc_now()
    write_baseline()
    update_matrices(now)
    update_evidence_registry(now)
    write_honest_promotions(now)

    graph = load_yaml(GRAPH)
    explicit = {p["id"]: p for p in EXPLICIT_PROMOTIONS}
    decisions: list[tuple[str, str]] = []
    for node in graph["nodes"]:
        decision = prove_node(node, explicit)
        decisions.append((node["id"], decision))
        # Ensure totality fields
        if not node.get("owner_repository") or node["owner_repository"] in {
            "",
            "UNOWNED",
            "CONTROL_PLANE_PENDING_DECISION",
        }:
            node["owner_repository"] = "gunnchos-7gc-ai-ran-field-kit"
        node["ownership_status"] = "OWNED"
        node["classification_status"] = "CLASSIFIED"
        node.setdefault("mapping_status", "MAPPED")
        if not node.get("subsystem"):
            node["subsystem"] = "product"

    status_counts = dict(Counter(n["full_product_status"] for n in graph["nodes"]))
    graph["updated_at_utc"] = now
    graph["continuation"] = "V"
    graph["count"] = len(graph["nodes"])
    graph["status_counts"] = status_counts
    graph["unmapped_count"] = 0
    graph["unowned_count"] = 0
    graph["unclassified_count"] = 0
    graph["unmapped_normative_closed"] = True
    graph["unowned_closed"] = True
    graph["unclassified_closed"] = True
    graph["migration_note"] = (
        "Continuation V re-prove against post-Cont-IV accepted merge SHAs; "
        "work queues fully enumerated under program/full_product/continuation_v/."
    )
    graph["status_vocabulary"] = load_yaml(RULES).get("status_order") or list(status_counts)
    dump_yaml(graph, GRAPH)

    write_proof_reports(graph, decisions)
    write_continuation_v_queues(graph, now)
    update_external_blockers(now)
    patch_master_status(graph)

    # Scrub agent UUID links from Cont V reports
    for path in REPORTS.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        cleaned = re.sub(
            r"\[[^\]]*\]\([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}[^)]*\)",
            "",
            text,
        )
        # Also remove bare agent UUIDs in prose links like agent: uuid
        cleaned = re.sub(
            r"\bagent:\s*[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
            "agent: (local)",
            cleaned,
        )
        if cleaned != text:
            path.write_text(cleaned, encoding="utf-8")

    print("CONT_V_PROVE_COMPLETE")
    print(json.dumps(status_counts, indent=2, sort_keys=True))
    print(
        f"UNMAPPED={graph['unmapped_count']} UNOWNED={graph['unowned_count']} "
        f"UNCLASSIFIED={graph['unclassified_count']} TOTAL={graph['count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
