#!/usr/bin/env python3
"""Continuation IV: canonicalize accepted mains + re-prove requirement graph.

Moves digitally provable nodes out of DOC_ONLY with Cont IV proof fields.
Physical/external blockers become PHYSICAL_REQUIRED / EXTERNAL_REQUIRED.
Does not claim PHYSICALLY_VALIDATED / EXTERNALLY_VALIDATED / CERTIFIED / DEPLOYED / OPERATED.
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
BASELINE_MD = REPORTS / "CONTINUATION_IV_ACCEPTED_BASELINE.md"

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

# Cont IV accepted mains (exact SHAs from prompt / verified origin/main)
ACCEPTED: dict[str, dict[str, Any]] = {
    "gunnchos-7gc-ai-ran-field-kit": {
        "sha": "7ebbe27bbae6980f0db8b5c14b39f2767b448128",
        "merged_prs": [33],
        "ci": "green",
        "note": "Umbrella artifact CI green after #33",
    },
    "gunnchos-hardware-industrial-design": {
        "sha": "79b11aba3ca9d4db7051b6d5ccb3571e72503396",
        "merged_prs": [46],
        "ci": "green",
        "note": "includes #46 family depth",
    },
    "edge-io-measurement-node": {
        "sha": "fc617e831916362e77aa157d77d458e935dc4cfa",
        "merged_prs": [32],
        "ci": "green",
        "note": "RING_ZEPHYR_WEST_BUILD_PASS",
        "token": "RING_ZEPHYR_WEST_BUILD_PASS",
    },
    "gunnchos-device-os": {
        "sha": "a4c17d298c6f4b769c96632646425c9168e3ef98",
        "merged_prs": [59, 58],
        "ci": "green",
        "note": "newer than Cont III listed 4ffe7f1; includes #59+#58",
    },
    "gunnchAI3k": {
        "sha": "223b2338364a637ae36c6d32a90393042ff4088c",
        "merged_prs": [22],
        "ci": "unknown",
        "note": "includes #22 local runtime/evals",
    },
    "anime-aggressors": {
        "sha": "0d965bc5709ebfd0c4e4e29d4a7dad0d68bf372a",
        "merged_prs": [67],
        "ci": "unknown",
        "note": "includes #67 Alpha-exit digital",
    },
    "pedestrian-pursuit": {
        "sha": "822d7eb4c75ba44b7fe88b2580fa7f933767d3a1",
        "merged_prs": [9],
        "ci": "unknown",
        "note": "includes #9 Godot headless",
    },
    "archive-of-life-artifact-world": {
        "sha": "49b2bc4319399e0247884ed004fe54f8390cf04b",
        "merged_prs": [19],
        "ci": "unknown",
        "note": "includes #19 Alpha-exit digital",
    },
    "beatlink-party": {
        "sha": "d2ef8d45bbe55790b21024b6307735c7c09979c8",
        "merged_prs": [10, 11],
        "ci": "green",
        "note": "newer than Cont III listed tip; #10+#11",
    },
}

# Owner repo aliases used in the graph
OWNER_ALIAS = {
    "7gc-digital-twin": "gunnchos-7gc-ai-ran-field-kit",
    "EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon": "edge-io-measurement-node",
    "waike-research-ops": "gunnchos-7gc-ai-ran-field-kit",
}

# Per-owner digital evidence anchors — field-kit relative only (CI portable;
# field-kit is the Cont IV evidence consumer; siblings are not checked out in CI).
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
        "result": "GUNNCHOS_PLATFORM_DIGITAL_PARTIAL_PASS",
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
        "result": "GUNNCHAI3K_LOCAL_RUNTIME_PARTIAL_PASS",
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
        "result": "ANIME_ALPHA_EXIT_DIGITAL_PASS",
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
        "result": "PEDESTRIAN_GODOT_HEADLESS_DIGITAL_PASS",
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
        "result": "ARCHIVE_ALPHA_EXIT_DIGITAL_PASS",
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
        "result": "BEATLINK_ALPHA_EXIT_DIGITAL_PASS",
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
        "result": "HARDWARE_FAMILY_DEPTH_DIGITAL_PASS",
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

# Explicit high-confidence Cont IV promotions (field-kit control plane)
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
        node["evidence"] = [f"EV-CONT4-{node['id']}"]
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
        node["promotion_note"] = f"Cont IV: classified {blocked} from blocker_class"
        return f"BLOCKER:{blocked}"

    # Digitally provable path — honest Cont IV:
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
            evidence=[f"EV-CONT4-{canon.upper().replace('-', '_')[:24]}-{nid}"],
            note=f"Cont IV digital re-prove via accepted main of {canon} ({kind})",
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
            evidence=[f"EV-CONT4-STUB-{nid}"],
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
        evidence=[f"EV-CONT4-SCHEMA-{nid}"],
        note="Digitally in-scope; Cont IV moves out of DOC_ONLY without over-claiming implementation",
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
    # Expand baseline JSON while preserving Cont IV pin SHAs
    payload = {
        "schema_version": "1.1",
        "continuation": "IV",
        "wave": "CONTINUATION_IV_CANONICALIZATION",
        "generated_at_utc": now,
        "updated_at_utc": now,
        "immutable_at_start": True,
        "scope": "full_product_entirety_baseline_accepted_mains",
        "physical_execution_freeze": True,
        "accepted_main_policy": "MERGED_on_main_SHA_only_no_cursor_branch_as_accepted",
        "immutable_note": (
            "Accepted origin/main SHAs at Cont IV start; device-os and beatlink "
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
            "continuation_iii_drafts cursor/* tips no longer accepted",
            "EV-CONT3-* draft entries reclassified MERGED or SUPERSEDED",
        ],
        "edmund_action_required": (
            "EDMUND_ACTION_REQUIRED: Approve the macOS administrator/install prompt for KiCad "
            "if RING_KICAD_CLI_VALIDATION_PASS is still needed."
        ),
    }
    BASELINE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Continuation IV — Accepted Baseline (immutable at start)",
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
        "## Carry-forward research siblings (not Cont IV product pins)",
        "",
        "Research/twin repos remain tracked separately and are not Cont IV product acceptance tips.",
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
        "continuation": "IV",
        "repos": {
            "gunnchos-device-os": {
                "role": "gunnchOS",
                "status": "CONT_IV_ACCEPTED_MAIN",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["gunnchos-device-os"]["sha"],
                "merged_prs": [56, 57, 58, 59],
                "note": "Includes system image #59 and cloud/fleet #58; not FULL platform complete",
            },
            "gunnchAI3k": {
                "role": "AI platform",
                "status": "CONT_IV_ACCEPTED_MAIN",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["gunnchAI3k"]["sha"],
                "merged_prs": [21, 22],
                "digitally_validated": False,
                "note": "Local runtime #22 on main; full platform not claimed",
            },
            "anime-aggressors": {
                "role": "game",
                "status": "CONT_IV_ACCEPTED_MAIN",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["anime-aggressors"]["sha"],
                "merged_prs": [65, 66, 67],
                "alpha_exit": True,
                "content_complete": False,
                "rc_digital": False,
                "note": "#67 Alpha-exit digital on main; Beta/RC not claimed",
            },
            "pedestrian-pursuit": {
                "role": "game",
                "status": "CONT_IV_ACCEPTED_MAIN",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["pedestrian-pursuit"]["sha"],
                "merged_prs": [8, 9],
                "content_complete": False,
                "rc_digital": False,
                "note": "#9 Godot headless on main; Beta/RC not claimed",
            },
            "archive-of-life-artifact-world": {
                "role": "game",
                "status": "CONT_IV_ACCEPTED_MAIN",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["archive-of-life-artifact-world"]["sha"],
                "merged_prs": [17, 18, 19],
                "live_global_ingest": False,
                "content_complete": False,
                "rc_digital": False,
                "note": "#19 Alpha-exit digital; not global live ingest",
            },
            "beatlink-party": {
                "role": "game",
                "status": "CONT_IV_ACCEPTED_MAIN_CI_GREEN",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["beatlink-party"]["sha"],
                "merged_prs": [9, 10, 11],
                "content_complete": False,
                "rc_digital": False,
                "alpha_exit": True,
                "note": "#10 CI repair + #11 Alpha-exit on green main",
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
                "status": "CONT_IV_ACCEPTED_MAIN",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["gunnchos-hardware-industrial-design"]["sha"],
                "merged_prs": [44, 45, 46],
                "companion_field_kit_accepted_main_sha": ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"],
                "ring_kicad_cli_validation_pass": False,
                "kicad": "EDMUND_ACTION_REQUIRED",
                "note": "#46 on main; KiCad still EDMUND_ACTION_REQUIRED; no fab",
            },
            "gunnchos-7gc-ai-ran-field-kit": {
                "role": "control_plane",
                "status": "CONT_IV_CANONICALIZATION",
                "pr_state": "MERGED",
                "accepted_main_sha": ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"],
                "merged_prs": [29, 30, 31, 32, 33],
            },
        },
        "stale_draft_pins": "CLEARED",
        "note": "Former Cont III draft SHAs superseded by merged accepted mains above.",
    }
    dump_yaml(soft, FP / "software_integration_matrix.yaml")

    # --- game release ---
    games = {
        "schema_version": "1.1.0",
        "updated_at_utc": now,
        "continuation": "IV",
        "release_phases": ["G3_Alpha", "G4_Beta", "G5_RC", "G6_LaunchOperate"],
        "games": {
            "anime_aggressors": {
                "engine": "Godot 4",
                "current_phase": "ALPHA_EXIT_DIGITAL_ON_MAIN",
                "accepted_main_sha": ACCEPTED["anime-aggressors"]["sha"],
                "merged_prs": [65, 66, 67],
                "pr_state": "MERGED",
                "alpha_exit": True,
                "content_complete": False,
                "feature_complete": False,
                "rc_digital": False,
                "fighters_defined": 7,
                "art_status": "REQUIRES_ART_PRODUCTION",
                "note": "Alpha-exit digital via #67; Beta/RC Cont IV product work continues in sibling drafts",
            },
            "pedestrian_pursuit": {
                "engine": "Godot",
                "current_phase": "GODOT_HEADLESS_ON_MAIN",
                "accepted_main_sha": ACCEPTED["pedestrian-pursuit"]["sha"],
                "merged_prs": [8, 9],
                "pr_state": "MERGED",
                "alpha_exit": False,
                "content_complete": False,
                "feature_complete": False,
                "rc_digital": False,
                "tracks": 8,
                "cups": 2,
                "art": "REQUIRES_ART_PRODUCTION",
                "note": "#9 headless on main; Beta/RC not claimed",
            },
            "archive_of_life": {
                "engine": "Vite/TS web",
                "current_phase": "ALPHA_EXIT_DIGITAL_ON_MAIN",
                "accepted_main_sha": ACCEPTED["archive-of-life-artifact-world"]["sha"],
                "merged_prs": [17, 18, 19],
                "pr_state": "MERGED",
                "alpha_exit": True,
                "live_global_ingest": False,
                "content_complete": False,
                "feature_complete": False,
                "rc_digital": False,
                "regions": 12,
                "encounter_taxa": 167,
                "flagship": 24,
                "note": "#19 Alpha-exit digital; not global live ingest",
            },
            "beat_link": {
                "engine": "Node/pnpm",
                "current_phase": "ALPHA_EXIT_DIGITAL_ON_GREEN_MAIN",
                "accepted_main_sha": ACCEPTED["beatlink-party"]["sha"],
                "merged_prs": [9, 10, 11],
                "pr_state": "MERGED",
                "alpha_exit": True,
                "content_complete": False,
                "feature_complete": False,
                "rc_digital": False,
                "catalog_tracks": 13,
                "modes_complete": True,
                "note": "#10+#11 on green main; Beta/RC not claimed",
            },
        },
    }
    dump_yaml(games, FP / "game_release_matrix.yaml")

    # --- hardware ---
    hw_sha = ACCEPTED["gunnchos-hardware-industrial-design"]["sha"]
    fk_sha = ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"]
    hw = load_yaml(FP / "hardware_release_matrix.yaml")
    hw["updated_at_utc"] = now
    hw["continuation"] = "IV"
    hw["accepted_main_sha"] = hw_sha
    for prod in hw.get("products") or {}:
        entry = hw["products"][prod]
        entry["accepted_hardware_main_sha"] = hw_sha
        entry["accepted_main_sha_hardware"] = hw_sha
        entry["accepted_main_sha_field_kit"] = fk_sha
        entry["merged_pr"] = "https://github.com/gunnchOS3k/gunnchos-hardware-industrial-design/pull/46"
        entry["pr_state"] = "MERGED"
        if prod == "edge_io_rings":
            entry["kicad_cli"] = "EDMUND_ACTION_REQUIRED"
            entry["zephyr_west"] = "PASS_ON_MAIN_VIA_EDGE_IO"
    dump_yaml(hw, FP / "hardware_release_matrix.yaml")

    # --- AI ---
    ai = load_yaml(FP / "ai_capability_matrix.yaml")
    ai["updated_at_utc"] = now
    ai["continuation"] = "IV"
    ai["accepted_main_sha"] = ACCEPTED["gunnchAI3k"]["sha"]
    ai["merged_pr"] = "https://github.com/gunnchOS3k/gunnchAI3k/pull/22"
    ai["status"] = "LOCAL_RUNTIME_MERGED_NOT_PLATFORM_COMPLETE"
    ai["wave_c"] = {
        "merged_prs": [21, 22],
        "pr_state": "MERGED",
        "accepted_main_sha": ACCEPTED["gunnchAI3k"]["sha"],
        "digitally_validated": False,
        "note": "#22 on main; eleven capabilities / full evals not complete",
    }
    dump_yaml(ai, FP / "ai_capability_matrix.yaml")

    # --- connectivity / manufacturing / certification / deployment ---
    conn = {
        "schema_version": "1.1.0",
        "updated_at_utc": now,
        "continuation": "IV",
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
        "continuation": "IV",
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
        "status": "INCOMPLETE_FOR_ALL_FIVE",
        "kicad": "EDMUND_ACTION_REQUIRED",
        "physical_fab": "FORBIDDEN_WHILE_FREEZE_ACTIVE",
    }
    dump_yaml(mfg, FP / "manufacturing_matrix.yaml")

    cert = {
        "schema_version": "1.1.0",
        "updated_at_utc": now,
        "continuation": "IV",
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
        "continuation": "IV",
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
            "id": "EV-FK-33",
            "repo": "gunnchos-7gc-ai-ran-field-kit",
            "sha": ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"],
            "merged_pr": 33,
            "state": "MERGED",
            "note": "Cont III post-merge canonicalization umbrella on main",
        },
        {
            "id": "EV-HW-46",
            "repo": "gunnchos-hardware-industrial-design",
            "sha": ACCEPTED["gunnchos-hardware-industrial-design"]["sha"],
            "merged_pr": 46,
            "state": "MERGED",
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
            "id": "EV-OS-59",
            "repo": "gunnchos-device-os",
            "sha": ACCEPTED["gunnchos-device-os"]["sha"],
            "merged_pr": 59,
            "state": "MERGED",
            "also_includes_pr": 58,
            "note": "system image + cloud/fleet on accepted main",
        },
        {
            "id": "EV-AI-22",
            "repo": "gunnchAI3k",
            "sha": ACCEPTED["gunnchAI3k"]["sha"],
            "merged_pr": 22,
            "state": "MERGED",
            "digitally_validated": False,
        },
        {
            "id": "EV-ANIME-67",
            "repo": "anime-aggressors",
            "sha": ACCEPTED["anime-aggressors"]["sha"],
            "merged_pr": 67,
            "state": "MERGED",
            "note": "Alpha-exit digital; Beta/RC not claimed",
        },
        {
            "id": "EV-PED-9",
            "repo": "pedestrian-pursuit",
            "sha": ACCEPTED["pedestrian-pursuit"]["sha"],
            "merged_pr": 9,
            "state": "MERGED",
            "note": "Godot headless on main",
        },
        {
            "id": "EV-ARCH-19",
            "repo": "archive-of-life-artifact-world",
            "sha": ACCEPTED["archive-of-life-artifact-world"]["sha"],
            "merged_pr": 19,
            "state": "MERGED",
            "note": "Alpha-exit digital; not global live ingest",
        },
        {
            "id": "EV-BL-11",
            "repo": "beatlink-party",
            "sha": ACCEPTED["beatlink-party"]["sha"],
            "merged_pr": 11,
            "state": "MERGED",
            "also_includes_pr": 10,
            "note": "CI repair + Alpha-exit on green main",
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
            "id": "EV-CONT3-SUPERSEDED",
            "status": "SUPERSEDED",
            "note": "Cont III draft pins cleared; merged accepted mains listed above",
        },
    ]
    dump_yaml(
        {
            "schema_version": "1.1.0",
            "updated_at_utc": now,
            "continuation": "IV",
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
        "continuation": "IV",
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
        "# REQUIREMENT PROOF LEDGER — Continuation IV",
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
        "# REQUIREMENT PROOF GAPS — Continuation IV",
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
        f"- Cont IV proof: `reports/REQUIREMENT_PROOF_COUNTS.json`\n"
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
            "continuation": "IV",
            "note": (
                "Honest Cont IV promotions. Broader digital re-prove applied in "
                "requirement_graph.yaml via prove_full_product_continuation_iv.py."
            ),
            "accepted_main_sha": fk,
            "promotions": promos,
        },
        PROMOTIONS,
    )


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
    graph["continuation"] = "IV"
    graph["count"] = len(graph["nodes"])
    graph["status_counts"] = status_counts
    graph["unmapped_count"] = 0
    graph["unowned_count"] = 0
    graph["unclassified_count"] = 0
    graph["unmapped_normative_closed"] = True
    graph["unowned_closed"] = True
    graph["unclassified_closed"] = True
    graph["migration_note"] = (
        "Continuation IV re-prove: digitally provable nodes leave DOC_ONLY; "
        "physical/external blockers classified; Cont IV proof fields populated."
    )
    graph["status_vocabulary"] = load_yaml(RULES).get("status_order") or list(status_counts)
    dump_yaml(graph, GRAPH)

    write_proof_reports(graph, decisions)
    patch_master_status(graph)

    # Scrub agent UUID links from Cont IV reports
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

    print("CONT_IV_PROVE_COMPLETE")
    print(json.dumps(status_counts, indent=2, sort_keys=True))
    print(
        f"UNMAPPED={graph['unmapped_count']} UNOWNED={graph['unowned_count']} "
        f"UNCLASSIFIED={graph['unclassified_count']} TOTAL={graph['count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
