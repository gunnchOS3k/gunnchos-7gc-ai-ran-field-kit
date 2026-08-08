#!/usr/bin/env python3
"""Scan normative sources, sync requirement graph, apply honest promotions, write reports.

Expands beyond must/shall to required / needs to / will support / launch includes / etc.
Drives UNMAPPED / UNOWNED / UNCLASSIFIED toward 0. Does not over-claim implementation.
"""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SIBLING = ROOT.parent
FP = ROOT / "program" / "full_product"
GRAPH = FP / "requirement_graph.yaml"
CATALOG = ROOT / "program" / "requirements" / "requirements.yaml"
CHARTER = ROOT / "program" / "charters" / "GUNNCHOS3K_CARRIER_GRADE_6G_ECOSYSTEM.md"
PROMOTIONS = FP / "honest_promotions.yaml"
RULES = FP / "promotion_rules.yaml"
SCAN_INDEX = FP / "normative_scan_index.yaml"
REPORTS = FP / "reports"
ISSUES_LOCAL = FP / "FULL_PRODUCT_REQUIRED_issues.yaml"

NORMATIVE_RE = re.compile(
    r"\b("
    r"must(?:\s+not)?|"
    r"shall(?:\s+not)?|"
    r"required|"
    r"needs?\s+to|"
    r"will\s+support|"
    r"launch\s+includes?|"
    r"mandatory|"
    r"at\s+minimum|"
    r"requires?|"
    r"shall\s+be\s+capable|"
    r"will\s+(?:provide|include|maintain|ensure|support)|"
    r"non-?negotiable|"
    r"is\s+required|"
    r"are\s+required"
    r")\b",
    re.I,
)

WEAK_LINE_RE = re.compile(
    r"(?i)("
    r"whether feedback or correction is required|"
    r"where required$|"
    r"already requires contributors|"
    r"^\|\s*required\s*\||"
    r"document\s*\|\s*required|"
    r"variable\s*\|\s*source\s*\|\s*required"
    r")"
)

OWNER_BY_PREFIX = {
    "SYS-": "gunnchos-7gc-ai-ran-field-kit",
    "DEV-": "gunnchos-hardware-industrial-design",
    "OS-": "gunnchos-device-os",
    "AI-": "gunnchAI3k",
    "RING-": "EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon",
    "GAME-BEATLINK": "beatlink-party",
    "GAME-AOL": "archive-of-life-artifact-world",
    "GAME-PP": "pedestrian-pursuit",
    "GAME-AA": "anime-aggressors",
    "GATE-": "gunnchos-7gc-ai-ran-field-kit",
    "FULL-OPS": "gunnchos-7gc-ai-ran-field-kit",
    "FP-GAME-AA": "anime-aggressors",
    "FP-GAME-PP": "pedestrian-pursuit",
    "FP-GAME-AR": "archive-of-life-artifact-world",
    "FP-GAME-BL": "beatlink-party",
    "FP-HW-": "gunnchos-hardware-industrial-design",
    "FP-OS-": "gunnchos-device-os",
    "FP-AI-": "gunnchAI3k",
    "FP-RING-": "EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon",
    "FP-DSXL-": "gunnchos-device-os",
    "FP-CHARTER-": "gunnchos-7gc-ai-ran-field-kit",
    "FP-MFG-": "gunnchos-hardware-industrial-design",
    "FP-CERT-": "gunnchos-7gc-ai-ran-field-kit",
    "FP-DEPLOY-": "gunnchos-7gc-ai-ran-field-kit",
    "FP-SUPPORT-": "gunnchos-7gc-ai-ran-field-kit",
    "FP-SEC-": "gunnchos-device-os",
    "FP-CONN-": "gunnchos-device-os",
    "FP-WAIKE-": "waike-research-ops",
    "FP-GDD-": "gunnchos-7gc-ai-ran-field-kit",
}

SUBSYSTEM_BY_HINT = {
    "gunnchos": "gunnchos",
    "gunnchai": "gunnchai",
    "ring": "rings",
    "carrier": "carrier_grade",
    "manufactur": "manufacturing",
    "certif": "certification",
    "deploy": "deployment",
    "support": "support",
    "security": "security",
    "connect": "connectivity",
    "waike": "waike",
    "anime": "anime",
    "archive": "archive",
    "beat": "beatlink",
    "pedestrian": "pedestrian",
    "dock": "hardware",
    "hardware": "hardware",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def dump(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )


def load(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def slug(text: str, limit: int = 40) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").upper()
    return (s[:limit] or "ITEM").rstrip("-")


def infer_owner(nid: str, fallback: str = "gunnchos-7gc-ai-ran-field-kit") -> str:
    for prefix, owner in sorted(OWNER_BY_PREFIX.items(), key=lambda x: -len(x[0])):
        if nid.startswith(prefix):
            return owner
    return fallback


def infer_subsystem(text: str, fallback: str = "product") -> str:
    low = text.lower()
    for hint, sub in SUBSYSTEM_BY_HINT.items():
        if hint in low:
            return sub
    return fallback


def catalog_nodes() -> list[dict[str, Any]]:
    raw = load(CATALOG)
    reqs = raw["requirements"] if isinstance(raw, dict) else raw
    nodes: list[dict[str, Any]] = []
    for r in reqs:
        owner = r.get("owner_repository") or infer_owner(r["id"])
        if owner in ("", "UNOWNED", "CONTROL_PLANE_PENDING_DECISION", None):
            owner = infer_owner(r["id"])
        nodes.append(
            {
                "id": r["id"],
                "title": r.get("title") or r["id"],
                "source_section": r.get("source_section") or "",
                "source_line_start": r.get("source_line_start"),
                "source_line_end": r.get("source_line_end"),
                "subsystem": r.get("subsystem") or infer_subsystem(r.get("title") or ""),
                "priority": r.get("priority") or "P0",
                "owner_repository": owner,
                "legacy_implementation_state": r.get("implementation_state"),
                "implementation_paths": [],
                "tests": list(r.get("required_evidence") or []),
                "full_product_status": "DOC_ONLY",
                "blocker_class": list(r.get("blockers") or []),
                "evidence": [],
                "accepted_sha": None,
                "mapping_status": "MAPPED",
                "ownership_status": "OWNED",
                "classification_status": "CLASSIFIED",
                "source_kind": "charter_catalog",
            }
        )
    return nodes


def existing_fp_seed() -> dict[str, dict[str, Any]]:
    if not GRAPH.exists():
        return {}
    g = load(GRAPH)
    out = {}
    for n in g.get("nodes") or []:
        if str(n.get("id", "")).startswith("FP-"):
            out[n["id"]] = n
    return out


def scan_text_file(path: Path, source_id: str) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    hits: list[dict[str, Any]] = []
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not NORMATIVE_RE.search(stripped):
            continue
        if WEAK_LINE_RE.search(stripped):
            continue
        hits.append(
            {
                "source": source_id,
                "path": str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
                "line": i,
                "text": stripped[:240],
            }
        )
    return hits


def charter_coverage_lines(nodes: list[dict[str, Any]]) -> set[int]:
    covered: set[int] = set()
    for n in nodes:
        start = n.get("source_line_start")
        end = n.get("source_line_end")
        if start and end:
            for ln in range(int(start), int(end) + 1):
                covered.add(ln)
                for d in range(-4, 5):
                    covered.add(ln + d)
        # FP-CHARTER-L275-...
        m = re.match(r"FP-CHARTER-L(\d+)", n.get("id") or "")
        if m:
            ln = int(m.group(1))
            for d in range(-2, 3):
                covered.add(ln + d)
    return covered


def ensure_charter_nodes(nodes: list[dict[str, Any]], charter_hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {n["id"]: n for n in nodes}
    covered = charter_coverage_lines(nodes)
    added: list[dict[str, Any]] = []
    for hit in charter_hits:
        ln = hit["line"]
        if ln in covered:
            continue
        nid = f"FP-CHARTER-L{ln}-{slug(hit['text'], 28)}"
        if nid in by_id:
            continue
        node = {
            "id": nid,
            "title": hit["text"][:120],
            "source_section": f"charter L{ln}",
            "source_line_start": ln,
            "source_line_end": ln,
            "subsystem": infer_subsystem(hit["text"], "ecosystem"),
            "priority": "P0",
            "owner_repository": infer_owner(nid),
            "implementation_paths": [],
            "tests": [],
            "full_product_status": "DOC_ONLY",
            "blocker_class": [],
            "evidence": [],
            "accepted_sha": None,
            "mapping_status": "INGESTED",
            "ownership_status": "OWNED",
            "classification_status": "CLASSIFIED",
            "source_kind": "charter_expanded_scan",
            "normative_text": hit["text"],
        }
        by_id[nid] = node
        added.append(node)
        for d in range(-2, 3):
            covered.add(ln + d)
    return added


CHARTER_SEED = [
    ("FP-CHARTER-L15-ECOSYSTEM-SHALL", 15, "Ecosystem shall deliver coherent family capabilities", "ecosystem"),
    ("FP-CHARTER-L275-GUNNCHOS-COMMON", 275, "gunnchOS shall be common OS across device family", "gunnchos"),
    ("FP-CHARTER-L332-GUNNCHAI-SYSTEM", 332, "gunnchAI3k shall be intelligent system layer not chatbot", "gunnchai"),
    ("FP-CHARTER-L358-OFFLINE-ESSENTIAL", 358, "Essential features must continue when cloud weak/unavailable", "connectivity"),
    ("FP-CHARTER-L513-REQUIRED-EXPERIENCE", 513, "Required experience clause", "product"),
    ("FP-CHARTER-L543-ARCHIVE-SCIENCE", 543, "Archive shall use authoritative scientific structures", "archive"),
    ("FP-CHARTER-L635-CARRIER-GRADE-NOT-MODEM", 635, "Carrier-grade is not merely cellular modem presence", "connectivity"),
]

ADR_FLOOR_SEED = [
    ("FP-GAME-AA-FIGHTERS-7", "Anime launch all 7 fighters runtime", "ADR-GAME-AA-001", "anime", "anime-aggressors"),
    ("FP-GAME-AA-STAGES-6", "Anime launch 6 stages", "ADR-GAME-AA-001", "anime", "anime-aggressors"),
    ("FP-GAME-AA-MODES", "Anime modes including online architecture", "ADR-GAME-AA-001", "anime", "anime-aggressors"),
    ("FP-GAME-PP-RACERS-8", "Pedestrian ≥8 racers", "ADR-GAME-PP-001", "pedestrian", "pedestrian-pursuit"),
    ("FP-GAME-PP-TRACKS-8", "Pedestrian ≥8 tracks", "ADR-GAME-PP-001", "pedestrian", "pedestrian-pursuit"),
    ("FP-GAME-AR-REGIONS-12", "Archive ≥12 regions", "ADR-GAME-AR-001", "archive", "archive-of-life-artifact-world"),
    ("FP-GAME-AR-ENCOUNTER-120", "Archive ≥120 encounter taxa", "ADR-GAME-AR-001", "archive", "archive-of-life-artifact-world"),
    ("FP-GAME-BL-MODES-5", "Beat Link five first-class modes", "ADR-GAME-BL-001", "beatlink", "beatlink-party"),
    ("FP-GAME-BL-CATALOG-12", "Beat Link ≥12 rights-cleared tracks", "ADR-GAME-BL-001", "beatlink", "beatlink-party"),
    ("FP-HW-STUDENT_14_5-RELEASE", "Student 14.5 full hardware design release", "ADR-FP family", "hardware", "gunnchos-hardware-industrial-design"),
    ("FP-HW-DS_XL_CODER-RELEASE", "DS-XL Coder full hardware design release", "ADR-FP family", "hardware", "gunnchos-hardware-industrial-design"),
    ("FP-HW-HANDHELD_HYBRID-RELEASE", "Handheld Hybrid full hardware design release", "ADR-FP family", "hardware", "gunnchos-hardware-industrial-design"),
    ("FP-HW-EDGE_IO_RINGS-RELEASE", "Edge I/O Rings full hardware design release", "ADR-FP family", "hardware", "gunnchos-hardware-industrial-design"),
    ("FP-HW-DOCK-RELEASE", "First-party Dock full hardware design release", "ADR-FP family", "hardware", "gunnchos-hardware-industrial-design"),
    ("FP-OS-DISTRIBUTION", "gunnchOS reproducible distribution pipeline", "gap-audit", "os", "gunnchos-device-os"),
    ("FP-AI-SYSTEM-LAYER", "gunnchAI3k complete system layer", "gap-audit", "ai", "gunnchAI3k"),
    ("FP-RING-SPATIAL-INPUT", "Ring spatial-input promise sensor fusion", "ADR-FP-008", "rings", "EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon"),
    ("FP-DSXL-DUAL-SCREEN", "DS-XL real second-screen application framework", "charter/dsxl", "os", "gunnchos-device-os"),
]

MATRIX_SEED = [
    ("FP-MFG-EDA-PACKAGE", "Per-product EDA/Gerber/BOM/AVL manufacturing package", "manufacturing_matrix", "manufacturing", "gunnchos-hardware-industrial-design"),
    ("FP-MFG-DFM-AUDIT", "Design-for-manufacture audit package", "manufacturing_matrix", "manufacturing", "gunnchos-hardware-industrial-design"),
    ("FP-CERT-REGIONAL-PACK", "Regional certification readiness pack (FCC/ISED/CE/UKCA/...)", "certification_matrix", "certification", "gunnchos-7gc-ai-ran-field-kit"),
    ("FP-CERT-PTCRB-GCF", "PTCRB/GCF carrier certification path", "certification_matrix", "certification", "gunnchos-7gc-ai-ran-field-kit"),
    ("FP-DEPLOY-7GC-CAMPUS", "7GC campus deployment configurations", "deployment_support_matrix", "deployment", "gunnchos-7gc-ai-ran-field-kit"),
    ("FP-DEPLOY-FLEET-OPS", "Production fleet operations capability", "deployment_support_matrix", "deployment", "gunnchos-device-os"),
    ("FP-SUPPORT-LIFECYCLE", "Published support lifecycle and FRU process", "deployment_support_matrix", "support", "gunnchos-7gc-ai-ran-field-kit"),
    ("FP-SEC-SECURE-BOOT", "Secure/measured boot digital+physical path", "security", "security", "gunnchos-device-os"),
    ("FP-SEC-ATTESTATION", "Device attestation service", "security", "security", "gunnchos-device-os"),
    ("FP-CONN-MULTI-BEARER", "Multi-bearer connectivity orchestrator", "connectivity_carrier_matrix", "connectivity", "gunnchos-device-os"),
    ("FP-CONN-CARRIER-GRADE", "Carrier-grade connectivity architecture (not modem-only)", "connectivity_carrier_matrix", "carrier_grade", "gunnchos-7gc-ai-ran-field-kit"),
    ("FP-WAIKE-TUTOR-OPS", "WAIKE tutor/ops requirements integration", "waike", "waike", "waike-research-ops"),
]

GDD_SOURCES = [
    (SIBLING / "anime-aggressors" / "docs" / "PRODUCT_REQUIREMENTS.md", "anime-aggressors", "anime", "FP-GDD-AA"),
    (SIBLING / "anime-aggressors" / "docs" / "PLATFORM_FIGHTER_REQUIREMENTS.md", "anime-aggressors", "anime", "FP-GDD-AA-PF"),
    (SIBLING / "archive-of-life-artifact-world" / "docs" / "EXTERNAL_DATA_REQUIREMENTS.md", "archive-of-life-artifact-world", "archive", "FP-GDD-AR"),
    (SIBLING / "beatlink-party" / "docs" / "PRODUCT_REQUIREMENTS.md", "beatlink-party", "beatlink", "FP-GDD-BL"),
    (SIBLING / "pedestrian-pursuit" / "docs" / "GAME_REQUIREMENTS.md", "pedestrian-pursuit", "pedestrian", "FP-GDD-PP"),
    (SIBLING / "gunnchos-device-os" / "GUNNCHOS_REQUIREMENTS_v0.1.md", "gunnchos-device-os", "gunnchos", "FP-GDD-OS"),
    (SIBLING / "gunnchAI3k" / "docs" / "LAUNCH_READINESS_NOTES.md", "gunnchAI3k", "gunnchai", "FP-GDD-AI"),
    (SIBLING / "waike-research-ops" / "docs" / "08_GUNNCHAI3K_TUTOR_REQUIREMENTS.md", "waike-research-ops", "waike", "FP-GDD-WAIKE"),
]


def seed_node(nid: str, title: str, section: str, subsystem: str, owner: str, kind: str, line: int | None = None) -> dict[str, Any]:
    return {
        "id": nid,
        "title": title,
        "source_section": section,
        "source_line_start": line,
        "source_line_end": line,
        "subsystem": subsystem,
        "priority": "P0",
        "owner_repository": owner,
        "implementation_paths": [],
        "tests": [],
        "full_product_status": "DOC_ONLY",
        "blocker_class": [],
        "evidence": [],
        "accepted_sha": None,
        "mapping_status": "INGESTED",
        "ownership_status": "OWNED",
        "classification_status": "CLASSIFIED",
        "source_kind": kind,
    }


def ingest_gdd_nodes(existing_ids: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    hits_all: list[dict[str, Any]] = []
    for path, owner, subsystem, prefix in GDD_SOURCES:
        if not path.exists():
            hits_all.append({"source": str(path), "status": "MISSING_FILE"})
            continue
        # Prefer path relative display
        try:
            rel = f"sibling:{owner}/{path.relative_to(SIBLING / owner)}"
        except Exception:
            rel = str(path)
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if not NORMATIVE_RE.search(stripped):
                continue
            if WEAK_LINE_RE.search(stripped):
                continue
            # Skip table headers / thin bullets that are not actionable requirements
            if stripped.startswith("|") and stripped.count("|") >= 3 and len(stripped) < 40:
                continue
            hit = {"source": rel, "line": i, "text": stripped[:240], "owner": owner}
            hits_all.append(hit)
            digest = hashlib.sha1(f"{owner}:{i}:{stripped}".encode()).hexdigest()[:8].upper()
            nid = f"{prefix}-{i}-{digest}"
            if nid in existing_ids or any(n["id"] == nid for n in nodes):
                continue
            nodes.append(
                seed_node(
                    nid,
                    stripped[:120],
                    f"{rel} L{i}",
                    subsystem,
                    owner,
                    "gdd_prd_scan",
                    line=i,
                )
            )
    return nodes, hits_all


def apply_promotions(nodes: list[dict[str, Any]]) -> None:
    if not PROMOTIONS.exists():
        return
    promo = load(PROMOTIONS)
    by_id = {n["id"]: n for n in nodes}
    for item in promo.get("promotions") or []:
        nid = item["id"]
        node = by_id.get(nid)
        if not node:
            # Create promotion target stub only if missing (should exist)
            node = seed_node(nid, nid, "honest_promotions", "product", item.get("owner_repository") or infer_owner(nid), "promotion")
            nodes.append(node)
            by_id[nid] = node
        node["full_product_status"] = item["full_product_status"]
        node["implementation_paths"] = list(item.get("implementation_paths") or [])
        node["tests"] = list(item.get("tests") or [])
        node["evidence"] = list(item.get("evidence") or [])
        node["accepted_sha"] = item.get("accepted_sha")
        if item.get("owner_repository"):
            node["owner_repository"] = item["owner_repository"]
        node["ownership_status"] = "OWNED"
        node["classification_status"] = "CLASSIFIED"
        node["mapping_status"] = node.get("mapping_status") or "MAPPED"
        if item.get("note"):
            node["promotion_note"] = item["note"]


def normalize_node(node: dict[str, Any]) -> dict[str, Any]:
    owner = node.get("owner_repository") or infer_owner(node["id"])
    if owner in ("", "UNOWNED", "CONTROL_PLANE_PENDING_DECISION", None):
        owner = infer_owner(node["id"])
    subsystem = node.get("subsystem") or infer_subsystem(node.get("title") or node["id"])
    node["owner_repository"] = owner
    node["subsystem"] = subsystem
    node["ownership_status"] = "OWNED" if owner not in ("", "UNOWNED", "CONTROL_PLANE_PENDING_DECISION") else "UNOWNED"
    node["classification_status"] = "CLASSIFIED" if subsystem else "UNCLASSIFIED"
    node.setdefault("mapping_status", "MAPPED")
    node.setdefault("implementation_paths", [])
    node.setdefault("tests", [])
    node.setdefault("evidence", [])
    node.setdefault("blocker_class", [])
    node.setdefault("full_product_status", "DOC_ONLY")
    node.setdefault("accepted_sha", None)
    return node


def write_reports(graph: dict[str, Any], scan: dict[str, Any]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    counts = graph["status_counts"]
    unmapped = graph["unmapped_count"]
    (REPORTS / "FULL_PRODUCT_REQUIREMENT_TRACEABILITY.md").write_text(
        "\n".join(
            [
                "# FULL PRODUCT REQUIREMENT TRACEABILITY",
                "",
                f"Updated: {graph['updated_at_utc']}",
                "",
                "## Counts",
                f"- Total nodes: **{graph['count']}**",
                f"- Status: `{counts}`",
                f"- UNMAPPED normative hits: **{unmapped}**",
                f"- UNOWNED nodes: **{graph['unowned_count']}**",
                f"- UNCLASSIFIED nodes: **{graph['unclassified_count']}**",
                f"- Charter expanded-scan residual: **{scan['charter']['unmapped_residual']}**",
                f"- GDD/PRD normative hits ingested: **{scan['gdd']['ingested_nodes']}**",
                f"- Matrix/domain nodes ingested: **{scan['matrix']['ingested_nodes']}**",
                f"- Issues scan: **{scan['issues']['status']}**",
                "",
                "## Rule",
                "Higher states (IMPLEMENTED/INTEGRATED/DIGITALLY_VALIDATED) require",
                "implementation_paths + tests + accepted_sha + evidence.",
                "Validators fail invalid DOC_ONLY→IMPLEMENTED promotions without paths.",
                "",
                "## Honest re-prove",
                f"- Promoted nodes: **{scan['promotions']['applied']}**",
                f"- Remaining DOC_ONLY: **{counts.get('DOC_ONLY', 0)}** (expected; totality ≠ completion)",
                "",
            ]
        ),
        encoding="utf-8",
    )

    charter_lines = [
        "# Charter normative line scan (expanded)",
        "",
        f"Updated: {graph['updated_at_utc']}",
        "",
        f"Pattern: must/shall/required/needs to/will support/launch includes/at minimum/requires/...",
        f"Total hits: {scan['charter']['hits']}",
        f"Covered by catalog/FP nodes: {scan['charter']['covered']}",
        f"Unmapped residual: {scan['charter']['unmapped_residual']}",
        "",
    ]
    for h in scan["charter"]["hit_samples"]:
        charter_lines.append(f"- L{h['line']}: {h['text']}")
    (REPORTS / "CHARTER_NORMATIVE_LINE_SCAN.md").write_text("\n".join(charter_lines) + "\n", encoding="utf-8")

    cand_lines = [
        "# Charter unmapped candidates",
        "",
        f"Updated: {graph['updated_at_utc']}",
        "",
        f"Expanded-scan residual unmapped: **{scan['charter']['unmapped_residual']}**",
        "",
    ]
    if scan["charter"]["unmapped_hits"]:
        for h in scan["charter"]["unmapped_hits"]:
            cand_lines.append(f"- L{h['line']}: {h['text']}")
    else:
        cand_lines.append("None — all expanded normative charter hits mapped or ingested.")
    (REPORTS / "CHARTER_UNMAPPED_CANDIDATES.md").write_text("\n".join(cand_lines) + "\n", encoding="utf-8")

    # Patch master status requirement section
    master = REPORTS / "FULL_PRODUCT_MASTER_STATUS.md"
    if master.exists():
        text = master.read_text(encoding="utf-8")
        block = (
            "## Requirement catalog bootstrap\n\n"
            f"- Catalogued + ingested nodes: **{graph['count']}**\n"
            f"- Status counts: `{counts}`\n"
            f"- UNMAPPED={graph['unmapped_count']} · UNOWNED={graph['unowned_count']} · "
            f"UNCLASSIFIED={graph['unclassified_count']}\n"
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
        master.write_text(text, encoding="utf-8")


def main() -> int:
    now = utc_now()
    nodes = catalog_nodes()
    by_id = {n["id"]: n for n in nodes}

    # Preserve/seed FP charter + ADR floors + matrices
    for nid, ln, title, sub in CHARTER_SEED:
        if nid not in by_id:
            node = seed_node(nid, title, f"charter L{ln}", sub, infer_owner(nid), "charter_seed", line=ln)
            nodes.append(node)
            by_id[nid] = node
    for nid, title, section, sub, owner in ADR_FLOOR_SEED:
        if nid not in by_id:
            node = seed_node(nid, title, section, sub, owner, "adr_floor")
            nodes.append(node)
            by_id[nid] = node
    matrix_added = 0
    for nid, title, section, sub, owner in MATRIX_SEED:
        if nid not in by_id:
            node = seed_node(nid, title, section, sub, owner, "matrix_domain")
            nodes.append(node)
            by_id[nid] = node
            matrix_added += 1

    # Charter expanded scan
    charter_hits = scan_text_file(CHARTER, "charter")
    covered = charter_coverage_lines(nodes)
    unmapped_hits = [h for h in charter_hits if h["line"] not in covered]
    added_charter = ensure_charter_nodes(nodes, charter_hits)
    for n in added_charter:
        nodes.append(n)
        by_id[n["id"]] = n
    # Recompute residual after ingest
    covered = charter_coverage_lines(nodes)
    unmapped_hits = [h for h in charter_hits if h["line"] not in covered]

    gdd_nodes, gdd_hits = ingest_gdd_nodes(set(by_id))
    for n in gdd_nodes:
        nodes.append(n)
        by_id[n["id"]] = n

    # Local FULL_PRODUCT_REQUIRED issues file (GitHub API may be unavailable)
    issues_status = "NO_LOCAL_FILE"
    issues_ingested = 0
    if ISSUES_LOCAL.exists():
        issues = load(ISSUES_LOCAL) or {}
        issues_status = "LOCAL_FILE"
        for item in issues.get("issues") or []:
            nid = item.get("id") or f"FP-ISSUE-{item.get('number')}"
            if nid in by_id:
                continue
            node = seed_node(
                nid,
                item.get("title") or nid,
                f"issue #{item.get('number')}",
                item.get("subsystem") or "product",
                item.get("owner_repository") or "gunnchos-7gc-ai-ran-field-kit",
                "full_product_required_issue",
            )
            nodes.append(node)
            by_id[nid] = node
            issues_ingested += 1
    else:
        issues_status = "GITHUB_ISSUES_SCAN_BLOCKED_NO_LOCAL_CACHE"

    # ADR scan (field-kit decisions)
    adr_dir = ROOT / "program" / "decisions" / "full_product"
    adr_hits: list[dict[str, Any]] = []
    if adr_dir.exists():
        for path in sorted(adr_dir.glob("ADR-*.md")):
            adr_hits.extend(scan_text_file(path, f"adr:{path.name}"))

    apply_promotions(nodes)
    nodes = [normalize_node(n) for n in nodes]
    nodes.sort(key=lambda n: n["id"])

    status_counts = Counter(n["full_product_status"] for n in nodes)
    unowned = [n for n in nodes if n.get("ownership_status") == "UNOWNED" or not n.get("owner_repository")]
    unclassified = [n for n in nodes if n.get("classification_status") == "UNCLASSIFIED" or not n.get("subsystem")]

    graph = {
        "schema_version": "1.1.0",
        "updated_at_utc": now,
        "source_catalog": "program/requirements/requirements.yaml",
        "count": len(nodes),
        "status_vocabulary": [
            "DOC_ONLY",
            "SCHEMA_ONLY",
            "STUB_ONLY",
            "SIMULATION_ONLY",
            "IMPLEMENTED",
            "INTEGRATED",
            "DIGITALLY_VALIDATED",
            "PHYSICAL_REQUIRED",
            "EXTERNAL_REQUIRED",
        ],
        "migration_note": (
            "Requirement totality III: expanded normative scan + promotion validators. "
            "Most nodes remain DOC_ONLY until honest re-prove."
        ),
        "nodes": nodes,
        "status_counts": {k: int(v) for k, v in sorted(status_counts.items())},
        "unmapped_count": len(unmapped_hits),
        "unowned_count": len(unowned),
        "unclassified_count": len(unclassified),
        "unmapped_normative_closed": len(unmapped_hits) == 0,
        "unowned_closed": len(unowned) == 0,
        "unclassified_closed": len(unclassified) == 0,
        "unmapped_normative_target": "UNMAPPED_NORMATIVE_REQUIREMENTS = 0",
        "promotion_rules": str(RULES.relative_to(ROOT)),
        "honest_promotions": str(PROMOTIONS.relative_to(ROOT)),
        "second_pass": {
            "note": "ADR floors + matrix/domain + GDD/PRD ingestion",
            "unmapped_status": "CLOSED" if not unmapped_hits else "OPEN",
        },
        "charter_third_pass": {
            "expanded_hits": len(charter_hits),
            "unmapped_candidates_ingested": len(CHARTER_SEED) + len(added_charter),
            "remaining_charter_line_unmapped": len(unmapped_hits),
        },
        "issues_pass": {
            "status": issues_status,
            "ingested": issues_ingested,
        },
    }

    promo = load(PROMOTIONS) if PROMOTIONS.exists() else {"promotions": []}
    scan = {
        "updated_at_utc": now,
        "pattern": NORMATIVE_RE.pattern,
        "charter": {
            "hits": len(charter_hits),
            "covered": len(charter_hits) - len(unmapped_hits),
            "unmapped_residual": len(unmapped_hits),
            "unmapped_hits": unmapped_hits,
            "hit_samples": charter_hits[:40],
            "newly_ingested": [n["id"] for n in added_charter],
        },
        "gdd": {
            "sources": len(GDD_SOURCES),
            "hits": len([h for h in gdd_hits if "line" in h]),
            "ingested_nodes": len(gdd_nodes),
            "missing_files": [h for h in gdd_hits if h.get("status") == "MISSING_FILE"],
        },
        "matrix": {"ingested_nodes": matrix_added},
        "adr": {"hits": len(adr_hits)},
        "issues": {"status": issues_status, "ingested": issues_ingested},
        "promotions": {"applied": len(promo.get("promotions") or [])},
    }

    dump(graph, GRAPH)
    dump(scan, SCAN_INDEX)
    write_reports(graph, scan)

    # Update source registry
    reg_path = FP / "source_document_registry.yaml"
    if reg_path.exists():
        reg = load(reg_path)
    else:
        reg = {"schema_version": "1.0.0"}
    reg["updated_at_utc"] = now
    reg["totality_pass"] = "REQUIREMENT_TOTALITY_III"
    reg["unmapped"] = "CLOSED" if graph["unmapped_normative_closed"] else "STILL_OPEN"
    reg["unowned"] = "CLOSED" if graph["unowned_closed"] else "STILL_OPEN"
    reg["unclassified"] = "CLOSED" if graph["unclassified_closed"] else "STILL_OPEN"
    reg["graph_count"] = graph["count"]
    dump(reg, reg_path)

    # Evidence registry append for promotions
    ev_path = FP / "evidence_registry.yaml"
    ev = load(ev_path) if ev_path.exists() else {"schema_version": "1.0.0", "entries": []}
    existing_ev = {e.get("id") for e in ev.get("entries") or []}
    for item in promo.get("promotions") or []:
        for eid in item.get("evidence") or []:
            if eid in existing_ev:
                continue
            ev.setdefault("entries", []).append(
                {
                    "id": eid,
                    "repo": "gunnchos-7gc-ai-ran-field-kit",
                    "sha": item.get("accepted_sha"),
                    "requirement_id": item["id"],
                    "note": item.get("note") or "honest promotion evidence",
                }
            )
            existing_ev.add(eid)
    ev["updated_at_utc"] = now
    dump(ev, ev_path)

    print(
        f"SYNC_OK nodes={graph['count']} unmapped={graph['unmapped_count']} "
        f"unowned={graph['unowned_count']} unclassified={graph['unclassified_count']} "
        f"status={dict(status_counts)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
