"""Repository inventory, ownership, and branch migration catalogs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CANONICAL_SEED = {
    "control_plane": ["gunnchos-7gc-ai-ran-field-kit", "gunnchos-research-portal"],
    "device_os_ai_input": [
        "gunnchos-device-os",
        "gunnchos-hardware-industrial-design",
        "gunnchAI3k",
        "EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon",
        "edge-io-measurement-node",
    ],
    "games": [
        "beatlink-party",
        "archive-of-life-artifact-world",
        "pedestrian-pursuit",
        "anime-aggressors",
    ],
    "connectivity_research": [
        "7gc-digital-twin",
        "spectrumx-ai-ran-gary",
        "ntn-resilience-sim",
        "readygary-6g-beam-selection",
        "waike-research-ops",
        "gunnchos-emergent-service-intent-protocols",
        "gunnchos-gpu-nr-baseband-platform",
    ],
}

# Local folder name -> classification / notes
CLASSIFICATIONS = {
    "gunnchos-7gc-ai-ran-field-kit": ("CANONICAL", "control_plane"),
    "gunnchos-research-portal": ("CANONICAL", "public_evidence"),
    "gunnchos-device-os": ("CANONICAL", "os"),
    "gunnchos-hardware-industrial-design": ("CANONICAL", "hardware"),
    "gunnchAI3k": ("CANONICAL", "ai"),
    "EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon": ("CANONICAL", "rings_gesture_research"),
    "edge-io-measurement-node": ("CANONICAL", "measurement"),
    "beatlink-party": ("CANONICAL", "game"),
    "archive-of-life-artifact-world": ("CANONICAL", "game"),
    "pedestrian-pursuit": ("CANONICAL", "game"),
    "anime-aggressors": ("CANONICAL", "game"),
    "7gc-digital-twin": ("CANONICAL", "7gc"),
    "spectrumx-ai-ran-gary": ("CANONICAL", "ai_ran"),
    "ntn-resilience-sim": ("CANONICAL", "ntn"),
    "readygary-6g-beam-selection": ("CANONICAL", "beam_selection"),
    "waike-research-ops": ("CANONICAL", "research_ops"),
    "gunnchos-emergent-service-intent-protocols": ("CANONICAL", "oulu_gate4a_science"),
    "gunnchos-gpu-nr-baseband-platform": ("CANONICAL", "nvidia_gate4b"),
    "gunnchos-6g-security-trust-privacy-lab": ("LEGACY_NAME", "oulu_named_supporting"),
    "gunnchos-information-theory-channel-coding-lab": ("LEGACY_NAME", "oulu_named_supporting"),
    "gunnchos-mimo-smart-antenna-lab": ("LEGACY_NAME", "oulu_named_supporting"),
    "gunnchos-open-ran-testbed-lab": ("LEGACY_NAME", "oulu_named_supporting"),
    "gunnchos-rf-front-end-lab": ("LEGACY_NAME", "oulu_named_supporting"),
    "gunnchos-stochastic-dsp-lab": ("LEGACY_NAME", "oulu_named_supporting"),
    "gunnchos-wireless-engineering-readiness-dashboard": ("LEGACY_NAME", "oulu_named_supporting"),
    "gunnchos-wireless-measurement-system-testing-lab": ("LEGACY_NAME", "oulu_named_supporting"),
    "gunnchos-7gc-verticals-6g-use-case-lab": ("SUPPORTING", "verticals"),
    "ECE-6023-Final-Project": ("OUT_OF_SCOPE", "course_project"),
    "curriculum": ("OUT_OF_SCOPE", "curriculum"),
    "docs": ("OUT_OF_SCOPE", "docs_folder"),
    "phd_application_readiness_package": ("SUPPORTING", "phd_readiness_package"),
    "quality": ("OUT_OF_SCOPE", "quality_folder"),
}


def build_branch_policy() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "canonical_default_branch": "main",
        "legacy_default_branch": "master",
        "new_master_references_prohibited": True,
        "master_deletion_requires_edmund_approval": True,
        "force_push_prohibited": True,
        "history_rewrite_prohibited": True,
        "master_read_only_after_migration": True,
        "allowlist_globs_for_master_mentions": [
            "program/reports/MAIN_BRANCH_MIGRATION_AUDIT.md",
            "program/reports/MASTER_REFERENCE_REMEDIATION_REPORT.md",
            "program/repositories/branch_migration_*.yaml",
            "GATES_1_TO_4_CLEAN_DEFAULT_BRANCH_AUDIT.md",
            "LOCAL_NO_REPO_BRANCH_SYNC_REPORT.md",
            "**/*migration*",
            "**/*MIGRATION*",
            "**/*remediation*",
            "**/*REMEDIATION*",
        ],
        "allowlist_workflow_dual_triggers": True,
        "notes": [
            "Dual-trigger workflows that retain master for historical PR compatibility may be allowlisted explicitly.",
            "Historical prose and archival reports may mention master.",
        ],
    }


def load_branch_audit(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_repository_inventory(
    repos_root: Path,
    audit_path: Path,
    field_kit_post_migration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Discover local repos and merge branch-migration audit facts."""
    audit = load_branch_audit(audit_path) or {"results": []}
    audit_by_name = {r["repository"]: r for r in audit.get("results", [])}

    discovered: list[dict[str, Any]] = []
    if repos_root.exists():
        for child in sorted(repos_root.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            if not (child / ".git").exists():
                # non-git folders noted when classified
                if child.name in CLASSIFICATIONS:
                    cls, role = CLASSIFICATIONS[child.name]
                    discovered.append(
                        {
                            "name": child.name,
                            "local_path": str(child),
                            "remote": None,
                            "classification": cls,
                            "role": role,
                            "has_git": False,
                            "default_branch": None,
                            "notes": "Directory present without .git",
                        }
                    )
                continue
            cls, role = CLASSIFICATIONS.get(child.name, ("SUPPORTING", "discovered"))
            entry: dict[str, Any] = {
                "name": child.name,
                "local_path": str(child),
                "classification": cls,
                "role": role,
                "has_git": True,
            }
            a = audit_by_name.get(child.name)
            if a:
                entry.update(
                    {
                        "remote": a.get("remote"),
                        "remote_owner_name": a.get("remote_owner_name"),
                        "visibility": a.get("visibility"),
                        "github_default_branch": a.get("github_default_branch"),
                        "local_branch": a.get("local_branch"),
                        "main_sha": a.get("main_sha"),
                        "master_sha": a.get("master_sha"),
                        "migration_case": a.get("migration_case"),
                        "dirty": a.get("dirty"),
                        "open_prs": a.get("open_prs") or [],
                    }
                )
            # Post-audit field-kit migration override (facts from later pass)
            if child.name == "gunnchos-7gc-ai-ran-field-kit" and field_kit_post_migration:
                entry.update(field_kit_post_migration)
                entry["notes"] = (
                    "Post-audit migration: main created at master SHA; "
                    "GitHub default=main; PR#12 and PR#1 retargeted to main. "
                    "master preserved read-only."
                )
            discovered.append(entry)

    # EdgeGesture standalone
    edge_standalone = Path(
        "/Users/gunnchos/Downloads/EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon"
    )
    a = audit_by_name.get("standalone:EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon")
    discovered.append(
        {
            "name": "EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon",
            "local_path": str(edge_standalone) if edge_standalone.exists() else None,
            "classification": "CANONICAL",
            "role": "rings_gesture_research",
            "location": "STANDALONE_DOWNLOADS",
            "has_git": edge_standalone.exists() and (edge_standalone / ".git").exists(),
            "remote": (a or {}).get("remote"),
            "remote_owner_name": (a or {}).get("remote_owner_name"),
            "visibility": (a or {}).get("visibility"),
            "github_default_branch": (a or {}).get("github_default_branch", "main"),
            "local_branch": (a or {}).get("local_branch"),
            "main_sha": (a or {}).get("main_sha"),
            "master_sha": (a or {}).get("master_sha"),
            "migration_case": (a or {}).get("migration_case", "A_MAIN_ONLY"),
            "dirty": (a or {}).get("dirty"),
            "open_prs": (a or {}).get("open_prs") or [],
            "notes": "Exists only as standalone Downloads copy; not under spine/repos.",
        }
    )

    # Missing canonical placeholders
    present_names = {d["name"] for d in discovered}
    for group, names in CANONICAL_SEED.items():
        for name in names:
            if name not in present_names and name != "EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon":
                discovered.append(
                    {
                        "name": name,
                        "local_path": None,
                        "classification": "MISSING_LOCALLY",
                        "role": group,
                        "has_git": False,
                        "notes": "Canonical seed entry not found under repos root",
                    }
                )

    return {
        "schema_version": "1.0.0",
        "repos_root": str(repos_root),
        "audit_source": str(audit_path) if audit_path.exists() else None,
        "repositories": discovered,
    }


def build_repository_ownership(requirements: list[dict[str, Any]]) -> dict[str, Any]:
    by_owner: dict[str, list[str]] = {}
    for req in requirements:
        owner = req["owner_repository"]
        by_owner.setdefault(owner, []).append(req["id"])
    ring_workstreams = {
        "industrial_electrical_design": "gunnchos-hardware-industrial-design",
        "ring_firmware": "CONTROL_PLANE_PENDING_DECISION",
        "sensing_and_inference": "EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon",
        "secure_pairing_and_authentication": "gunnchos-device-os",
        "gunnchos_input_service": "gunnchos-device-os",
        "calibration": "EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon",
        "haptics": "CONTROL_PLANE_PENDING_DECISION",
        "application_sdk": "gunnchos-device-os",
        "game_integration": "gunnchos-7gc-ai-ran-field-kit",
        "measurement_and_validation": "edge-io-measurement-node",
        "privacy": "gunnchos-device-os",
        "safety": "gunnchos-hardware-industrial-design",
        "manufacturing": "CONTROL_PLANE_PENDING_DECISION",
    }
    return {
        "schema_version": "1.0.0",
        "owner_to_requirements": {k: sorted(v) for k, v in sorted(by_owner.items())},
        "ring_workstream_ownership": ring_workstreams,
        "ring_ownership_disclaimer": (
            "Cross-repo responsibility is documented for planning only. "
            "Assignment does not claim that ring firmware, manufactured rings, "
            "or validated production components exist."
        ),
        "pending_decision_owners": [
            k for k in by_owner if k == "CONTROL_PLANE_PENDING_DECISION"
        ],
    }


def build_canonical_policy() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "canonical_seed": CANONICAL_SEED,
        "classifications": [
            "CANONICAL",
            "SUPPORTING",
            "LEGACY_NAME",
            "DUPLICATE",
            "ARCHIVE_CANDIDATE",
            "OUT_OF_SCOPE",
            "MISSING_LOCALLY",
            "INACCESSIBLE",
        ],
        "rules": [
            "Repositories beginning with oulu- are not automatically canonical product repos.",
            "Do not rename, delete, archive, or recreate repositories during Gate 0.",
            "Do not plaster Oulu branding throughout the general gunnchOS ecosystem.",
            "EdgeGesture is canonical for ring gesture research even when only present as standalone.",
        ],
    }


def build_branch_migration_inventory(audit_path: Path) -> dict[str, Any]:
    audit = load_branch_audit(audit_path) or {"results": [], "generated_at": None}
    rows = []
    for r in audit.get("results", []):
        rows.append(
            {
                "repository": r.get("repository"),
                "remote_owner_name": r.get("remote_owner_name"),
                "github_default_branch": r.get("github_default_branch"),
                "has_origin_main": r.get("has_origin_main"),
                "has_origin_master": r.get("has_origin_master"),
                "main_sha": r.get("main_sha"),
                "master_sha": r.get("master_sha"),
                "migration_case": r.get("migration_case"),
                "open_pr_bases": sorted(
                    {p.get("baseRefName") for p in (r.get("open_prs") or []) if p.get("baseRefName")}
                ),
                "dirty": r.get("dirty"),
            }
        )
    return {
        "schema_version": "1.0.0",
        "generated_from": str(audit_path),
        "audit_generated_at": audit.get("generated_at"),
        "repositories": rows,
    }


def build_branch_migration_status(audit_path: Path) -> dict[str, Any]:
    inv = build_branch_migration_inventory(audit_path)
    # Post-migration field-kit correction per user context
    field_kit_status = {
        "repository": "gunnchos-7gc-ai-ran-field-kit",
        "audit_case": "B_MASTER_ONLY",
        "post_migration_status": "MIGRATED_IDENTICAL_HISTORY",
        "github_default_branch": "main",
        "main_sha": "de818fbe...",
        "master_sha": "de818fbe...",
        "prs_retargeted": ["#12", "#1"],
        "master_preserved": True,
        "notes": (
            "Audit snapshot predated migration. Subsequent pass created main at same SHA as "
            "master, set GitHub default=main, retargeted PR#12 and PR#1 to main."
        ),
    }
    already_main = [
        r["repository"]
        for r in inv["repositories"]
        if r.get("migration_case") == "A_MAIN_ONLY"
        and not str(r.get("repository", "")).startswith("standalone:")
    ]
    return {
        "schema_version": "1.0.0",
        "overall": "MAIN_BRANCH_NORMALIZATION_PASS",
        "field_kit": field_kit_status,
        "already_main_count": len(already_main),
        "edgegesture_standalone": "ALREADY_MAIN",
        "scine_workspace_note": "scine workspace had empty stub field-kit; spine/repos is active workspace",
        "force_push_used": False,
        "history_rewritten": False,
        "master_deleted": False,
    }
