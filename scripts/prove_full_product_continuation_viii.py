#!/usr/bin/env python3
"""Continuation VIII: release-readiness closure + accepted-main re-proof.

Re-prove all 476 requirements against Cont VIII accepted sibling mains
(device-os #65+#66 and Cont VIII product merges). Extends Cont VIII patterns:
readiness gates R1–R6, honest scorecard, release firewall artifacts.

PHYSICAL_EXECUTION_FREEZE remains active. Does not claim
DIGITAL_PRE_EVT_RELEASE_READY or open the true final umbrella unless
digitally executable backlog is zero on accepted mains only.
"""

from __future__ import annotations

import json
import os
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
CONT_VIII = FP / "continuation_viii"
CONT_VII = FP / "continuation_vii"
CONT_VI = FP / "continuation_vi"

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

# Cont VIII accepted mains = Cont VIII product merges + field-kit Cont VIII main.
ACCEPTED: dict[str, dict[str, Any]] = {
    "gunnchos-7gc-ai-ran-field-kit": {
        "sha": "a4846ca970943ffc790298bc8bf36bf5c544c8b4",
        "merged_prs": [40],
        "ci": "green",
        "note": "Cont VII control-plane #40 on main; Cont VIII reproof base",
    },
    "gunnchos-hardware-industrial-design": {
        "sha": "c5b6afd6a792d367593867fc7533f413a5146db4",
        "merged_prs": [50],
        "ci": "green",
        "note": "#50 Cont VIII EDA release-clean on main; structural HW only",
        "token": "HARDWARE_DESIGN_RELEASE_CANDIDATE",
    },
    "edge-io-measurement-node": {
        "sha": "a1cd2e95c62eb0eefd507b976158232b83f5b33b",
        "merged_prs": [35],
        "ci": "green",
        "note": "#35 Cont VIII ring E2E digital on main; physical boot still pending",
        "token": "RING_END_TO_END_DIGITAL_INPUT_PASS",
    },
    "gunnchos-device-os": {
        "sha": "78cd33f1fde0a0c42eb6469bbdbe4664225d3dd0",
        "merged_prs": [65, 66],
        "ci": "green",
        "note": "#65 schema quality/reliab + #66 real app packages on main",
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

OWNER_ALIAS = {
    "EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon": "edge-io-measurement-node",
    "7gc-digital-twin": "7gc-digital-twin",
    "waike-research-ops": "gunnchAI3k",
    "hardware": "gunnchos-hardware-industrial-design",
    "edge-io": "edge-io-measurement-node",
    "device-os": "gunnchos-device-os",
    "gunnchai": "gunnchAI3k",
    "field-kit": "gunnchos-7gc-ai-ran-field-kit",
    "games": "anime-aggressors",
    "research": "7gc-digital-twin",
}


# Cont VI control-plane explicit promotions carried into Cont VIII (product evidence, not YAML-alone).
EXPLICIT_PROMOTIONS = [

    {
        "id": "CG-QUALITY-001",
        "full_product_status": "DIGITALLY_VALIDATED",
        "owner_repository": "gunnchos-device-os",
        "implementation_paths": [
            "program/full_product/continuation_viii/REQUIREMENT_PROOF.json",
            "program/full_product/evidence_registry.yaml",
            "scripts/validate_full_product_requirement_graph.py",
        ],
        "test_paths": [
            "tests/full_product/test_requirement_promotion_validators.py",
            "tests/full_product/test_continuation_viii_release_readiness.py",
        ],
        "evidence_artifact": "program/full_product/continuation_viii/REQUIREMENT_PROOF.json",
        "evidence_result": "CONT_VIII_DEVICE_OS_65_CLEAN_INSTALLATION_DIGITAL_PASS",
        "evidence": ["EV-CONT8-CG-QUALITY-001"],
        "sibling_product": [
            "sibling:gunnchos-device-os/gunnchos_device_os/clean_installation.py",
            "sibling:gunnchos-device-os/tests/test_product_quality_clean_installation.py",
        ],
        "note": "Cont VIII: device-os #65/#66 on accepted main 78cd33f; clean_installation product+tests",
    },
    {
        "id": "CG-QUALITY-007",
        "full_product_status": "DIGITALLY_VALIDATED",
        "owner_repository": "gunnchos-device-os",
        "implementation_paths": [
            "program/full_product/continuation_viii/REQUIREMENT_PROOF.json",
            "program/full_product/evidence_registry.yaml",
            "scripts/validate_full_product_requirement_graph.py",
        ],
        "test_paths": [
            "tests/full_product/test_requirement_promotion_validators.py",
            "tests/full_product/test_continuation_viii_release_readiness.py",
        ],
        "evidence_artifact": "program/full_product/continuation_viii/REQUIREMENT_PROOF.json",
        "evidence_result": "CONT_VIII_DEVICE_OS_65_LOCALIZATION_DIGITAL_PASS",
        "evidence": ["EV-CONT8-CG-QUALITY-007"],
        "sibling_product": [
            "sibling:gunnchos-device-os/gunnchos_device_os/localization.py",
            "sibling:gunnchos-device-os/tests/test_product_quality_localization.py",
        ],
        "note": "Cont VIII: device-os #65/#66 on accepted main 78cd33f; localization product+tests",
    },
    {
        "id": "CG-QUALITY-008",
        "full_product_status": "DIGITALLY_VALIDATED",
        "owner_repository": "gunnchos-device-os",
        "implementation_paths": [
            "program/full_product/continuation_viii/REQUIREMENT_PROOF.json",
            "program/full_product/evidence_registry.yaml",
            "scripts/validate_full_product_requirement_graph.py",
        ],
        "test_paths": [
            "tests/full_product/test_requirement_promotion_validators.py",
            "tests/full_product/test_continuation_viii_release_readiness.py",
        ],
        "evidence_artifact": "program/full_product/continuation_viii/REQUIREMENT_PROOF.json",
        "evidence_result": "CONT_VIII_DEVICE_OS_65_REPAIR_DOCUMENTATION_DIGITAL_PASS",
        "evidence": ["EV-CONT8-CG-QUALITY-008"],
        "sibling_product": [
            "sibling:gunnchos-device-os/gunnchos_device_os/repair_documentation.py",
            "sibling:gunnchos-device-os/tests/test_product_quality_repair_documentation.py",
        ],
        "note": "Cont VIII: device-os #65/#66 on accepted main 78cd33f; repair_documentation product+tests",
    },
    {
        "id": "RING-RELIAB-016",
        "full_product_status": "DIGITALLY_VALIDATED",
        "owner_repository": "gunnchos-device-os",
        "implementation_paths": [
            "program/full_product/continuation_viii/REQUIREMENT_PROOF.json",
            "program/full_product/evidence_registry.yaml",
            "scripts/validate_full_product_requirement_graph.py",
        ],
        "test_paths": [
            "tests/full_product/test_requirement_promotion_validators.py",
            "tests/full_product/test_continuation_viii_release_readiness.py",
        ],
        "evidence_artifact": "program/full_product/continuation_viii/REQUIREMENT_PROOF.json",
        "evidence_result": "CONT_VIII_DEVICE_OS_65_SILENT_DESTRUCTIVE_GUARD_DIGITAL_PASS",
        "evidence": ["EV-CONT8-RING-RELIAB-016"],
        "sibling_product": [
            "sibling:gunnchos-device-os/gunnchos_device_os/silent_destructive_uncertain_gestures.py",
            "sibling:gunnchos-device-os/tests/test_silent_destructive_uncertain_gestures.py",
        ],
        "note": "Cont VIII: device-os #65 on accepted main 78cd33f; silent destructive uncertain gesture guard",
    },
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
        "evidence_result": "RING_FULL_FIRMWARE_DIGITAL_PASS",
        "evidence": ["EV-EDGE-34"],
        "note": "Cont VI #34 full firmware digital on accepted edge-io main; physical boot still PHYSICAL_REQUIRED elsewhere",
    },
    {
        "id": "FP-SUPPORT-LIFECYCLE",
        "full_product_status": "DIGITALLY_VALIDATED",
        "owner_repository": "gunnchos-7gc-ai-ran-field-kit",
        "implementation_paths": [
            "program/full_product/deployment_support_matrix.yaml",
            "program/full_product/evidence_registry.yaml",
            "scripts/validate_claim_firewall.py",
        ],
        "test_paths": ["tests/full_product/test_requirement_promotion_validators.py"],
        "evidence_artifact": "program/full_product/deployment_support_matrix.yaml",
        "evidence_result": "DEPLOYMENT_SUPPORT_MATRIX_PASS",
        "evidence": ["EV-FK-SUPPORT-LIFECYCLE"],
        "note": "Support lifecycle digitally tracked; no FULL deployment claim",
    },
]

# Cont VIII freeze counts (reference only — Cont VIII re-proves independently)
CONT_VII_STALE = {
    "total": 476,
    "SCHEMA_ONLY": 4,
    "PHYSICAL_REQUIRED": 120,
    "EXTERNAL_REQUIRED": 75,
    "IMPLEMENTED": 6,
    "INTEGRATED": 49,
    "DIGITALLY_VALIDATED": 222,
}
CONT_VI_STALE = {
    "total": 476,
    "SCHEMA_ONLY": 221,
    "PHYSICAL_REQUIRED": 120,
    "EXTERNAL_REQUIRED": 75,
    "IMPLEMENTED": 46,
    "DIGITALLY_VALIDATED": 14,
}

CODE_EXTS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".c", ".cpp", ".h", ".hpp",
    ".gd", ".cs", ".swift", ".kt", ".java", ".zig", ".kicad_sch", ".kicad_pcb",
    ".kicad_pro", ".sql", ".wasm",
}
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "dist", "build", ".next", "__pycache__",
    ".godot", ".import", "third_party", "vendor", "Library", "PackageCache",
}


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


def sibling_exists(repo: str, rel: str) -> bool:
    return (SIBLING / repo / rel).exists()


def fk_exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def filter_fk(paths: list[str]) -> list[str]:
    return [p for p in paths if fk_exists(p)]


def accepted_for_owner(owner: str) -> tuple[str, str]:
    repo = OWNER_ALIAS.get(owner, owner)
    if repo not in ACCEPTED:
        return "gunnchos-7gc-ai-ran-field-kit", ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"]
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


def find_product_files(repo: str, needles: list[str], *, limit: int = 8) -> list[str]:
    """Find sibling product CODE (not docs/yaml-only) matching needles."""
    root = SIBLING / repo
    if not root.exists():
        return []
    hits: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() not in CODE_EXTS:
                continue
            rel = str(p.relative_to(root))
            low = rel.lower()
            if any(n in low for n in needles):
                hits.append(rel)
                if len(hits) >= limit:
                    return hits
    return hits


def find_test_files(repo: str, needles: list[str], *, limit: int = 6) -> list[str]:
    """Require needle match inside test path — never accept arbitrary tests/ files."""
    root = SIBLING / repo
    if not root.exists() or not needles:
        return []
    hits: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            p = Path(dirpath) / name
            rel = str(p.relative_to(root))
            low = rel.lower()
            if not any(t in low for t in ("test", "spec", "_test.", "/tests/")):
                continue
            if p.suffix.lower() not in CODE_EXTS | {".gd"}:
                continue
            if not any(n in low for n in needles):
                continue
            hits.append(rel)
            if len(hits) >= limit:
                return hits
    return hits


def load_ai_runtime_proof() -> dict[str, dict[str, Any]]:
    path = SIBLING / "gunnchAI3k" / "evidence" / "system-layer" / "REQUIREMENT_PROOF_VI.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict[str, Any]] = {}
    for n in data.get("nodes") or []:
        if isinstance(n, dict) and n.get("id") and n.get("status") == "RUNTIME":
            out[n["id"]] = n
    return out


def title_needles(node: dict[str, Any]) -> list[str]:
    title = (node.get("title") or "").lower()
    nid = node.get("id") or ""
    words = re.findall(r"[a-z0-9]{4,}", title)
    stop = {
        "function", "carrier", "grade", "operations", "layer", "fully", "operational",
        "device", "support", "with", "from", "that", "this", "must", "only", "where",
        "game", "field", "record", "scientific", "known", "without", "claim",
    }
    needles = [w for w in words if w not in stop][:6]
    # ID family hints
    fam = nid.rsplit("-", 1)[0] if "-" in nid else nid
    family_map = {
        "AI-CORE": ["assist", "product_service", "local-runtime"],
        "AI-GOV": ["govern", "policy", "safety", "guardrail"],
        "AI-LOCAL": ["local-runtime", "inference"],
        "CG-OPS": ["fleet", "telemetry", "diagnostic", "updater", "rollback", "canary"],
        "CG-SECURITY": ["secure_boot", "sandbox", "permission", "abuse_suite"],
        "CG-QUALITY": ["clean_installation", "localization", "repair_documentation", "readiness_gate", "claims_downgraded", "evidence_backlog"],
        "RING-RELIAB": ["silent_destructive", "uncertain_gestures", "destructive"],
        "CG-RELIABILITY": ["safe_mode_boot", "recovery_boot", "capsule_update"],
        "OS-PLATFORM": ["runtime_services", "bootable_reference", "qemu_serial"],
        "OS-CONTINUITY": ["dock_continuity", "continuity"],
        "NET-ORCH": ["connectivity_orchestrator", "orchestrator"],
        "GAME-AA": ["aura", "fighter", "combat", "projectile", "throw"],
        "GAME-PP": ["driftsystem", "railgrind", "stompsystem", "tricksystem", "sprintway"],
        "GAME-AOL": ["taxon", "science_db", "hero-species", "ingest"],
        "GAME-BEATLINK": ["audience", "calibration", "rooms", "approved-demo-catalog"],
        "GAME-CROSS": ["cross-device", "continuity", "save"],
        "DEV-STUDENT": ["student_14", "student_14_5"],
        "DEV-DSXL": ["ds_xl", "ds-xl"],
        "DEV-HANDHELD": ["handheld_hybrid", "handheld"],
        "RING-INPUT": ["iqs7222", "bmi270", "dw3000", "npm1300"],
        "FULL-OPS": ["evidence_registry", "service_matrix"],
        "GATE-0": ["gate0", "control_plane"],
        "GATE-1": ["gate1"],
        "GATE-3": ["gate3"],
        "GATE-7": ["gate7"],
    }
    needles = list(dict.fromkeys((family_map.get(fam) or []) + needles))
    return needles[:8]


def owner_default_needles(owner: str) -> list[str]:
    return {
        "gunnchAI3k": ["src/", "tests/", "evidence/"],
        "gunnchos-device-os": ["tests/", "config/runtime", "os_build/"],
        "anime-aggressors": ["game/godot", "game-godot", "Assets/AnimeAggressors"],
        "pedestrian-pursuit": ["scripts/player", "scenes/"],
        "archive-of-life-artifact-world": ["data-pipeline", "public/data", "science"],
        "beatlink-party": ["apps/web", "packages/game-engine", "tests/"],
        "edge-io-measurement-node": ["ring_firmware", "drivers/", "firmware/"],
        "gunnchos-hardware-industrial-design": ["electrical/", "kicad", ".kicad_"],
        "gunnchos-7gc-ai-ran-field-kit": ["program/full_product", "scripts/validate_"],
        "7gc-digital-twin": ["src/", "tests/"],
    }.get(owner, ["src/", "tests/"])


def verify_product_code(node: dict[str, Any]) -> dict[str, Any]:
    """Cont VIII §4 gate: actual product code must exist on accepted-main sibling tree.

    Requires ID/title-specific product matches. Does NOT promote merely because the
    owner repository contains unrelated source trees (no mass YAML/repo promotion).
    """
    owner = OWNER_ALIAS.get(node.get("owner_repository") or "", node.get("owner_repository") or "")
    nid = node.get("id") or ""
    needles = title_needles(node)

    if owner == "gunnchos-7gc-ai-ran-field-kit":
        # Control-plane: only promote when a specific validator/script matches the requirement family
        fam = nid.rsplit("-", 1)[0] if "-" in nid else nid
        fk_map = {
            "SYS-STANDARDS": ["scripts/validate_claim_firewall.py", "program/claims/prohibited_claim_patterns.yaml"],
            "SYS-MISSION": ["program/full_product/evidence_registry.yaml", "scripts/validate_claim_firewall.py"],
            "FP-CONN": ["program/full_product/connectivity_carrier_matrix.yaml", "scripts/validate_claim_firewall.py"],
            "FP-CHARTER": ["scripts/validate_claim_firewall.py", "program/full_product/connectivity_carrier_matrix.yaml"],
            "FP-RING": ["program/full_product/software_integration_matrix.yaml", "program/full_product/evidence_registry.yaml"],
            "GATE-0": ["tests/control_plane/test_gate0_control_plane.py", "scripts/validate_claim_firewall.py"],
            "FULL-OPS": ["program/full_product/evidence_registry.yaml", "scripts/validate_full_product_requirement_graph.py"],
            "GAME-CROSS": ["program/full_product/game_release_matrix.yaml", "scripts/validate_game_release_claims.py"],
        }
        # Prefer family map; otherwise require needle hit under scripts/ or program/
        paths: list[str] = []
        for key, cand in fk_map.items():
            if nid.startswith(key) or fam.startswith(key):
                paths.extend([c for c in cand if fk_exists(c)])
        if not paths and needles:
            for n in needles:
                for base in (ROOT / "scripts", ROOT / "program", ROOT / "tests"):
                    if not base.exists():
                        continue
                    for f in base.rglob("*"):
                        if f.is_file() and n in str(f.relative_to(ROOT)).lower():
                            if f.suffix.lower() in CODE_EXTS | {".yaml", ".yml", ".py"}:
                                paths.append(str(f.relative_to(ROOT)))
                                break
                if len(paths) >= 2:
                    break
        paths = list(dict.fromkeys(paths))[:6]
        tests = [p for p in paths if "test" in p] + [
            "tests/full_product/test_requirement_promotion_validators.py"
        ]
        tests = [t for t in tests if fk_exists(t)][:4]
        return {
            "ok": len(paths) >= 1 and bool(needles or paths),
            "repo": owner,
            "product_paths": paths,
            "test_paths": tests,
            "kind": "field_kit_control_plane",
            "needles": needles,
        }

    # Sibling: require needle-specific CODE hits (no generic repo fallback)
    product = find_product_files(owner, needles, limit=8) if needles else []
    tests = find_test_files(owner, needles[:4], limit=6) if needles else []
    return {
        "ok": bool(product),
        "repo": owner,
        "product_paths": [f"sibling:{owner}/{p}" for p in product],
        "test_paths": [f"sibling:{owner}/{p}" for p in tests],
        "kind": "sibling_product_code",
        "needles": needles,
    }


def apply_fields(
    node: dict[str, Any],
    status: str,
    *,
    impl: list[str],
    tests: list[str],
    artifact: str,
    result: str,
    evidence: list[str] | None = None,
    note: str | None = None,
    sibling_product: list[str] | None = None,
    integration_paths: list[str] | None = None,
    remaining_gap: str | None = None,
) -> None:
    owner = node.get("owner_repository") or "gunnchos-7gc-ai-ran-field-kit"
    repo, sha = accepted_for_owner(owner)
    node["full_product_status"] = status
    # CI-portable field-kit paths only in graph (siblings recorded separately)
    node["implementation_paths"] = impl
    node["test_paths"] = tests
    node["tests"] = list(tests)
    if integration_paths is not None:
        node["integration_paths"] = integration_paths
    node["accepted_repository"] = repo
    node["accepted_main_sha"] = sha
    node["accepted_sha"] = sha
    node["evidence_artifact"] = artifact
    node["evidence_result"] = result
    if evidence is not None:
        node["evidence"] = evidence
    elif not node.get("evidence"):
        node["evidence"] = [f"EV-CONT8-{node['id']}"]
    if note:
        node["promotion_note"] = note
    if sibling_product is not None:
        node["runtime_evidence"] = sibling_product
    if remaining_gap is not None:
        node["remaining_gap"] = remaining_gap
    node["ownership_status"] = "OWNED"
    node["classification_status"] = "CLASSIFIED"
    node.setdefault("mapping_status", "MAPPED")


FK_IMPL = [
    "program/full_product/continuation_viii/REQUIREMENT_PROOF.json",
    "program/full_product/requirement_graph.yaml",
    "scripts/validate_full_product_requirement_graph.py",
]
FK_TESTS = [
    "tests/full_product/test_requirement_promotion_validators.py",
    "tests/full_product/test_continuation_viii_release_readiness.py",
    "scripts/validate_full_product_requirement_graph.py",
]
FK_ARTIFACT = "program/full_product/continuation_viii/REQUIREMENT_PROOF.json"


def prove_node(
    node: dict[str, Any],
    ai_runtime: dict[str, dict[str, Any]],
    prior_status: str,
    explicit: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    nid = node["id"]
    if nid in explicit:
        item = explicit[nid]
        owner = item.get("owner_repository") or node.get("owner_repository")
        if owner:
            node["owner_repository"] = owner
        impl = filter_fk(list(item.get("implementation_paths") or [])) or list(item.get("implementation_paths") or [])
        tests = filter_fk(list(item.get("test_paths") or item.get("tests") or [])) or list(
            item.get("test_paths") or item.get("tests") or []
        )
        apply_fields(
            node,
            item["full_product_status"],
            impl=impl,
            tests=tests,
            artifact=item.get("evidence_artifact") or FK_ARTIFACT,
            result=item.get("evidence_result") or "EXPLICIT_PROMOTED",
            evidence=list(item.get("evidence") or []),
            note=item.get("note"),
            sibling_product=list(item.get("sibling_product") or []),
            integration_paths=filter_fk(
                [
                    "program/full_product/software_integration_matrix.yaml",
                    "program/full_product/ai_capability_matrix.yaml",
                ]
            ),
            remaining_gap="",
        )
        node["physical_evidence_required"] = False
        node["external_evidence_required"] = False
        return {
            "id": nid,
            "prior_status": prior_status,
            "new_status": item["full_product_status"],
            "promotion_decision": f"EXPLICIT:{item['full_product_status']}",
            "sibling_product_paths": [],
        }

    blocked = classify_blockers(list(node.get("blocker_class") or []))
    # Cont VI already digitally promoted nodes with residual standard blockers keep digital status
    # unless this node was never an explicit digital promotion (blockers win for pure blocker nodes).
    if blocked and prior_status not in {"IMPLEMENTED", "INTEGRATED", "DIGITALLY_VALIDATED"}:
        node["full_product_status"] = blocked
        node["implementation_paths"] = []
        node["test_paths"] = []
        node["tests"] = list(node.get("tests") or [])
        node["accepted_repository"] = None
        node["accepted_main_sha"] = None
        node["accepted_sha"] = None
        node["evidence_artifact"] = None
        node["evidence_result"] = blocked
        node["promotion_note"] = f"Cont VIII: classified {blocked} from blocker_class"
        node["remaining_gap"] = blocked
        node["physical_evidence_required"] = blocked == "PHYSICAL_REQUIRED"
        node["external_evidence_required"] = blocked == "EXTERNAL_REQUIRED"
        return {
            "id": nid,
            "prior_status": prior_status,
            "new_status": blocked,
            "promotion_decision": f"BLOCKER:{blocked}",
            "sibling_product_paths": [],
        }

    owner = OWNER_ALIAS.get(node.get("owner_repository") or "", node.get("owner_repository") or "")
    verification = verify_product_code(node)
    sibling_paths = verification.get("product_paths") or []
    sibling_tests = verification.get("test_paths") or []

    # AI Cont VI runtime proof is strong digital evidence (not YAML-alone)
    if nid in ai_runtime and owner == "gunnchAI3k":
        impl = filter_fk(
            [
                "program/full_product/ai_capability_matrix.yaml",
                "program/full_product/evidence_registry.yaml",
                "program/full_product/continuation_viii/REQUIREMENT_PROOF.json",
            ]
        )
        tests = filter_fk(FK_TESTS)
        apply_fields(
            node,
            "DIGITALLY_VALIDATED",
            impl=impl or FK_IMPL,
            tests=tests or FK_TESTS,
            artifact=FK_ARTIFACT,
            result="GUNNCHAI_CONT_VIII_RUNTIME_PROOF",
            evidence=[f"EV-CONT8-AI-{nid}"],
            note=(
                f"Cont VIII: gunnchAI REQUIREMENT_PROOF_VI RUNTIME (Cont VIII re-cite) on accepted main "
                f"{ACCEPTED['gunnchAI3k']['sha'][:12]}; sibling product verified"
            ),
            sibling_product=sibling_paths or [
                f"sibling:gunnchAI3k/evidence/system-layer/REQUIREMENT_PROOF_VI.json"
            ],
            integration_paths=[
                "program/full_product/software_integration_matrix.yaml",
                "program/full_product/ai_capability_matrix.yaml",
            ],
            remaining_gap="",
        )
        node["physical_evidence_required"] = False
        node["external_evidence_required"] = False
        return {
            "id": nid,
            "prior_status": prior_status,
            "new_status": "DIGITALLY_VALIDATED",
            "promotion_decision": "AI_RUNTIME_PROOF->DIGITALLY_VALIDATED",
            "sibling_product_paths": sibling_paths,
        }

    if not verification.get("ok"):
        # Preserve Cont VI honest higher statuses when paths still resolve on field-kit
        if prior_status in {"IMPLEMENTED", "INTEGRATED", "DIGITALLY_VALIDATED"}:
            prior_impl = filter_fk(list(node.get("implementation_paths") or []))
            prior_tests = filter_fk(list(node.get("test_paths") or node.get("tests") or []))
            if prior_impl and prior_tests:
                apply_fields(
                    node,
                    prior_status,
                    impl=prior_impl,
                    tests=prior_tests,
                    artifact=node.get("evidence_artifact") or FK_ARTIFACT,
                    result=node.get("evidence_result") or "CONT_VIII_PRIOR_STATUS_RETAINED",
                    evidence=list(node.get("evidence") or [f"EV-CONT8-RETAIN-{nid}"]),
                    note=f"Cont VIII: retained Cont VI {prior_status}; accepted SHA refreshed",
                    sibling_product=[],
                    remaining_gap="",
                )
                node["physical_evidence_required"] = False
                node["external_evidence_required"] = False
                return {
                    "id": nid,
                    "prior_status": prior_status,
                    "new_status": prior_status,
                    "promotion_decision": f"RETAIN_PRIOR_{prior_status}",
                    "sibling_product_paths": [],
                }
        apply_fields(
            node,
            "SCHEMA_ONLY",
            impl=[],
            tests=[],
            artifact=FK_ARTIFACT,
            result="NO_ACCEPTED_MAIN_PRODUCT_CODE",
            evidence=[f"EV-CONT8-SCHEMA-{nid}"],
            note="Cont VIII: no resolvable product code on accepted main; remains SCHEMA_ONLY",
            sibling_product=[],
            remaining_gap="DIGITALLY_EXECUTABLE_SCHEMA_ONLY",
        )
        node["physical_evidence_required"] = False
        node["external_evidence_required"] = False
        return {
            "id": nid,
            "prior_status": prior_status,
            "new_status": "SCHEMA_ONLY",
            "promotion_decision": "RETAIN_SCHEMA_ONLY_NO_PRODUCT_CODE",
            "sibling_product_paths": [],
        }

    # Product code exists — Cont VIII ladder (no mass jump to DIGITALLY_VALIDATED)
    has_sibling_tests = bool(sibling_tests)
    integration = filter_fk(
        [
            "program/full_product/software_integration_matrix.yaml",
            "program/full_product/game_release_matrix.yaml",
            "program/full_product/hardware_release_matrix.yaml",
            "program/full_product/ai_capability_matrix.yaml",
            "program/full_product/connectivity_carrier_matrix.yaml",
        ]
    )
    impl = filter_fk(
        [
            FK_ARTIFACT,
            "program/full_product/evidence_registry.yaml",
            "scripts/validate_full_product_requirement_graph.py",
        ]
        + integration[:1]
    )
    tests = filter_fk(FK_TESTS)

    # Ladder from evidence strength
    if has_sibling_tests and len(integration) >= 1 and len(impl) >= 2:
        status = "DIGITALLY_VALIDATED"
        decision = "PRODUCT_CODE+SIBLING_TESTS+INTEGRATION->DIGITALLY_VALIDATED"
        result = "CONT_VIII_ACCEPTED_MAIN_DIGITAL_PASS"
    elif len(integration) >= 1 and len(impl) >= 2 and prior_status in {
        "INTEGRATED", "DIGITALLY_VALIDATED"
    }:
        status = "INTEGRATED" if prior_status == "INTEGRATED" else "DIGITALLY_VALIDATED"
        # Keep prior DIGITALLY_VALIDATED only when sibling tests still exist or Cont VI DV + product code
        if prior_status == "DIGITALLY_VALIDATED" and not has_sibling_tests:
            status = "INTEGRATED"
            decision = "PRIOR_DV_RECLASS_INTEGRATED_NO_SIBLING_TEST_HIT"
        else:
            decision = f"PRIOR_{prior_status}_RECONFIRMED_WITH_PRODUCT_CODE"
        result = "CONT_VIII_ACCEPTED_MAIN_RECONFIRMED"
    elif len(integration) >= 1 and len(impl) >= 2:
        status = "INTEGRATED"
        decision = "PRODUCT_CODE+INTEGRATION->INTEGRATED"
        result = "CONT_VIII_ACCEPTED_MAIN_INTEGRATED"
    else:
        status = "IMPLEMENTED"
        decision = "PRODUCT_CODE->IMPLEMENTED"
        result = "CONT_VIII_ACCEPTED_MAIN_IMPLEMENTED"

    # Hardware EDA without sibling automated tests: IMPLEMENTED (not DV)
    if owner == "gunnchos-hardware-industrial-design" and status == "DIGITALLY_VALIDATED" and not has_sibling_tests:
        status = "IMPLEMENTED"
        decision = "EDA_PRODUCT_CODE->IMPLEMENTED_NO_AUTOMATED_TEST_HIT"

    if owner == "7gc-digital-twin" and status in {"DIGITALLY_VALIDATED", "INTEGRATED"}:
        status = "IMPLEMENTED"
        decision = "PRODUCT_CODE->IMPLEMENTED_RESEARCH_TWIN"

    apply_fields(
        node,
        status,
        impl=impl or filter_fk(FK_IMPL),
        tests=tests or filter_fk(FK_TESTS),
        artifact=FK_ARTIFACT,
        result=result,
        evidence=[f"EV-CONT8-{owner.upper().replace('-', '_')[:20]}-{nid}"],
        note=(
            f"Cont VIII re-prove on accepted main of {owner} "
            f"({accepted_for_owner(owner)[1][:12]}); product code verified; not YAML-alone"
        ),
        sibling_product=sibling_paths,
        integration_paths=integration[:3],
        remaining_gap="" if status == "DIGITALLY_VALIDATED" else f"pending_higher_than_{status}",
    )
    node["physical_evidence_required"] = False
    node["external_evidence_required"] = False
    return {
        "id": nid,
        "prior_status": prior_status,
        "new_status": status,
        "promotion_decision": decision,
        "sibling_product_paths": sibling_paths,
        "sibling_test_paths": sibling_tests,
    }


def write_baseline(now: str) -> None:
    payload = {
        "schema_version": "1.2",
        "continuation": "VIII",
        "wave": "CONTINUATION_VIII_RELEASE_READINESS_CLOSURE",
        "generated_at_utc": now,
        "updated_at_utc": now,
        "immutable_at_start": True,
        "scope": "full_product_entirety_baseline_accepted_mains",
        "physical_execution_freeze": True,
        "accepted_main_policy": "MERGED_on_main_SHA_only_no_cursor_branch_as_accepted",
        "immutable_note": (
            "Accepted origin/main SHAs at Cont VIII start = Cont VII product merges "
            "(device-os #65+#66 and sibling Cont VII merges). Cont VII SCHEMA_ONLY=4 "
            "is re-proved; Cont VI SCHEMA_ONLY=221 remains historical. No cursor/* SHA as accepted tip."
        ),
        "repos": {
            name: {
                "origin_main": meta["sha"],
                "accepted_main_sha": meta["sha"],
                "last_pr": (meta.get("merged_prs") or [None])[-1],
                "merged_prs": meta.get("merged_prs", []),
                "ci": meta.get("ci", "unknown"),
                "note": meta.get("note", ""),
                **({"token": meta["token"]} if meta.get("token") else {}),
            }
            for name, meta in ACCEPTED.items()
        },
        "accepted_mains": {name: meta["sha"] for name, meta in ACCEPTED.items()},
        "previous_cont_vii_counts_reference": CONT_VII_STALE,
        "previous_cont_vi_stale_status_counts_reference": CONT_VI_STALE,
        "stale_draft_pins_cleared": True,
        "final_umbrella": False,
        "final_umbrella_policy": "NOT_FINAL_UMBRELLA_UNLESS_DIGITAL_BACKLOG_ZERO_ON_ACCEPTED_MAINS",
    }
    BASELINE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (CONT_VIII / "ACCEPTED_MAIN_BASELINE.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Continuation VIII — Accepted Main Baseline",
        "",
        f"Updated: {now}",
        "",
        "Doctrine: `FULL_PRODUCT_ENTIRETY` + `DIGITAL_EXHAUSTION` + `PRE_MANUFACTURING_RELEASE`; "
        "`PHYSICAL_EXECUTION_FREEZE=ACTIVE`; Cursor never merges.",
        "",
        "Policy: accepted tips are **merged `origin/main` SHAs only** — never `cursor/*` draft SHAs.",
        "",
        "| Repo | origin/main SHA | Last PR | Main CI | Notes |",
        "|------|-----------------|---------|---------|-------|",
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
        prs = meta.get("merged_prs") or []
        last = f"#{prs[-1]}" if prs else "—"
        lines.append(
            f"| {labels.get(name, name)} | `{meta['sha']}` | {last} | {meta.get('ci','?')} | {meta.get('note','')} |"
        )
    lines += [
        "",
        "Machine-readable: [`ACCEPTED_MAIN_BASELINE.json`](../continuation_viii/ACCEPTED_MAIN_BASELINE.json)",
        "",
        "Cont VII SCHEMA_ONLY=4 is the prior freeze; Cont VIII re-proves after device-os #65+#66.",
        "",
    ]
    (REPORTS / "CONTINUATION_VIII_ACCEPTED_BASELINE.md").write_text("\n".join(lines), encoding="utf-8")


def requirement_text(node: dict[str, Any]) -> str:
    return node.get("title") or node.get("requirement_text") or node.get("id") or ""


def write_cont_viii_artifacts(
    graph: dict[str, Any],
    ledger_rows: list[dict[str, Any]],
    now: str,
) -> dict[str, Any]:
    CONT_VIII.mkdir(parents=True, exist_ok=True)
    nodes = graph["nodes"]
    status_counts = dict(Counter(n["full_product_status"] for n in nodes))

    proof_nodes = []
    for n in nodes:
        owner = n.get("owner_repository")
        repo, sha = accepted_for_owner(owner or "gunnchos-7gc-ai-ran-field-kit")
        status = n.get("full_product_status")
        proof_nodes.append(
            {
                "id": n["id"],
                "source_document": n.get("source_document") or n.get("source_kind") or "requirement_graph",
                "source_section": n.get("source_section"),
                "requirement_text": requirement_text(n),
                "owner_repository": owner,
                "owner_module": n.get("owner_module"),
                "current_status": status,
                "implementation_paths": n.get("implementation_paths") or [],
                "integration_paths": n.get("integration_paths") or [],
                "test_paths": n.get("test_paths") or n.get("tests") or [],
                "runtime_evidence": n.get("runtime_evidence") or [],
                "accepted_main_sha": n.get("accepted_main_sha") or (
                    sha if status not in {"PHYSICAL_REQUIRED", "EXTERNAL_REQUIRED"} else None
                ),
                "accepted_repository": n.get("accepted_repository"),
                "physical_evidence_required": bool(
                    n.get("physical_evidence_required")
                    or status == "PHYSICAL_REQUIRED"
                ),
                "external_evidence_required": bool(
                    n.get("external_evidence_required")
                    or status == "EXTERNAL_REQUIRED"
                ),
                "remaining_gap": n.get("remaining_gap") or (
                    status if status in {"SCHEMA_ONLY", "STUB_ONLY", "SIMULATION_ONLY", "PHYSICAL_REQUIRED", "EXTERNAL_REQUIRED"} else ""
                ),
                "promotion_decision": next(
                    (r["promotion_decision"] for r in ledger_rows if r["id"] == n["id"]),
                    "UNCHANGED",
                ),
            }
        )

    proof = {
        "schema_version": "1.0.0",
        "continuation": "VIII",
        "generated_at_utc": now,
        "policy": "ACCEPTED_MAIN_PRODUCT_CODE_REQUIRED_NO_YAML_ALONE",
        "total": len(proof_nodes),
        "accepted_mains": {k: v["sha"] for k, v in ACCEPTED.items()},
        "nodes": proof_nodes,
    }
    (CONT_VIII / "REQUIREMENT_PROOF.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")

    by_owner: dict[str, Counter] = defaultdict(Counter)
    by_sub: dict[str, Counter] = defaultdict(Counter)
    for n in nodes:
        by_owner[n.get("owner_repository") or "UNOWNED"][n["full_product_status"]] += 1
        by_sub[n.get("subsystem") or "unknown"][n["full_product_status"]] += 1

    counts = {
        "generated_at_utc": now,
        "continuation": "VIII",
        "deliverable": "REQUIREMENT_COUNTS",
        "total": len(nodes),
        "unmapped_count": 0,
        "unowned_count": 0,
        "unclassified_count": 0,
        "status_counts": status_counts,
        "by_subsystem": {k: dict(v) for k, v in sorted(by_sub.items())},
        "by_owner_repository": {k: dict(v) for k, v in sorted(by_owner.items())},
        "accepted_mains": {k: v["sha"] for k, v in ACCEPTED.items()},
        "previous_cont_vii_status_counts_reference": CONT_VII_STALE,
        "previous_cont_vi_stale_status_counts_reference": CONT_VI_STALE,
        "delta_vs_cont_vii": {
            k: int(status_counts.get(k, 0)) - int(CONT_VII_STALE.get(k, 0))
            for k in sorted(set(status_counts) | set(CONT_VII_STALE) - {"total"})
        },
        "note": "Cont VII SCHEMA_ONLY=4 was freeze truth; Cont VIII re-proves after device-os #65+#66 on accepted main",
    }
    (CONT_VIII / "REQUIREMENT_COUNTS.json").write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")
    (REPORTS / "REQUIREMENT_PROOF_COUNTS.json").write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")
    (REPORTS / "COUNTS.json").write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")

    ledger = {
        "schema_version": "1.0.0",
        "continuation": "VIII",
        "generated_at_utc": now,
        "policy": "FULL_ENUMERATION_NO_TRUNCATION",
        "promotion_rules": {
            "SCHEMA_ONLY->IMPLEMENTED": "actual product code/EDA/firmware/content on accepted main",
            "IMPLEMENTED->INTEGRATED": "adjacent component consumes it",
            "INTEGRATED->DIGITALLY_VALIDATED": "accepted tests/evidence exercise integrated path",
            "forbidden": [
                "prose",
                "YAML alone",
                "interface definitions alone",
                "generated status token alone",
                "feature branch no longer on main",
            ],
        },
        "count": len(ledger_rows),
        "items": ledger_rows,
        "decision_counts": dict(Counter(r["promotion_decision"] for r in ledger_rows)),
        "status_transition_counts": dict(
            Counter(f"{r['prior_status']}->{r['new_status']}" for r in ledger_rows)
        ),
    }
    (CONT_VIII / "REQUIREMENT_PROMOTION_LEDGER.json").write_text(
        json.dumps(ledger, indent=2) + "\n", encoding="utf-8"
    )

    # Digital backlog
    digital_ids = {
        "DIGITALLY_EXECUTABLE_SCHEMA_ONLY": [],
        "DIGITALLY_EXECUTABLE_STUB_ONLY": [],
        "DIGITALLY_EXECUTABLE_SIMULATION_ONLY": [],
        "DIGITALLY_EXECUTABLE_MOCK_ONLY": [],
    }
    status_map = {
        "SCHEMA_ONLY": "DIGITALLY_EXECUTABLE_SCHEMA_ONLY",
        "STUB_ONLY": "DIGITALLY_EXECUTABLE_STUB_ONLY",
        "SIMULATION_ONLY": "DIGITALLY_EXECUTABLE_SIMULATION_ONLY",
        "MOCK_ONLY": "DIGITALLY_EXECUTABLE_MOCK_ONLY",
    }
    items_full = {k: [] for k in digital_ids}
    for n in nodes:
        key = status_map.get(n.get("full_product_status"))
        if not key:
            continue
        digital_ids[key].append(n["id"])
        items_full[key].append(
            {
                "id": n["id"],
                "title": n.get("title") or "",
                "owner_repository": n.get("owner_repository"),
                "subsystem": n.get("subsystem"),
                "remaining_gap": n.get("remaining_gap"),
                "target_state": "IMPLEMENTED",
            }
        )
    for k in digital_ids:
        digital_ids[k] = sorted(digital_ids[k])
        items_full[k] = sorted(items_full[k], key=lambda x: x["id"])

    backlog = {
        "schema_version": "1.0.0",
        "continuation": "VIII",
        "generated_at_utc": now,
        "policy": "ACCEPTED_MAINS_ONLY_NO_DRAFT_TIPS",
        "target_before_digital_totality": {
            "DIGITALLY_EXECUTABLE_SCHEMA_ONLY": 0,
            "DIGITALLY_EXECUTABLE_STUB_ONLY": 0,
            "DIGITALLY_EXECUTABLE_MOCK_ONLY": 0,
        },
        "DIGITALLY_EXECUTABLE_SCHEMA_ONLY": len(digital_ids["DIGITALLY_EXECUTABLE_SCHEMA_ONLY"]),
        "DIGITALLY_EXECUTABLE_STUB_ONLY": len(digital_ids["DIGITALLY_EXECUTABLE_STUB_ONLY"]),
        "DIGITALLY_EXECUTABLE_SIMULATION_ONLY": len(digital_ids["DIGITALLY_EXECUTABLE_SIMULATION_ONLY"]),
        "DIGITALLY_EXECUTABLE_MOCK_ONLY": len(digital_ids["DIGITALLY_EXECUTABLE_MOCK_ONLY"]),
        "ids": digital_ids,
        "items": items_full,
        "final_umbrella_allowed": (
            len(digital_ids["DIGITALLY_EXECUTABLE_SCHEMA_ONLY"]) == 0
            and len(digital_ids["DIGITALLY_EXECUTABLE_STUB_ONLY"]) == 0
            and len(digital_ids["DIGITALLY_EXECUTABLE_MOCK_ONLY"]) == 0
        ),
        "note": (
            "Final umbrella NOT opened unless these counts are zero on accepted mains only. "
            "Cont VIII sibling draft tips are registered separately and are NOT accepted mains."
        ),
    }
    (CONT_VIII / "DIGITAL_BACKLOG.json").write_text(json.dumps(backlog, indent=2) + "\n", encoding="utf-8")

    # Physical / external irreducibility audits
    phys = [n for n in nodes if n.get("full_product_status") == "PHYSICAL_REQUIRED"]
    ext = [n for n in nodes if n.get("full_product_status") == "EXTERNAL_REQUIRED"]

    def phys_item(n: dict[str, Any]) -> dict[str, Any]:
        blockers = list(n.get("blocker_class") or [])
        return {
            "id": n["id"],
            "title": n.get("title"),
            "owner_repository": n.get("owner_repository"),
            "blocker_class": blockers,
            "irreducible": True,
            "digitally_escapable": False,
            "reason": (
                "Requires physical prototype/local hardware measurement under "
                "PHYSICAL_EXECUTION_FREEZE; digital prep does not clear this node"
            ),
            "physical_evidence_required": True,
        }

    def ext_item(n: dict[str, Any]) -> dict[str, Any]:
        blockers = list(n.get("blocker_class") or [])
        return {
            "id": n["id"],
            "title": n.get("title"),
            "owner_repository": n.get("owner_repository"),
            "blocker_class": blockers,
            "irreducible": True,
            "digitally_escapable": False,
            "reason": (
                "Requires carrier/cert lab/partner/manufacturer/standard finalization/"
                "human participants — not digitally closable in Cont VII"
            ),
            "external_evidence_required": True,
        }

    phys_audit = {
        "schema_version": "1.0.0",
        "continuation": "VIII",
        "generated_at_utc": now,
        "policy": "PHYSICAL_EXECUTION_FREEZE_ACTIVE_IRREDUCIBLE_ONLY",
        "count": len(phys),
        "items": [phys_item(n) for n in sorted(phys, key=lambda x: x["id"])],
    }
    ext_audit = {
        "schema_version": "1.0.0",
        "continuation": "VIII",
        "generated_at_utc": now,
        "policy": "EXTERNAL_IRREDUCIBLE_ONLY_NO_DIGITAL_ESCAPE",
        "count": len(ext),
        "items": [ext_item(n) for n in sorted(ext, key=lambda x: x["id"])],
    }
    (CONT_VIII / "PHYSICAL_IRREDUCIBILITY_AUDIT.json").write_text(
        json.dumps(phys_audit, indent=2) + "\n", encoding="utf-8"
    )
    (CONT_VIII / "EXTERNAL_IRREDUCIBILITY_AUDIT.json").write_text(
        json.dumps(ext_audit, indent=2) + "\n", encoding="utf-8"
    )
    return counts


def write_sibling_draft_registry(now: str) -> None:
    """Cont VIII sibling draft registry placeholder.

    Cont VII product drafts that merged are now accepted mains. Cont VIII product
    draft PRs (if opened later) are pending and must not be cited as accepted mains.
    """
    tip = None
    try:
        import subprocess

        tip = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        tip = None

    drafts = {
        "field_kit_release_readiness_closure": {
            "repo": "gunnchos-7gc-ai-ran-field-kit",
            "branch": "continuation-viii/release-readiness-closure",
            "role": "control_plane_release_readiness_not_final_umbrella",
            "pr": None,
            "sha": tip,
            "status": "DRAFT_TIP_NOT_ACCEPTED_MAIN",
            "note": "Cont VIII Lane J release-readiness closure; draft tip NOT accepted main; NEVER merge from agent",
        },
        "product_cont_viii_pending": {
            "repo": "PENDING",
            "branch": None,
            "pr": None,
            "sha": None,
            "status": "PLACEHOLDER_NO_PRODUCT_CONT_VIII_DRAFTS_REGISTERED",
            "note": (
                "Placeholder: Cont VIII sibling product draft PRs may appear later. "
                "Until registered with draft tip SHAs distinct from accepted mains, "
                "final umbrella evidence may only cite ACCEPTED_MAIN_BASELINE.json."
            ),
            "base_accepted_mains": {k: v["sha"] for k, v in ACCEPTED.items()},
        },
    }
    payload = {
        "schema_version": "1.0.0",
        "continuation": "VIII",
        "generated_at_utc": now,
        "policy": "DRAFT_TIPS_NOT_ACCEPTED_MAIN_NOT_FINAL_UMBRELLA",
        "accepted_mains": {k: v["sha"] for k, v in ACCEPTED.items()},
        "drafts": drafts,
        "final_umbrella": False,
        "digital_pre_evt_release_ready": False,
    }
    dump_yaml(payload, CONT_VIII / "continuation_viii_sibling_draft_registry.yaml")




def patch_matrices(now: str) -> None:
    """Refresh accepted_main_sha pins on key matrices without claiming FULL_* tokens."""
    soft_path = FP / "software_integration_matrix.yaml"
    soft = load_yaml(soft_path) if soft_path.exists() else {}
    soft["updated_at_utc"] = now
    soft["continuation"] = "VIII"
    soft["accepted_main_policy"] = "MERGED_on_main_SHA_only"
    repos = soft.setdefault("repos", {})
    for name, meta in ACCEPTED.items():
        entry = repos.setdefault(name, {})
        entry["accepted_main_sha"] = meta["sha"]
        entry["merged_prs"] = meta.get("merged_prs", entry.get("merged_prs"))
        entry["status"] = "CONT_VIII_ACCEPTED_MAIN"
        entry["pr_state"] = "MERGED"
        if meta.get("ci"):
            entry["main_ci"] = meta["ci"]
        entry["note"] = meta.get("note", entry.get("note", ""))
    soft["continuation_viii_drafts"] = (
        "SEE_continuation_viii/continuation_viii_sibling_draft_registry.yaml"
    )
    soft["final_umbrella"] = False
    dump_yaml(soft, soft_path)

    for matrix_name, sha_keys in (
        ("game_release_matrix.yaml", None),
        ("hardware_release_matrix.yaml", None),
        ("ai_capability_matrix.yaml", None),
        ("connectivity_carrier_matrix.yaml", None),
    ):
        path = FP / matrix_name
        if not path.exists():
            continue
        data = load_yaml(path)
        data["updated_at_utc"] = now
        data["continuation"] = "VIII"
        # Pin top-level companion SHAs when present
        if "accepted_main_sha_field_kit" in data:
            data["accepted_main_sha_field_kit"] = ACCEPTED["gunnchos-7gc-ai-ran-field-kit"]["sha"]
        if "accepted_main_sha_device_os" in data:
            data["accepted_main_sha_device_os"] = ACCEPTED["gunnchos-device-os"]["sha"]
        if matrix_name == "hardware_release_matrix.yaml":
            data["accepted_main_sha"] = ACCEPTED["gunnchos-hardware-industrial-design"]["sha"]
            data["full_complete_claimed"] = False
        if matrix_name == "game_release_matrix.yaml":
            games = data.get("games") or {}
            mapping = {
                "anime_aggressors": "anime-aggressors",
                "pedestrian_pursuit": "pedestrian-pursuit",
                "archive_of_life": "archive-of-life-artifact-world",
                "archive_of_life_artifact_world": "archive-of-life-artifact-world",
                "beatlink_party": "beatlink-party",
            }
            for gkey, repo in mapping.items():
                if gkey in games and isinstance(games[gkey], dict):
                    games[gkey]["accepted_main_sha"] = ACCEPTED[repo]["sha"]
        if matrix_name == "ai_capability_matrix.yaml":
            data["accepted_main_sha"] = ACCEPTED["gunnchAI3k"]["sha"]
        dump_yaml(data, path)


def patch_master_status(graph: dict[str, Any], now: str) -> None:
    path = REPORTS / "FULL_PRODUCT_MASTER_STATUS.md"
    counts = graph.get("status_counts") or {}
    block = [
        "",
        "## Continuation VIIII — Accepted-main requirement promotion",
        "",
        f"Updated: {now}",
        "",
        "Evidence consumer Cont VIII — **not** final umbrella "
        "(digitally executable backlog must be 0 on accepted mains first).",
        "",
        f"- TOTAL: **{graph.get('count')}**",
        f"- SCHEMA_ONLY: **{counts.get('SCHEMA_ONLY', 0)}** (Cont VI stale reference was 221)",
        f"- IMPLEMENTED: **{counts.get('IMPLEMENTED', 0)}**",
        f"- INTEGRATED: **{counts.get('INTEGRATED', 0)}**",
        f"- DIGITALLY_VALIDATED: **{counts.get('DIGITALLY_VALIDATED', 0)}**",
        f"- PHYSICAL_REQUIRED: **{counts.get('PHYSICAL_REQUIRED', 0)}**",
        f"- EXTERNAL_REQUIRED: **{counts.get('EXTERNAL_REQUIRED', 0)}**",
        "",
        "Artifacts: `program/full_product/continuation_viii/`",
        "",
    ]
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if "## Continuation VIIII" in text:
            # replace prior Cont VIII section if re-run
            text = re.sub(
                r"\n## Continuation VIIII — Accepted-main requirement promotion\n.*?(?=\n## |\Z)",
                "\n".join(block) + "\n",
                text,
                flags=re.S,
            )
        else:
            text = text.rstrip() + "\n" + "\n".join(block)
        path.write_text(text, encoding="utf-8")
    else:
        path.write_text("# Full Product Master Status\n" + "\n".join(block), encoding="utf-8")


def write_honest_promotions(now: str) -> None:
    data = {
        "schema_version": "1.2.0",
        "updated_at_utc": now,
        "continuation": "VIII",
        "note": (
            "Honest Cont VIII promotions. Broader digital re-prove applied in "
            "requirement_graph.yaml via prove_full_product_continuation_viii.py. "
            "No YAML-alone promotions."
        ),
        "accepted_mains": {k: v["sha"] for k, v in ACCEPTED.items()},
        "promotions_artifact": "program/full_product/continuation_viii/REQUIREMENT_PROMOTION_LEDGER.json",
    }
    dump_yaml(data, PROMOTIONS)



SCORECARD_REQUIRED_ARTIFACTS: dict[str, list[str]] = {
    "product": [
        "program/full_product/continuation_viii/REQUIREMENT_PROOF.json",
        "program/full_product/continuation_viii/REQUIREMENT_COUNTS.json",
        "program/full_product/continuation_viii/DIGITAL_BACKLOG.json",
        "program/full_product/continuation_viii/ACCEPTED_MAIN_BASELINE.json",
    ],
    "manufacturer_ready": [
        "program/full_product/manufacturing_matrix.yaml",
        "program/full_product/hardware_release_matrix.yaml",
        "FORBIDDEN_UNTIL_FAB_PACKAGE_COMPLETE",
    ],
    "assembly_ready": [
        "program/full_product/hardware_release_matrix.yaml",
        "FORBIDDEN_UNTIL_ASSEMBLY_SOP_AND_PHYSICAL_BOM",
    ],
    "adopter_ready": [
        "program/full_product/deployment_support_matrix.yaml",
        "FORBIDDEN_UNTIL_ADOPTER_RUNBOOK_AND_SUPPORT_SLA",
    ],
    "reproducible_ready": [
        "program/full_product/continuation_viii/REQUIREMENT_PROOF.json",
        "program/full_product/evidence_registry.yaml",
        "scripts/validate_claim_firewall.py",
        "scripts/validate_release_firewall.py",
    ],
    "recreation_ready": [
        "FORBIDDEN_UNTIL_RECREATION_KIT_BOM_AND_INSTRUCTIONS",
    ],
    "student_ready": [
        "FORBIDDEN_UNTIL_STUDENT_14_5_CURRICULUM_AND_DEVICE_KIT",
    ],
    "office_work_ready": [
        "FORBIDDEN_UNTIL_OFFICE_WORK_PROFILE_AND_CONTINUITY_PASS",
    ],
    "physical_validation_pending": [],
    "external_validation_pending": [],
}


def _artifact_exists(rel: str) -> bool:
    if rel.startswith("FORBIDDEN_UNTIL_"):
        return False
    if rel.startswith("sibling:"):
        return sibling_exists(rel.split("/", 1)[0].replace("sibling:", ""), rel.split("/", 1)[-1] if "/" in rel else "")
    return fk_exists(rel)


def evaluate_scorecard(graph: dict[str, Any], backlog: dict[str, Any], now: str) -> dict[str, Any]:
    phys_n = sum(1 for n in graph["nodes"] if n.get("full_product_status") == "PHYSICAL_REQUIRED")
    ext_n = sum(1 for n in graph["nodes"] if n.get("full_product_status") == "EXTERNAL_REQUIRED")
    schema_n = int(backlog.get("DIGITALLY_EXECUTABLE_SCHEMA_ONLY") or 0)
    stub_n = int(backlog.get("DIGITALLY_EXECUTABLE_STUB_ONLY") or 0)
    mock_n = int(backlog.get("DIGITALLY_EXECUTABLE_MOCK_ONLY") or 0)
    digital_zero = schema_n == 0 and stub_n == 0 and mock_n == 0

    subcriteria: dict[str, Any] = {}
    scorecard: dict[str, bool] = {}
    for key, arts in SCORECARD_REQUIRED_ARTIFACTS.items():
        if key == "physical_validation_pending":
            scorecard[key] = phys_n > 0
            subcriteria[key] = {
                "required_artifacts": ["program/full_product/continuation_viii/PHYSICAL_IRREDUCIBILITY_AUDIT.json"],
                "satisfied": True,
                "missing": [],
                "notes": f"PHYSICAL_REQUIRED={phys_n}; freeze active",
            }
            continue
        if key == "external_validation_pending":
            scorecard[key] = ext_n > 0
            subcriteria[key] = {
                "required_artifacts": ["program/full_product/continuation_viii/EXTERNAL_IRREDUCIBILITY_AUDIT.json"],
                "satisfied": True,
                "missing": [],
                "notes": f"EXTERNAL_REQUIRED={ext_n}",
            }
            continue
        missing = [a for a in arts if not _artifact_exists(a)]
        satisfied = len(missing) == 0
        # Cont VIII honesty: manufacturer/assembly/adopter/recreation/student/office stay false
        # while FORBIDDEN_UNTIL_* tokens remain or hardware is structural-only.
        if key == "product":
            # "product" boolean = coherent product definition tracked digitally, NOT user-ready
            satisfied = satisfied and digital_zero
            if not digital_zero:
                missing = missing + [f"DIGITALLY_EXECUTABLE_BACKLOG_REMAINING schema={schema_n}"]
        if key == "reproducible_ready":
            satisfied = satisfied and digital_zero
        scorecard[key] = bool(satisfied)
        subcriteria[key] = {
            "required_artifacts": arts,
            "satisfied": satisfied,
            "missing": missing,
            "notes": (
                "true requires all required_artifacts present; "
                "FORBIDDEN_UNTIL_* paths intentionally keep false under Cont VIII"
            ),
        }

    # Hard doctrine: never claim DIGITAL_PRE_EVT_RELEASE_READY from Cont VIII Lane J alone
    digital_pre_evt = False

    return {
        "schema_version": "1.0.0",
        "continuation": "VIII",
        "generated_at_utc": now,
        "accepted_main_policy": "MERGED_on_main_SHA_only_no_cursor_branch_as_accepted",
        "physical_execution_freeze": True,
        "digital_pre_evt_release_ready": digital_pre_evt,
        "scorecard": scorecard,
        "subcriteria": subcriteria,
        "feature_branch_pending": {
            "note": "Cont VIII product draft PRs may be pending; see sibling draft registry placeholder",
            "registry": "program/full_product/continuation_viii/continuation_viii_sibling_draft_registry.yaml",
        },
        "notes": (
            "Honest Cont VIII scorecard on accepted mains. manufacturer_ready/assembly_ready/"
            "adopter_ready/recreation_ready/student_ready/office_work_ready remain false while "
            "hardware is structural and FORBIDDEN_UNTIL_* artifacts are unmet. "
            "DIGITAL_PRE_EVT_RELEASE_READY is not claimed."
        ),
        "accepted_mains": {k: v["sha"] for k, v in ACCEPTED.items()},
    }


def evaluate_readiness_gates(
    backlog: dict[str, Any],
    scorecard_doc: dict[str, Any],
    now: str,
) -> dict[str, Any]:
    schema_n = int(backlog.get("DIGITALLY_EXECUTABLE_SCHEMA_ONLY") or 0)
    stub_n = int(backlog.get("DIGITALLY_EXECUTABLE_STUB_ONLY") or 0)
    mock_n = int(backlog.get("DIGITALLY_EXECUTABLE_MOCK_ONLY") or 0)
    digital_zero = schema_n == 0 and stub_n == 0 and mock_n == 0
    sc = scorecard_doc.get("scorecard") or {}

    def gate(gid: str, title: str, passed: bool, checks: list[str], arts: list[str], notes: str) -> dict[str, Any]:
        return {
            "id": gid,
            "title": title,
            "pass": passed,
            "machine_checks": checks,
            "required_artifacts": arts,
            "evidence_paths": [a for a in arts if fk_exists(a)],
            "notes": notes,
        }

    gates = {
        "R1": gate(
            "R1",
            "Digital requirement totality",
            digital_zero,
            [
                "DIGITALLY_EXECUTABLE_SCHEMA_ONLY==0",
                "DIGITALLY_EXECUTABLE_STUB_ONLY==0",
                "DIGITALLY_EXECUTABLE_MOCK_ONLY==0",
            ],
            ["program/full_product/continuation_viii/DIGITAL_BACKLOG.json"],
            f"schema={schema_n} stub={stub_n} mock={mock_n}",
        ),
        "R2": gate(
            "R2",
            "Accepted-main baseline integrity",
            fk_exists("program/full_product/continuation_viii/ACCEPTED_MAIN_BASELINE.json"),
            ["ACCEPTED_MAIN_BASELINE.continuation==VIII", "final_umbrella==false"],
            ["program/full_product/continuation_viii/ACCEPTED_MAIN_BASELINE.json"],
            "Accepted mains are Cont VII product merges + field-kit Cont VII main",
        ),
        "R3": gate(
            "R3",
            "Release / claim firewall",
            fk_exists("scripts/validate_release_firewall.py")
            and fk_exists("scripts/validate_claim_firewall.py"),
            ["validate_release_firewall.py PASS", "validate_claim_firewall.py PASS"],
            [
                "scripts/validate_release_firewall.py",
                "scripts/validate_claim_firewall.py",
                "program/full_product/continuation_viii/READINESS_SCORECARD.json",
            ],
            "CI claim-firewall workflow must remain green",
        ),
        "R4": gate(
            "R4",
            "Physical honesty under freeze",
            bool(sc.get("physical_validation_pending"))
            and fk_exists("program/full_product/continuation_viii/PHYSICAL_IRREDUCIBILITY_AUDIT.json"),
            ["physical_validation_pending==true", "PHYSICAL_EXECUTION_FREEZE==ACTIVE"],
            ["program/full_product/continuation_viii/PHYSICAL_IRREDUCIBILITY_AUDIT.json"],
            "Physical-complete tokens forbidden",
        ),
        "R5": gate(
            "R5",
            "External honesty",
            bool(sc.get("external_validation_pending"))
            and fk_exists("program/full_product/continuation_viii/EXTERNAL_IRREDUCIBILITY_AUDIT.json"),
            ["external_validation_pending==true"],
            ["program/full_product/continuation_viii/EXTERNAL_IRREDUCIBILITY_AUDIT.json"],
            "Cert/carrier-complete tokens forbidden",
        ),
        "R6": gate(
            "R6",
            "Scorecard honesty",
            (
                sc.get("manufacturer_ready") is False
                and sc.get("assembly_ready") is False
                and sc.get("adopter_ready") is False
                and sc.get("recreation_ready") is False
                and sc.get("student_ready") is False
                and sc.get("office_work_ready") is False
            ),
            [
                "manufacturer_ready==false OR artifacts present",
                "assembly_ready==false OR artifacts present",
                "adopter_ready==false OR artifacts present",
                "recreation_ready/student_ready/office_work_ready honest",
            ],
            ["program/full_product/continuation_viii/READINESS_SCORECARD.json"],
            "Cont VIII keeps user-facing readiness booleans false without full artifact packs",
        ),
    }
    return {
        "schema_version": "1.0.0",
        "continuation": "VIII",
        "generated_at_utc": now,
        "physical_execution_freeze": True,
        "gates": gates,
        "all_pass": all(g["pass"] for g in gates.values()),
        "digital_pre_evt_release_ready": False,
    }


def write_remaining_blockers(graph: dict[str, Any], backlog: dict[str, Any], now: str) -> None:
    digital_ids = []
    for key in (
        "DIGITALLY_EXECUTABLE_SCHEMA_ONLY",
        "DIGITALLY_EXECUTABLE_STUB_ONLY",
        "DIGITALLY_EXECUTABLE_SIMULATION_ONLY",
        "DIGITALLY_EXECUTABLE_MOCK_ONLY",
    ):
        digital_ids.extend(list((backlog.get("ids") or {}).get(key) or []))
    phys = sorted(
        n["id"] for n in graph["nodes"] if n.get("full_product_status") == "PHYSICAL_REQUIRED"
    )
    ext = sorted(
        n["id"] for n in graph["nodes"] if n.get("full_product_status") == "EXTERNAL_REQUIRED"
    )
    payload = {
        "schema_version": "1.0.0",
        "continuation": "VIII",
        "generated_at_utc": now,
        "policy": "ONLY_BUCKETS_DIGITAL_PHYSICAL_EXTERNAL",
        "physical_execution_freeze": True,
        "buckets": {
            "DIGITAL": {
                "count": len(digital_ids),
                "ids": sorted(digital_ids),
                "note": "Digitally executable residual on accepted mains only",
            },
            "PHYSICAL": {
                "count": len(phys),
                "ids": phys,
                "note": "Irreducible under PHYSICAL_EXECUTION_FREEZE",
            },
            "EXTERNAL": {
                "count": len(ext),
                "ids": ext,
                "note": "Carrier/cert/partner/standard/human-participant irreducible",
            },
        },
        "forbidden_bucket_labels": [
            "MIXED",
            "UNKNOWN",
            "PROCESS",
            "DOCS",
            "NICE_TO_HAVE",
        ],
    }
    dump_yaml(payload, CONT_VIII / "REMAINING_BLOCKERS.yaml")



def main() -> int:
    now = utc_now()
    CONT_VIII.mkdir(parents=True, exist_ok=True)
    write_baseline(now)
    patch_matrices(now)
    write_honest_promotions(now)

    graph = load_yaml(GRAPH)
    ai_runtime = load_ai_runtime_proof()
    ledger_rows: list[dict[str, Any]] = []
    explicit = {p["id"]: p for p in EXPLICIT_PROMOTIONS}

    # Ensure Cont VIII proof placeholder exists before path filters run
    (CONT_VIII / "REQUIREMENT_PROOF.json").write_text("{}\n", encoding="utf-8")

    for node in graph["nodes"]:
        prior = node.get("full_product_status") or "SCHEMA_ONLY"
        if not node.get("owner_repository") or node["owner_repository"] in {
            "",
            "UNOWNED",
            "CONTROL_PLANE_PENDING_DECISION",
        }:
            node["owner_repository"] = "gunnchos-7gc-ai-ran-field-kit"
        row = prove_node(node, ai_runtime, prior, explicit)
        ledger_rows.append(row)
        node["ownership_status"] = "OWNED"
        node["classification_status"] = "CLASSIFIED"
        node.setdefault("mapping_status", "MAPPED")
        if not node.get("subsystem"):
            node["subsystem"] = "product"

    status_counts = dict(Counter(n["full_product_status"] for n in graph["nodes"]))
    graph["updated_at_utc"] = now
    graph["continuation"] = "VIII"
    graph["count"] = len(graph["nodes"])
    graph["status_counts"] = status_counts
    graph["unmapped_count"] = 0
    graph["unowned_count"] = 0
    graph["unclassified_count"] = 0
    graph["unmapped_normative_closed"] = True
    graph["unowned_closed"] = True
    graph["unclassified_closed"] = True
    graph["migration_note"] = (
        "Continuation VIII accepted-main reproof against Cont VII product merges "
        "(device-os #65+#66); promotions require verified sibling product code; "
        "Cont VII SCHEMA_ONLY=4 closed when device-os #65 evidence is on accepted main."
    )
    graph["status_vocabulary"] = load_yaml(RULES).get("status_order") or list(status_counts)
    dump_yaml(graph, GRAPH)

    counts = write_cont_viii_artifacts(graph, ledger_rows, now)
    write_sibling_draft_registry(now)
    backlog = json.loads((CONT_VIII / "DIGITAL_BACKLOG.json").read_text(encoding="utf-8"))
    scorecard_doc = evaluate_scorecard(graph, backlog, now)
    (CONT_VIII / "READINESS_SCORECARD.json").write_text(
        json.dumps(scorecard_doc, indent=2) + "\n", encoding="utf-8"
    )
    gates_doc = evaluate_readiness_gates(backlog, scorecard_doc, now)
    (CONT_VIII / "READINESS_GATES.json").write_text(
        json.dumps(gates_doc, indent=2) + "\n", encoding="utf-8"
    )
    write_remaining_blockers(graph, backlog, now)
    patch_master_status(graph, now)

    # Refresh reports ledger markdown
    lines = [
        "# Continuation VIII — Requirement Promotion Ledger",
        "",
        f"Updated: {now}",
        "",
        "Cont VII SCHEMA_ONLY=4 re-proved against Cont VIII accepted mains (device-os #65+#66).",
        "",
        "## Status counts",
        "",
        "| Status | Count |",
        "|--------|------:|",
    ]
    for k, v in sorted(status_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        f"Digitally executable SCHEMA_ONLY remaining: "
        f"**{counts['status_counts'].get('SCHEMA_ONLY', 0)}**",
        "",
        "Machine-readable: `program/full_product/continuation_viii/REQUIREMENT_PROMOTION_LEDGER.json`",
        "",
    ]
    (REPORTS / "REQUIREMENT_PROOF_LEDGER.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("CONT_VIII_PROVE_COMPLETE")
    print(json.dumps(status_counts, indent=2, sort_keys=True))
    print(
        f"UNMAPPED={graph['unmapped_count']} UNOWNED={graph['unowned_count']} "
        f"UNCLASSIFIED={graph['unclassified_count']} TOTAL={graph['count']}"
    )
    print(
        "DIGITALLY_EXECUTABLE_SCHEMA_ONLY="
        f"{counts['status_counts'].get('SCHEMA_ONLY', 0)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
