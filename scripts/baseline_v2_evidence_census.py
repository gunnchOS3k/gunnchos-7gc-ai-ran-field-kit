#!/usr/bin/env python3
"""Phase B.2 accepted-main evidence census for Baseline V2."""

from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CANONICAL_REPOS = [
    "gunnchos-7gc-ai-ran-field-kit",
    "gunnchos-research-portal",
    "gunnchos-device-os",
    "gunnchos-hardware-industrial-design",
    "gunnchAI3k",
    "edge-io-measurement-node",
    "anime-aggressors",
    "pedestrian-pursuit",
    "archive-of-life-artifact-world",
    "beatlink-party",
    "7gc-digital-twin",
    "spectrumx-ai-ran-gary",
    "ntn-resilience-sim",
    "readygary-6g-beam-selection",
    "waike-research-ops",
    "gunnchos-emergent-service-intent-protocols",
    "gunnchos-gpu-nr-baseband-platform",
]

END_GOAL_FAMILIES: list[dict[str, Any]] = [
    {"id": 1, "key": "release_control_plane", "name": "Release/control plane"},
    {"id": 2, "key": "gunnchos_os", "name": "gunnchOS"},
    {"id": 3, "key": "gunnchdevice_lab", "name": "gunnchDevice Lab"},
    {"id": 4, "key": "gunnchai", "name": "gunnchAI"},
    {"id": 5, "key": "waike", "name": "WAIKE"},
    {"id": 6, "key": "anime_aggressors", "name": "Anime Aggressors"},
    {"id": 7, "key": "pedestrian_pursuit", "name": "Pedestrian Pursuit"},
    {"id": 8, "key": "archive_of_life", "name": "Archive of Life"},
    {"id": 9, "key": "beatlink", "name": "BeatLink"},
    {"id": 10, "key": "device_quartet_hardware", "name": "Device Quartet hardware"},
    {"id": 11, "key": "first_party_dock", "name": "First-party Dock"},
    {"id": 12, "key": "edge_io_rings", "name": "Edge I/O Rings"},
    {"id": 13, "key": "readygary", "name": "ReadyGary"},
    {"id": 14, "key": "spectrumx_ai_ran", "name": "SpectrumX/AI-RAN"},
    {"id": 15, "key": "digital_twin", "name": "7GC Digital Twin"},
    {"id": 16, "key": "ntn_resilience", "name": "NTN resilience"},
    {"id": 17, "key": "gpu_nr_baseband", "name": "GPU NR baseband"},
    {"id": 18, "key": "r6g_field_kit", "name": "R6G/field kit"},
    {"id": 19, "key": "emergent_protocols", "name": "Emergent protocols"},
    {"id": 20, "key": "research_papers", "name": "Research Papers I-III"},
    {"id": 21, "key": "security_privacy_supply_chain", "name": "Security/privacy/supply chain"},
    {"id": 22, "key": "publishing_platform_release", "name": "Publishing/platform release"},
    {"id": 23, "key": "carrier_cellular_ntn", "name": "Carrier/cellular/NTN"},
    {"id": 24, "key": "manufacturing_commercialization", "name": "Manufacturing/commercialization"},
    {"id": 25, "key": "regulatory_certification", "name": "Regulatory/certification"},
    {"id": 26, "key": "human_validation", "name": "Human validation"},
    {"id": 27, "key": "field_deployment_7gc", "name": "Field deployment/7GC"},
    {"id": 28, "key": "standards_evolution_6g", "name": "Standards evolution/standardized 6G"},
]

CANONICAL_CURRENT_LEVELS = {
    "L0_DEFINED",
    "L1_IMPLEMENTED",
    "L2_DIGITALLY_VERIFIED",
    "L3_USER_READY_DIGITAL_RC",
    "L4_HUMAN_OR_TARGET_HARDWARE_VALIDATED",
    "L5_EXTERNAL_OR_CERTIFIED",
    "L6_PRODUCTION_OR_FIELD",
}

WORK_STATES_COMPLETE = {"DIGITAL_IMPLEMENTATION_COMPLETE", "COMPLETE_AT_REQUIRED_LEVEL"}
WORK_STATES_OPEN = {
    "DIGITAL_IMPLEMENTATION_OPEN",
    "DIGITAL_VALIDATION_OPEN",
    "EVIDENCE_MAPPING_OPEN",
}
WORK_STATES_PREP = {
    "DIGITAL_PREPARATION_COMPLETE_HUMAN_PENDING",
    "DIGITAL_PREPARATION_COMPLETE_PHYSICAL_PENDING",
    "DIGITAL_PREPARATION_COMPLETE_EXTERNAL_PENDING",
}
WORK_STATES_PENDING = {
    "STANDARD_PENDING",
    "CERTIFICATION_PENDING",
    "CARRIER_PENDING",
    "VENDOR_PENDING",
    "OWNER_DECISION_PENDING",
    "HUMAN_PENDING",
    "PHYSICAL_PENDING",
    "EXTERNAL_PENDING",
}

SKIP_DIR_PARTS = {
    "node_modules",
    ".git",
    "build",
    "dist",
    "target",
    "__pycache__",
    ".venv",
    "venv",
    ".godot",
    ".import",
}
SKIP_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".apk",
    ".so",
    ".dylib",
    ".bin",
    ".glb",
    ".gltf",
    ".wav",
    ".mp3",
    ".mp4",
    ".sock",
}
MAX_FILE_BYTES = 512_000

INDEX_PREFIXES = (
    "README",
    "STATUS",
    "RELEASE",
    "REPRODUCIBILITY",
    "EVIDENCE",
)
INDEX_DIRS = (
    "artifacts",
    "docs",
    "tests",
    "scripts",
    "src",
    "app",
    "firmware",
    "hardware",
    "paper",
    "papers",
    "program",
    "curriculum",
    "results",
)

L0_CHARTER_IDS = {
    "CHARTER_NARRATIVE",
    "REPO_OWNERSHIP_MAP",
    "CLAIM_BOUNDARIES",
    "COMPLETION_REGISTER_V1",
}

OWNER_FAMILY_MAP: dict[str, list[int]] = {
    "gunnchos-device-os": [2, 3],
    "gunnchAI3k": [4],
    "waike-research-ops": [5],
    "anime-aggressors": [6],
    "pedestrian-pursuit": [7],
    "archive-of-life-artifact-world": [8],
    "beatlink-party": [9],
    "gunnchos-hardware-industrial-design": [10, 11],
    "edge-io-measurement-node": [12],
    "readygary-6g-beam-selection": [13, 20],
    "spectrumx-ai-ran-gary": [14, 20],
    "7gc-digital-twin": [15, 27],
    "ntn-resilience-sim": [16, 23],
    "gunnchos-gpu-nr-baseband-platform": [17, 23],
    "gunnchos-7gc-ai-ran-field-kit": [1, 18, 20, 21],
    "gunnchos-emergent-service-intent-protocols": [19],
    "gunnchos-research-portal": [22],
}

SUBSYSTEM_FAMILY_MAP: dict[str, list[int]] = {
    "ecosystem": [1],
    "os": [2],
    "ai": [4],
    "applications": [5, 6, 7, 8, 9],
    "games": [6, 7, 8, 9],
    "rings": [12],
    "device": [10, 11],
    "connectivity": [23],
    "7gc": [27],
    "carrier_grade": [23],
    "standards": [28],
    "evidence": [1, 20],
    "gates": [1],
}


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 120) -> str:
    try:
        env = os.environ.copy()
        env.setdefault("GH_PAGER", "cat")
        return subprocess.check_output(
            cmd, cwd=cwd, text=True, stderr=subprocess.DEVNULL, timeout=timeout, env=env
        ).strip()
    except Exception:
        return ""


def repo_path(repos_root: Path, repo: str) -> Path:
    return repos_root / repo


def ensure_repo(repos_root: Path, temp_root: Path, repo: str) -> tuple[Path, str]:
    local = repo_path(repos_root, repo)
    if local.is_dir() and (local / ".git").exists():
        run(["git", "fetch", "origin", "main"], cwd=local)
        sha = run(["git", "rev-parse", "origin/main"], cwd=local)
        if sha:
            return local, sha
    temp_root.mkdir(parents=True, exist_ok=True)
    clone = temp_root / repo
    if not (clone / ".git").exists():
        run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                "main",
                f"https://github.com/gunnchOS3k/{repo}.git",
                str(clone),
            ],
            timeout=300,
        )
    else:
        run(["git", "fetch", "origin", "main"], cwd=clone)
    sha = run(["git", "rev-parse", "origin/main"], cwd=clone) or run(["git", "rev-parse", "HEAD"], cwd=clone)
    return clone, sha


def should_index_path(rel: str) -> bool:
    parts = rel.split("/")
    if any(p in SKIP_DIR_PARTS for p in parts):
        return False
    base = Path(rel).name
    if any(base.startswith(p) for p in INDEX_PREFIXES):
        return True
    if parts[0] in INDEX_DIRS:
        return True
    upper = rel.upper()
    if any(x in upper for x in ("STATUS", "EVIDENCE", "REPRODUC", "RELEASE")):
        return True
    return False


def classify_artifact_type(rel: str) -> str:
    low = rel.lower()
    if low.startswith("tests/"):
        return "test"
    if "/artifacts/" in low or low.startswith("artifacts/"):
        return "artifact_json" if low.endswith(".json") else "artifact_md"
    if low.startswith("paper/") or low.startswith("papers/"):
        return "paper"
    if low.startswith("docs/"):
        return "doc"
    if low.startswith(("src/", "app/", "firmware/", "hardware/")):
        return "implementation"
    if low.startswith("scripts/"):
        return "script"
    if low.startswith("program/"):
        return "program"
    if low.endswith(".json"):
        return "json"
    if low.endswith(".md"):
        return "markdown"
    return "other"


def git_list_files(repo_dir: Path) -> list[str]:
    raw = run(["git", "ls-tree", "-r", "--name-only", "origin/main"], cwd=repo_dir)
    if not raw:
        raw = run(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=repo_dir)
    return [line for line in raw.splitlines() if line and should_index_path(line)]


def git_show_file(repo_dir: Path, rel: str) -> str | None:
    ext = Path(rel).suffix.lower()
    if ext in SKIP_EXTENSIONS:
        return None
    blob = run(["git", "cat-file", "-s", f"origin/main:{rel}"], cwd=repo_dir)
    if not blob:
        blob = run(["git", "cat-file", "-s", f"HEAD:{rel}"], cwd=repo_dir)
    try:
        if blob and int(blob) > MAX_FILE_BYTES:
            return None
    except ValueError:
        pass
    content = run(["git", "show", f"origin/main:{rel}"], cwd=repo_dir, timeout=30)
    if not content:
        content = run(["git", "show", f"HEAD:{rel}"], cwd=repo_dir, timeout=30)
    return content or None


def extract_tokens(content: str) -> list[str]:
    tokens: set[str] = set()
    for m in re.finditer(r"[A-Z][A-Z0-9_]{4,}", content):
        tokens.add(m.group(0))
    for m in re.finditer(r'"([A-Za-z0-9_.-]+)"\s*:\s*(true|"PASS"|"pass")', content):
        tokens.add(m.group(1))
    return sorted(tokens)


def extract_requirement_ids(content: str) -> list[str]:
    return sorted(set(re.findall(r"\b[A-Z]{2,}(?:-[A-Z0-9]+)+\b", content)))


def extract_verification_class(rel: str, content: str) -> str:
    low = rel.lower()
    if low.startswith("tests/"):
        return "UNIT_VERIFIED"
    if "reproduc" in low or "REPRODUC" in content:
        return "DIGITALLY_REPRODUCED"
    if "INDEPENDENT" in content or "VP_" in content:
        return "INDEPENDENTLY_VERIFIED_DIGITAL"
    if "RC_" in content or "DIGITAL_RC" in content:
        return "INTEGRATION_VERIFIED"
    if low.endswith(".json") and ("PASS" in content or '"ok": true' in content):
        return "INTEGRATION_VERIFIED"
    return "NOT_VERIFIED"


@dataclass
class EvidenceRecord:
    repo: str
    accepted_main_sha: str
    path: str
    artifact_type: str
    tokens_or_results: list[str] = field(default_factory=list)
    requirement_ids: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    verification_class: str = "NOT_VERIFIED"
    freshness: str = "accepted_main"


@dataclass
class EvidenceIndex:
    records: list[EvidenceRecord] = field(default_factory=list)
    by_requirement_id: dict[str, list[EvidenceRecord]] = field(default_factory=lambda: defaultdict(list))
    by_token: dict[str, list[EvidenceRecord]] = field(default_factory=lambda: defaultdict(list))
    by_repo: dict[str, list[EvidenceRecord]] = field(default_factory=lambda: defaultdict(list))
    repo_shas: dict[str, str] = field(default_factory=dict)
    traceability_hits: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))


def build_evidence_index(repos_root: Path, temp_root: Path, repos: list[str] | None = None) -> EvidenceIndex:
    index = EvidenceIndex()
    for repo in repos or CANONICAL_REPOS:
        repo_dir, sha = ensure_repo(repos_root, temp_root, repo)
        index.repo_shas[repo] = sha
        files = git_list_files(repo_dir)
        for rel in files:
            if Path(rel).suffix.lower() not in {".json", ".md", ".yaml", ".yml", ".py", ".gd", ".rs", ".toml"}:
                if not any(rel.startswith(d + "/") for d in INDEX_DIRS):
                    continue
            content = git_show_file(repo_dir, rel)
            if content is None:
                continue
            req_ids = extract_requirement_ids(content)
            tokens = extract_tokens(content)
            rec = EvidenceRecord(
                repo=repo,
                accepted_main_sha=sha,
                path=rel,
                artifact_type=classify_artifact_type(rel),
                tokens_or_results=tokens[:40],
                requirement_ids=req_ids[:40],
                capabilities=[t for t in tokens if t.endswith("_PASS") or t.endswith("_READY")][:20],
                verification_class=extract_verification_class(rel, content),
                freshness="accepted_main",
            )
            index.records.append(rec)
            index.by_repo[repo].append(rec)
            for rid in req_ids:
                index.by_requirement_id[rid].append(rec)
            for tok in tokens:
                index.by_token[tok].append(rec)
    return index


def load_traceability_maps(field_kit_root: Path) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = defaultdict(list)
    patterns = [
        "program/reports/*TRACEABILITY*",
        "program/full_product/reports/*",
        "ROLE_REQUIREMENT_TRACEABILITY.md",
        "program/requirements/*.yaml",
    ]
    for pat in patterns:
        for path in field_kit_root.glob(pat):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for rid in extract_requirement_ids(text):
                hits[rid].append(str(path.relative_to(field_kit_root)))
    return hits


def map_implementation_state(yaml_state: str) -> str:
    s = (yaml_state or "").upper()
    if s in ("IMPLEMENTED",):
        return "IMPLEMENTED"
    if s in ("IN_PROGRESS", "PARTIAL"):
        return "PARTIALLY_IMPLEMENTED"
    if s in ("SUPERSEDED",):
        return "SUPERSEDED"
    if s in ("NOT_APPLICABLE", "N/A"):
        return "NOT_APPLICABLE"
    return "NOT_IMPLEMENTED"


def map_verification_state(yaml_state: str, evidence: EvidenceRecord | None) -> str:
    s = (yaml_state or "").upper()
    if s == "INDEPENDENTLY_VALIDATED":
        return "INDEPENDENTLY_VERIFIED_DIGITAL"
    if s in ("VALIDATED", "PASS"):
        return "INTEGRATION_VERIFIED"
    if evidence:
        vc = evidence.verification_class
        if vc != "NOT_VERIFIED":
            return vc
    if s in ("NOT_STARTED", "FAIL", "IN_PROGRESS"):
        return "NOT_VERIFIED"
    return "NOT_VERIFIED"


def infer_current_level(
    implementation_state: str,
    verification_state: str,
    program_gate: int | None,
    work_state: str,
) -> str:
    if work_state in WORK_STATES_PENDING:
        if work_state in {"HUMAN_PENDING", "PHYSICAL_PENDING"}:
            return "L4_HUMAN_OR_TARGET_HARDWARE_VALIDATED"
        if work_state in {"EXTERNAL_PENDING", "CERTIFICATION_PENDING"}:
            return "L5_EXTERNAL_OR_CERTIFIED"
        if work_state in {"CARRIER_PENDING", "VENDOR_PENDING", "STANDARD_PENDING"}:
            return "L6_PRODUCTION_OR_FIELD"
    if verification_state in {
        "PRODUCTION_FIELD_VERIFIED",
    }:
        return "L6_PRODUCTION_OR_FIELD"
    if verification_state in {"EXTERNALLY_VERIFIED", "CERTIFIED", "TARGET_HARDWARE_VERIFIED", "HUMAN_VERIFIED"}:
        return "L4_HUMAN_OR_TARGET_HARDWARE_VALIDATED"
    if verification_state in {"INDEPENDENTLY_VERIFIED_DIGITAL"}:
        return "L3_USER_READY_DIGITAL_RC"
    if verification_state in {"DIGITALLY_REPRODUCED", "INTEGRATION_VERIFIED", "UNIT_VERIFIED"}:
        return "L2_DIGITALLY_VERIFIED"
    if implementation_state in {"IMPLEMENTED", "PARTIALLY_IMPLEMENTED"}:
        return "L1_IMPLEMENTED"
    return "L0_DEFINED"


def blocker_classes(req: dict[str, Any]) -> list[str]:
    blob = " ".join(
        [
            " ".join(req.get("blockers") or []),
            req.get("notes") or "",
            req.get("title") or "",
        ]
    ).upper()
    out: list[str] = []
    rules = [
        ("PHYSICAL", ("PHYSICAL", "FAB_", "EVT0", "MANUFACTUR", "ENCLOSURE", "BATTERY", "THERMAL", "RFQ", "LOCAL_HARDWARE", "PROTOTYPE")),
        ("HUMAN", ("HUMAN", "PILOT", "OPERATOR", "CONSENT", "PLAYTEST", "FUN", "BALANCE")),
        ("EXTERNAL", ("EXTERNAL", "NVIDIA", "SIONNA", "AERIAL", "DOI", "PENTEST", "NGC", "BLOCKED_GPU", "OTA")),
        ("STANDARD", ("STANDARD", "IMT2030", "3GPP", "6G")),
        ("CERTIFICATION", ("CERTIF", "REGULATORY", "FCC", "CE_MARK")),
        ("CARRIER", ("CARRIER", "CELLULAR", "MNO", "NTN_DEPLOY")),
        ("VENDOR", ("VENDOR", "SUPPLIER", "NDA")),
        ("OWNER_DECISION", ("OWNER_DECISION", "WP001", "EDMUND", "PRODUCT_CHARTER_APPROVAL", "CHARTER_APPROVAL")),
    ]
    for cls, keys in rules:
        if any(k in blob for k in keys):
            out.append(cls)
    return out


def map_end_goal_families(req: dict[str, Any], search: dict[str, Any] | None = None) -> list[int]:
    families: set[int] = set()
    owner = req.get("owner_repository") or ""
    subsystem = req.get("subsystem") or ""
    rid = req.get("id") or ""
    title = (req.get("title") or "").upper()
    normative = (req.get("normative_text") or "").upper()
    blockers = blocker_classes(req)
    supporting = req.get("supporting_repositories") or []

    families.update(OWNER_FAMILY_MAP.get(owner, []))
    for sr in supporting:
        families.update(OWNER_FAMILY_MAP.get(sr, []))
    families.update(SUBSYSTEM_FAMILY_MAP.get(subsystem, []))

    # Field-kit research / R6G portfolio bridge (repos absent from requirements.yaml owners)
    if owner == "gunnchos-7gc-ai-ran-field-kit":
        if subsystem in ("7gc", "evidence", "gates") or req.get("scientific_evidence_relevant"):
            families.update({13, 14, 16, 17, 18, 19, 20})
        if (req.get("gate") or 0) >= 7:
            families.update({13, 14, 16, 17, 18, 19, 20, 27, 28})

    if search:
        repo_to_families = {
            "readygary-6g-beam-selection": [13, 20],
            "spectrumx-ai-ran-gary": [14, 20],
            "ntn-resilience-sim": [16, 23],
            "gunnchos-gpu-nr-baseband-platform": [17, 23],
            "gunnchos-emergent-service-intent-protocols": [19],
            "gunnchos-research-portal": [22],
            "7gc-digital-twin": [15, 27],
        }
        for hit in search.get("hits") or []:
            families.update(repo_to_families.get(hit.repo, []))

    blob = f"{title} {normative} {rid}"
    keyword_family = [
        ("READYGARY", 13), ("BEAM", 13), ("SPECTRUM", 14), ("AI-RAN", 14), ("AI RAN", 14),
        ("NTN", 16), ("GPU", 17), ("BASEBAND", 17), ("CUPHY", 17), ("EMERGENT", 19),
        ("INTENT PROTOCOL", 19), ("PORTAL", 22), ("PUBLISH", 22), ("CONTACT_SNAPSHOT", 22),
        ("PAPER I", 20), ("PAPER II", 20), ("PAPER III", 20), ("RQ1", 20), ("RQ2", 20),
    ]
    for kw, fid in keyword_family:
        if kw in blob:
            families.add(fid)

    if rid.startswith("PAPER-"):
        families.add(20)
    if "PRIVACY" in rid or "SECURITY" in rid or "BOM" in rid or "SUPPLY" in title:
        families.add(21)
    if "DOCK" in title or "DOCK" in rid:
        families.add(11)
    if "RING" in title or subsystem == "rings":
        families.add(12)
    if "HARDWARE" in title or owner == "gunnchos-hardware-industrial-design":
        families.add(10)
    if "CERTIF" in " ".join(blockers):
        families.add(25)
    if "HUMAN" in blockers:
        families.add(26)
    if "PHYSICAL" in blockers or "VENDOR" in blockers:
        families.add(24)
    if "CARRIER" in blockers or subsystem == "connectivity":
        families.add(23)
    if "STANDARD" in blockers or subsystem == "standards":
        families.add(28)
    if "EXTERNAL" in blockers and any(x in title for x in ("NVIDIA", "GPU", "SIONNA")):
        families.add(17)
    if gate := req.get("gate"):
        if gate >= 7:
            families.update({27, 28})
        if gate >= 4:
            families.add(27)

    if not families:
        families.add(1)
    return sorted(families)


def search_passes(req: dict[str, Any], index: EvidenceIndex, trace_maps: dict[str, list[str]]) -> dict[str, Any]:
    rid = req["id"]
    owner = req.get("owner_repository") or "gunnchos-7gc-ai-ran-field-kit"
    supporting = req.get("supporting_repositories") or []
    search_repos = [owner] + [r for r in supporting if r in CANONICAL_REPOS]
    tokens = list(req.get("required_evidence") or [])
    title_bits = re.findall(r"[A-Za-z0-9_]{4,}", req.get("title") or "")
    tokens.extend(title_bits)

    hits: list[EvidenceRecord] = []
    pass_log: dict[str, list[str]] = {
        "pass1_exact_id": [],
        "pass2_tokens": [],
        "pass3_traceability": [],
        "pass4_implementation": [],
        "pass5_verification": [],
    }

    for rec in index.by_requirement_id.get(rid, []):
        if rec.repo in search_repos or rec.repo in CANONICAL_REPOS:
            hits.append(rec)
            pass_log["pass1_exact_id"].append(f"{rec.repo}:{rec.path}")

    for tok in tokens:
        tok_u = tok.upper()
        for rec in index.by_token.get(tok_u, []) + index.by_token.get(tok, []):
            if rec.repo in search_repos or rec.repo in CANONICAL_REPOS:
                hits.append(rec)
                pass_log["pass2_tokens"].append(f"{rec.repo}:{rec.path} token={tok}")

    for path in trace_maps.get(rid, []):
        pass_log["pass3_traceability"].append(path)

    impl_hits = [
        h
        for h in hits
        if h.artifact_type in {"implementation", "script", "artifact_json", "artifact_md", "program"}
        and not h.path.startswith("tests/")
    ]
    for h in impl_hits:
        pass_log["pass4_implementation"].append(f"{h.repo}:{h.path}")

    verif_hits = [h for h in hits if h.path.startswith("tests/") or h.verification_class != "NOT_VERIFIED"]
    for h in verif_hits:
        pass_log["pass5_verification"].append(f"{h.repo}:{h.path}")

    # dedupe hits preserving order
    seen: set[tuple[str, str]] = set()
    uniq: list[EvidenceRecord] = []
    for h in hits:
        key = (h.repo, h.path)
        if key not in seen:
            seen.add(key)
            uniq.append(h)

    best_impl = impl_hits[0] if impl_hits else (uniq[0] if uniq else None)
    best_verif = verif_hits[0] if verif_hits else None

    return {
        "hits": uniq,
        "best_implementation": best_impl,
        "best_verification": best_verif,
        "pass_log": pass_log,
        "searched_repos": search_repos,
    }


def choose_work_state(
    req: dict[str, Any],
    implementation_state: str,
    verification_state: str,
    search: dict[str, Any],
    blockers: list[str],
) -> tuple[str, str]:
    impl_ev = search.get("best_implementation")
    verif_ev = search.get("best_verification")
    has_impl = impl_ev is not None or implementation_state == "IMPLEMENTED"
    has_verif = verif_ev is not None or verification_state not in ("NOT_VERIFIED",)
    pass_log = search.get("pass_log") or {}
    any_pass = any(pass_log.get(k) for k in pass_log)

    if blockers and not has_impl and not any_pass:
        mapping = {
            "PHYSICAL": "PHYSICAL_PENDING",
            "HUMAN": "HUMAN_PENDING",
            "EXTERNAL": "EXTERNAL_PENDING",
            "STANDARD": "STANDARD_PENDING",
            "CERTIFICATION": "CERTIFICATION_PENDING",
            "CARRIER": "CARRIER_PENDING",
            "VENDOR": "VENDOR_PENDING",
            "OWNER_DECISION": "OWNER_DECISION_PENDING",
        }
        return mapping.get(blockers[0], "OWNER_DECISION_PENDING"), (
            f"Non-digital blocker {blockers[0]}; no accepted-main implementation evidence located."
        )

    if has_impl and has_verif:
        return "DIGITAL_IMPLEMENTATION_COMPLETE", "Accepted-main implementation and verification evidence located."

    if has_impl and not has_verif:
        if blockers:
            prep_map = {
                "HUMAN": "DIGITAL_PREPARATION_COMPLETE_HUMAN_PENDING",
                "PHYSICAL": "DIGITAL_PREPARATION_COMPLETE_PHYSICAL_PENDING",
                "EXTERNAL": "DIGITAL_PREPARATION_COMPLETE_EXTERNAL_PENDING",
            }
            if blockers[0] in prep_map:
                return prep_map[blockers[0]], (
                    f"Implementation evidence on accepted main; verification blocked by {blockers[0]}."
                )
        return "DIGITAL_VALIDATION_OPEN", "Implementation evidence located; digital verification/reproduction proof missing."

    if not any_pass:
        return "EVIDENCE_MAPPING_OPEN", "Five-pass accepted-main search found no evidence mapping for this requirement."

    if blockers:
        prep_map = {
            "HUMAN": "DIGITAL_PREPARATION_COMPLETE_HUMAN_PENDING",
            "PHYSICAL": "DIGITAL_PREPARATION_COMPLETE_PHYSICAL_PENDING",
            "EXTERNAL": "DIGITAL_PREPARATION_COMPLETE_EXTERNAL_PENDING",
        }
        if blockers[0] in prep_map:
            return prep_map[blockers[0]], f"Traceability/token hints only; primary blocker is {blockers[0]}."

    yaml_impl = (req.get("implementation_state") or "").upper()
    if yaml_impl in ("NOT_STARTED", "DOCUMENTED_DESIGN", ""):
        return "DIGITAL_IMPLEMENTATION_OPEN", "No accepted-main implementation artifact; requirement remains digitally unimplemented."

    return "EVIDENCE_MAPPING_OPEN", "Search inconclusive; evidence mapping still open on accepted main."


def reconcile_requirement(
    req: dict[str, Any],
    index: EvidenceIndex,
    trace_maps: dict[str, list[str]],
    field_kit_sha: str,
    wp012_path: str | None,
) -> dict[str, Any]:
    rid = req["id"]
    owner = req.get("owner_repository") or "gunnchos-7gc-ai-ran-field-kit"
    program_gate = req.get("gate")
    sha = index.repo_shas.get(owner, "")
    blockers = blocker_classes(req)
    search = search_passes(req, index, trace_maps)
    end_goals = map_end_goal_families(req, search)

    yaml_impl = req.get("implementation_state") or ""
    yaml_val = req.get("validation_state") or ""

    # L0 charter shortcut with WP-012
    if (rid in L0_CHARTER_IDS or rid.startswith("SYS-MISSION-")) and program_gate == 0 and wp012_path:
        implementation_state = "IMPLEMENTED"
        verification_state = "INTEGRATION_VERIFIED"
        work_state = "DIGITAL_IMPLEMENTATION_COMPLETE"
        current_level = "L2_DIGITALLY_VERIFIED"
        return _row(
            req,
            owner,
            program_gate,
            field_kit_sha or sha,
            wp012_path,
            wp012_path,
            "PASS",
            implementation_state,
            verification_state,
            current_level,
            work_state,
            end_goals,
            "WP-012 VP artifact on accepted field-kit main proves L0 charter digital discoverability.",
            "Owner charter approval may remain human/owner pending.",
            {"pass1_exact_id": [wp012_path]},
            blockers,
        )

    impl_ev = search["best_implementation"]
    verif_ev = search["best_verification"]

    implementation_state = map_implementation_state(yaml_impl)
    if impl_ev or search["pass_log"]["pass4_implementation"]:
        implementation_state = "IMPLEMENTED" if yaml_impl == "IMPLEMENTED" or impl_ev else "PARTIALLY_IMPLEMENTED"

    verification_state = map_verification_state(yaml_val, verif_ev)
    work_state, reason = choose_work_state(req, implementation_state, verification_state, search, blockers)
    current_level = infer_current_level(implementation_state, verification_state, program_gate, work_state)

    impl_path = f"{impl_ev.repo}:{impl_ev.path}" if impl_ev else ""
    verif_path = f"{verif_ev.repo}:{verif_ev.path}" if verif_ev else ""
    token = ""
    if verif_ev and verif_ev.tokens_or_results:
        token = verif_ev.tokens_or_results[0]
    elif impl_ev and impl_ev.tokens_or_results:
        token = impl_ev.tokens_or_results[0]

    return _row(
        req,
        owner,
        program_gate,
        (verif_ev or impl_ev).accepted_main_sha if (verif_ev or impl_ev) else sha,
        impl_path,
        verif_path or impl_path,
        token,
        implementation_state,
        verification_state,
        current_level,
        work_state,
        end_goals,
        reason,
        "Locate or extend accepted-main evidence." if work_state == "EVIDENCE_MAPPING_OPEN" else "Continue digital verification or resolve non-digital blocker.",
        search["pass_log"],
        blockers,
    )


def _row(
    req: dict[str, Any],
    owner: str,
    program_gate: int | None,
    accepted_main_sha: str,
    implementation_evidence: str,
    validation_evidence: str,
    token_or_result: str,
    implementation_state: str,
    verification_state: str,
    current_level: str,
    work_state: str,
    end_goal_families: list[int],
    resolution_reason: str,
    next_action: str,
    search_passes: dict[str, list[str]],
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "requirement_id": req["id"],
        "title": req.get("title"),
        "owner_repo": owner,
        "program_gate": program_gate,
        "end_goal_families": end_goal_families,
        "accepted_main_sha": accepted_main_sha,
        "implementation_evidence": implementation_evidence,
        "validation_evidence": validation_evidence,
        "token_or_result": token_or_result,
        "implementation_state": implementation_state,
        "verification_state": verification_state,
        "current_level": current_level,
        "work_state": work_state,
        "resolution": work_state,
        "engineering_state": work_state,
        "resolution_reason": resolution_reason,
        "next_action": next_action,
        "search_passes": search_passes,
        "blocker_classes": blockers,
        "yaml_implementation_state_hint": req.get("implementation_state"),
        "yaml_validation_state_hint": req.get("validation_state"),
        "subsystem": req.get("subsystem"),
        "blockers": req.get("blockers") or [],
    }


def compute_totals(rows: list[dict[str, Any]]) -> dict[str, int]:
    c = Counter(r["work_state"] for r in rows)
    level_c = Counter(r["current_level"] for r in rows)
    return {
        "ATOMIC_TOTAL": len(rows),
        "IMPLEMENTED": sum(1 for r in rows if r["implementation_state"] == "IMPLEMENTED"),
        "DIGITALLY_VERIFIED": sum(
            1
            for r in rows
            if r["current_level"]
            in {"L2_DIGITALLY_VERIFIED", "L3_USER_READY_DIGITAL_RC", "L4_HUMAN_OR_TARGET_HARDWARE_VALIDATED", "L5_EXTERNAL_OR_CERTIFIED", "L6_PRODUCTION_OR_FIELD"}
        ),
        "USER_READY_DIGITAL_RC": sum(1 for r in rows if r["current_level"] == "L3_USER_READY_DIGITAL_RC"),
        "HUMAN_OR_TARGET_HARDWARE_VALIDATED": sum(
            1 for r in rows if r["current_level"] == "L4_HUMAN_OR_TARGET_HARDWARE_VALIDATED"
        ),
        "EXTERNAL_OR_CERTIFIED": sum(1 for r in rows if r["current_level"] == "L5_EXTERNAL_OR_CERTIFIED"),
        "PRODUCTION_OR_FIELD": sum(1 for r in rows if r["current_level"] == "L6_PRODUCTION_OR_FIELD"),
        "DIGITAL_IMPLEMENTATION_COMPLETE": c.get("DIGITAL_IMPLEMENTATION_COMPLETE", 0) + c.get("COMPLETE_AT_REQUIRED_LEVEL", 0),
        "DIGITAL_IMPLEMENTATION_OPEN": c.get("DIGITAL_IMPLEMENTATION_OPEN", 0),
        "DIGITAL_VALIDATION_OPEN": c.get("DIGITAL_VALIDATION_OPEN", 0),
        "EVIDENCE_MAPPING_OPEN": c.get("EVIDENCE_MAPPING_OPEN", 0),
        "HUMAN_PENDING": c.get("HUMAN_PENDING", 0) + c.get("DIGITAL_PREPARATION_COMPLETE_HUMAN_PENDING", 0),
        "PHYSICAL_PENDING": c.get("PHYSICAL_PENDING", 0) + c.get("DIGITAL_PREPARATION_COMPLETE_PHYSICAL_PENDING", 0),
        "EXTERNAL_PENDING": c.get("EXTERNAL_PENDING", 0) + c.get("DIGITAL_PREPARATION_COMPLETE_EXTERNAL_PENDING", 0),
        "STANDARD_PENDING": c.get("STANDARD_PENDING", 0),
        "CERTIFICATION_PENDING": c.get("CERTIFICATION_PENDING", 0),
        "CARRIER_PENDING": c.get("CARRIER_PENDING", 0),
        "VENDOR_PENDING": c.get("VENDOR_PENDING", 0),
        "OWNER_DECISION_PENDING": c.get("OWNER_DECISION_PENDING", 0),
        "L0_DEFINED": level_c.get("L0_DEFINED", 0),
        "L1_IMPLEMENTED": level_c.get("L1_IMPLEMENTED", 0),
        "L2_DIGITALLY_VERIFIED": level_c.get("L2_DIGITALLY_VERIFIED", 0),
    }


def build_end_goal_matrix(rows: list[dict[str, Any]]) -> dict[str, Any]:
    fam_data: dict[int, dict[str, Any]] = {
        f["id"]: {
            "id": f["id"],
            "key": f["key"],
            "name": f["name"],
            "requirement_count": 0,
            "owners": set(),
            "highest_level": "L0_DEFINED",
            "work_state_counts": Counter(),
        }
        for f in END_GOAL_FAMILIES
    }
    level_rank = {lvl: i for i, lvl in enumerate(sorted(CANONICAL_CURRENT_LEVELS))}
    for row in rows:
        for fid in row.get("end_goal_families") or []:
            f = fam_data[fid]
            f["requirement_count"] += 1
            f["owners"].add(row.get("owner_repo"))
            cl = row.get("current_level") or "L0_DEFINED"
            if level_rank.get(cl, 0) > level_rank.get(f["highest_level"], 0):
                f["highest_level"] = cl
            f["work_state_counts"][row.get("work_state")] += 1
    families = []
    for f in END_GOAL_FAMILIES:
        rec = fam_data[f["id"]]
        families.append(
            {
                "id": rec["id"],
                "key": rec["key"],
                "name": rec["name"],
                "requirement_count": rec["requirement_count"],
                "owners": sorted(rec["owners"]),
                "highest_level": rec["highest_level"],
                "work_state_counts": dict(rec["work_state_counts"]),
            }
        )
    return {"families": families, "family_count": len(families)}


def false_open_report(rows: list[dict[str, Any]], index: EvidenceIndex) -> dict[str, Any]:
    total = len(rows) or 1
    impl_open = sum(1 for r in rows if r["work_state"] == "DIGITAL_IMPLEMENTATION_OPEN")
    alarms: list[dict[str, Any]] = []

    if impl_open / total > 0.9:
        alarms.append(
            {
                "check": "false_open_rate",
                "severity": "CRITICAL",
                "detail": f"{impl_open}/{total} ({100*impl_open/total:.1f}%) classified DIGITAL_IMPLEMENTATION_OPEN",
            }
        )

    pending_classes = [
        "HUMAN_PENDING",
        "PHYSICAL_PENDING",
        "EXTERNAL_PENDING",
        "STANDARD_PENDING",
        "CERTIFICATION_PENDING",
        "CARRIER_PENDING",
        "VENDOR_PENDING",
        "OWNER_DECISION_PENDING",
    ]
    pending_total = sum(sum(1 for r in rows if r["work_state"] == p or p in (r.get("blocker_classes") or [])) for p in pending_classes)
    if pending_total == 0:
        alarms.append(
            {
                "check": "all_pending_zero",
                "severity": "CRITICAL",
                "detail": "All non-digital pending classes are zero — likely under-classification.",
            }
        )

    yaml_only_open = 0
    for r in rows:
        if r["work_state"] != "DIGITAL_IMPLEMENTATION_OPEN":
            continue
        passes = r.get("search_passes") or {}
        if not any(passes.get(k) for k in passes) and (r.get("yaml_implementation_state_hint") or "").upper() in (
            "NOT_STARTED",
            "DOCUMENTED_DESIGN",
        ):
            yaml_only_open += 1
    if yaml_only_open > impl_open * 0.5:
        alarms.append(
            {
                "check": "yaml_only_open",
                "severity": "HIGH",
                "detail": f"{yaml_only_open} rows open solely from stale yaml NOT_STARTED without search hits",
            }
        )

    impl_missing_proof = sum(
        1
        for r in rows
        if r["work_state"] == "DIGITAL_IMPLEMENTATION_OPEN" and r["implementation_state"] == "IMPLEMENTED"
    )
    if impl_missing_proof:
        alarms.append(
            {
                "check": "implemented_classified_open",
                "severity": "HIGH",
                "detail": f"{impl_missing_proof} IMPLEMENTED rows classified DIGITAL_IMPLEMENTATION_OPEN",
            }
        )

    search_miss_impl_open = sum(
        1
        for r in rows
        if r["work_state"] == "DIGITAL_IMPLEMENTATION_OPEN" and not any((r.get("search_passes") or {}).values())
    )
    if search_miss_impl_open:
        alarms.append(
            {
                "check": "search_miss_impl_open",
                "severity": "HIGH",
                "detail": f"{search_miss_impl_open} rows should be EVIDENCE_MAPPING_OPEN not DIGITAL_IMPLEMENTATION_OPEN",
            }
        )

    status = "PASS" if not alarms else "FAIL"
    return {
        "status": status,
        "alarms": alarms,
        "metrics": {
            "digital_implementation_open_rate": round(impl_open / total, 4),
            "yaml_only_open": yaml_only_open,
            "index_record_count": len(index.records),
            "index_requirement_ids": len(index.by_requirement_id),
        },
    }


def index_to_json(index: EvidenceIndex) -> dict[str, Any]:
    return {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.accepted_main_evidence_index",
        "repo_shas": index.repo_shas,
        "record_count": len(index.records),
        "records": [
            {
                "repo": r.repo,
                "accepted_main_sha": r.accepted_main_sha,
                "path": r.path,
                "artifact_type": r.artifact_type,
                "tokens_or_results": r.tokens_or_results,
                "requirement_ids": r.requirement_ids,
                "capabilities": r.capabilities,
                "verification_class": r.verification_class,
                "freshness": r.freshness,
            }
            for r in index.records
        ],
    }
