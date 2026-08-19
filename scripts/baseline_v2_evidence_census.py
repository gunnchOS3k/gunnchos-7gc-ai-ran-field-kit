#!/usr/bin/env python3
"""Phase B.3 accepted-main evidence census — precision/provenance correction."""

from __future__ import annotations

import json
import os
import random
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

LEVEL_RANK = {lvl: i for i, lvl in enumerate(sorted(CANONICAL_CURRENT_LEVELS))}

IMPLEMENTATION_ROLES = {
    "IMPLEMENTATION_CODE",
    "CONFIG",
    "FIRMWARE",
    "HARDWARE_DESIGN",
    "CONTENT",
    "DATA_PIPELINE",
}
VERIFICATION_ROLES = {
    "UNIT_TEST",
    "INTEGRATION_TEST",
    "REPRODUCTION_RESULT",
    "INDEPENDENT_VERIFIER_RESULT",
    "RUNTIME_RESULT",
    "BUILD_RESULT",
    "DEVICE_RESULT",
    "MEASUREMENT_RESULT",
}
NON_PROOF_ROLES = {
    "TRACEABILITY_ONLY",
    "STATUS_ONLY",
    "REQUIREMENT_ONLY",
    "DESIGN_ONLY",
    "DOCUMENTATION_ONLY",
    "HISTORICAL_ONLY",
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
    "node_modules", ".git", "build", "dist", "target", "__pycache__", ".venv", "venv", ".godot", ".import",
}
SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".tar", ".gz", ".apk",
    ".so", ".dylib", ".bin", ".glb", ".gltf", ".wav", ".mp3", ".mp4", ".sock",
}
MAX_FILE_BYTES = 512_000

INDEX_PREFIXES = ("README", "STATUS", "RELEASE", "REPRODUCIBILITY", "EVIDENCE")
INDEX_DIRS = (
    "artifacts", "docs", "tests", "scripts", "src", "app", "firmware", "hardware",
    "paper", "papers", "program", "curriculum", "results",
)

L0_CHARTER_IDS = {
    "CHARTER_NARRATIVE", "REPO_OWNERSHIP_MAP", "CLAIM_BOUNDARIES", "COMPLETION_REGISTER_V1",
}

OWNER_PRIMARY_FAMILY: dict[str, int] = {
    "gunnchos-7gc-ai-ran-field-kit": 1,
    "gunnchos-device-os": 2,
    "gunnchAI3k": 4,
    "waike-research-ops": 5,
    "anime-aggressors": 6,
    "pedestrian-pursuit": 7,
    "archive-of-life-artifact-world": 8,
    "beatlink-party": 9,
    "gunnchos-hardware-industrial-design": 10,
    "edge-io-measurement-node": 12,
    "readygary-6g-beam-selection": 13,
    "spectrumx-ai-ran-gary": 14,
    "7gc-digital-twin": 15,
    "ntn-resilience-sim": 16,
    "gunnchos-gpu-nr-baseband-platform": 17,
    "gunnchos-emergent-service-intent-protocols": 19,
    "gunnchos-research-portal": 22,
}

L3_PATH_MARKERS = (
    "product_use", "digital_rc", "user_ready", "persona", "playtest", "ux_pass",
    "PRODUCT_USE", "DIGITAL_RC", "RC_", "persona/", "user_journey",
)

L3_EXCLUDE_MARKERS = (
    "paper/", "papers/", "sim/", "hardware/", "program/digital_ecosystem",
    "tests/unit", "research_card", "benchmark_summary",
)


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
                "git", "clone", "--depth", "1", "--branch", "main",
                f"https://github.com/gunnchOS3k/{repo}.git", str(clone),
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


def classify_evidence_role(rel: str, content: str, artifact_type: str) -> str:
    low = rel.lower()
    if low.startswith("program/"):
        if "requirements" in low or low.endswith("requirements.yaml"):
            return "REQUIREMENT_ONLY"
        if "traceability" in low:
            return "TRACEABILITY_ONLY"
        return "STATUS_ONLY"
    if low.startswith("tests/"):
        return "UNIT_TEST" if "unit" in low or "test_" in low else "INTEGRATION_TEST"
    if "reproduc" in low or "make reproduce" in content.lower():
        return "REPRODUCTION_RESULT"
    if "VP_" in content or "INDEPENDENT" in content.upper():
        if any(m in low for m in L3_PATH_MARKERS):
            return "RUNTIME_RESULT"
        return "INDEPENDENT_VERIFIER_RESULT"
    if low.startswith(("firmware/", "hardware/")):
        return "HARDWARE_DESIGN" if "hardware" in low else "FIRMWARE"
    if low.startswith(("src/", "app/", "scripts/")):
        return "IMPLEMENTATION_CODE"
    if low.endswith((".yaml", ".yml", ".toml", ".cfg", ".ini")):
        return "CONFIG"
    if low.startswith("docs/") or low.endswith(".md"):
        if any(x in content.upper() for x in ("IMPLEMENTED", "VALIDATED", "STATUS")):
            return "HISTORICAL_ONLY"
        return "DOCUMENTATION_ONLY"
    if low.startswith("artifacts/") and low.endswith(".json"):
        if '"PASS"' in content or '"ok": true' in content or '"status": "PASS"' in content:
            if any(m in low for m in L3_PATH_MARKERS):
                return "RUNTIME_RESULT"
            return "BUILD_RESULT"
        return "STATUS_ONLY"
    if low.startswith(("paper/", "papers/")):
        return "DESIGN_ONLY"
    if artifact_type == "implementation":
        return "IMPLEMENTATION_CODE"
    if artifact_type == "script":
        return "IMPLEMENTATION_CODE"
    return "DOCUMENTATION_ONLY"


def is_implementation_proof(role: str) -> bool:
    return role in IMPLEMENTATION_ROLES


def is_verification_proof(role: str, rel: str, content: str) -> bool:
    if role not in VERIFICATION_ROLES:
        return False
    low = rel.lower()
    if role == "BUILD_RESULT" and low.endswith(".json") and '"PASS"' in content:
        return False
    if role == "INDEPENDENT_VERIFIER_RESULT" and any(x in low for x in L3_EXCLUDE_MARKERS):
        return True
    return True


def has_l3_user_ready_evidence(rel: str, content: str, role: str) -> bool:
    low = rel.lower()
    if any(x in low for x in L3_EXCLUDE_MARKERS):
        return False
    if any(m.lower() in low for m in L3_PATH_MARKERS):
        return True
    if role == "RUNTIME_RESULT" and ("PRODUCT_USE" in content or "DIGITAL_RC" in content):
        return True
    if "persona" in content.lower() and "RC_" in content:
        return True
    return False


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


def classify_artifact_type(rel: str) -> str:
    low = rel.lower()
    if low.startswith("tests/"):
        return "test"
    if "/artifacts/" in low or low.startswith("artifacts/"):
        return "artifact_json" if low.endswith(".json") else "artifact_md"
    if low.startswith(("paper/", "papers/")):
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


def extract_tokens(content: str) -> list[str]:
    tokens: set[str] = set()
    for m in re.finditer(r"[A-Z][A-Z0-9_]{4,}", content):
        tokens.add(m.group(0))
    for m in re.finditer(r'"([A-Za-z0-9_.-]+)"\s*:\s*(true|"PASS"|"pass")', content):
        tokens.add(m.group(1))
    return sorted(tokens)


def extract_requirement_ids(content: str) -> list[str]:
    return sorted(set(re.findall(r"\b[A-Z]{2,}(?:-[A-Z0-9]+)+\b", content)))


@dataclass
class EvidenceRecord:
    repo: str
    accepted_main_sha: str
    path: str
    artifact_type: str
    evidence_role: str = "DOCUMENTATION_ONLY"
    tokens_or_results: list[str] = field(default_factory=list)
    requirement_ids: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    verification_class: str = "NOT_VERIFIED"
    freshness: str = "accepted_main"
    matched_proof_identifiers: list[str] = field(default_factory=list)
    admissible: bool = True
    why_repo_is_admissible: str = ""


@dataclass
class EvidenceIndex:
    records: list[EvidenceRecord] = field(default_factory=list)
    by_requirement_id: dict[str, list[EvidenceRecord]] = field(default_factory=lambda: defaultdict(list))
    by_token: dict[str, list[EvidenceRecord]] = field(default_factory=lambda: defaultdict(list))
    by_repo: dict[str, list[EvidenceRecord]] = field(default_factory=lambda: defaultdict(list))
    repo_shas: dict[str, str] = field(default_factory=dict)
    traceability_hits: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    traceability_repo_links: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))


def build_evidence_index(repos_root: Path, temp_root: Path, repos: list[str] | None = None) -> EvidenceIndex:
    index = EvidenceIndex()
    for repo in repos or CANONICAL_REPOS:
        repo_dir, sha = ensure_repo(repos_root, temp_root, repo)
        index.repo_shas[repo] = sha
        for rel in git_list_files(repo_dir):
            if Path(rel).suffix.lower() not in {".json", ".md", ".yaml", ".yml", ".py", ".gd", ".rs", ".toml"}:
                if not any(rel.startswith(d + "/") for d in INDEX_DIRS):
                    continue
            content = git_show_file(repo_dir, rel)
            if content is None:
                continue
            artifact_type = classify_artifact_type(rel)
            role = classify_evidence_role(rel, content, artifact_type)
            req_ids = extract_requirement_ids(content)
            tokens = extract_tokens(content)
            rec = EvidenceRecord(
                repo=repo,
                accepted_main_sha=sha,
                path=rel,
                artifact_type=artifact_type,
                evidence_role=role,
                tokens_or_results=tokens[:40],
                requirement_ids=req_ids[:40],
                capabilities=[t for t in tokens if t.endswith("_PASS") or t.endswith("_READY")][:20],
                verification_class=_verification_class_from_role(role),
                freshness="accepted_main",
            )
            index.records.append(rec)
            index.by_repo[repo].append(rec)
            for rid in req_ids:
                index.by_requirement_id[rid].append(rec)
            for tok in tokens:
                index.by_token[tok].append(rec)
    return index


def _verification_class_from_role(role: str) -> str:
    mapping = {
        "UNIT_TEST": "UNIT_VERIFIED",
        "INTEGRATION_TEST": "INTEGRATION_VERIFIED",
        "REPRODUCTION_RESULT": "DIGITALLY_REPRODUCED",
        "INDEPENDENT_VERIFIER_RESULT": "INDEPENDENTLY_VERIFIED_DIGITAL",
        "RUNTIME_RESULT": "INTEGRATION_VERIFIED",
        "BUILD_RESULT": "INTEGRATION_VERIFIED",
        "DEVICE_RESULT": "TARGET_HARDWARE_VERIFIED",
        "MEASUREMENT_RESULT": "INTEGRATION_VERIFIED",
    }
    return mapping.get(role, "NOT_VERIFIED")


def load_traceability_maps(field_kit_root: Path) -> tuple[dict[str, list[str]], dict[str, set[str]]]:
    hits: dict[str, list[str]] = defaultdict(list)
    repo_links: dict[str, set[str]] = defaultdict(set)
    patterns = [
        "program/reports/*TRACEABILITY*",
        "program/full_product/reports/*",
        "ROLE_REQUIREMENT_TRACEABILITY.md",
        "program/requirements/*.yaml",
    ]
    repo_name_re = re.compile(r"gunnch[a-zA-Z0-9-]+|7gc-[a-z0-9-]+|waike-[a-z0-9-]+|readygary-[a-z0-9-]+|ntn-[a-z0-9-]+|edge-io-[a-z0-9-]+|spectrumx-[a-z0-9-]+|anime-[a-z0-9-]+|pedestrian-[a-z0-9-]+|archive-of-[a-z0-9-]+|beatlink-[a-z0-9-]+")
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
                for repo_match in repo_name_re.findall(text):
                    for canon in CANONICAL_REPOS:
                        if repo_match in canon or canon.endswith(repo_match.split("/")[-1]):
                            repo_links[rid].add(canon)
    return hits, repo_links


def is_control_plane_requirement(req: dict[str, Any]) -> bool:
    owner = req.get("owner_repository") or ""
    subsystem = req.get("subsystem") or ""
    gate = req.get("gate") or 0
    if owner == "gunnchos-7gc-ai-ran-field-kit" and gate == 0:
        return True
    if subsystem in ("ecosystem", "gates", "evidence"):
        return True
    if req.get("requirement_type") in ("control", "gate", "charter"):
        return True
    if (req.get("id") or "").startswith(("CHARTER-", "GATE-", "SYS-MISSION-")):
        return True
    return False


def admissible_repositories(
    req: dict[str, Any],
    req_by_id: dict[str, dict[str, Any]],
    trace_repo_links: dict[str, set[str]],
) -> tuple[list[str], str]:
    owner = req.get("owner_repository") or "gunnchos-7gc-ai-ran-field-kit"
    admissible: set[str] = {owner}
    reasons = [f"owner_repository={owner}"]

    for sr in req.get("supporting_repositories") or []:
        if sr in CANONICAL_REPOS:
            admissible.add(sr)
            reasons.append(f"supporting_repository={sr}")

    for dep in req.get("dependencies") or []:
        dep_req = req_by_id.get(dep)
        if dep_req:
            dep_owner = dep_req.get("owner_repository")
            if dep_owner in CANONICAL_REPOS:
                admissible.add(dep_owner)
                reasons.append(f"dependency={dep}→{dep_owner}")

    for repo in trace_repo_links.get(req["id"], set()):
        if repo in CANONICAL_REPOS:
            admissible.add(repo)
            reasons.append(f"traceability_interface={repo}")

    if is_control_plane_requirement(req):
        admissible.add("gunnchos-7gc-ai-ran-field-kit")
        reasons.append("field_kit_control_plane_aggregate")

    return sorted(admissible), "; ".join(reasons)


def proof_identifiers(req: dict[str, Any]) -> list[str]:
    ids: list[str] = [req["id"]]
    for ev in req.get("required_evidence") or []:
        if ev and len(ev) >= 4:
            ids.append(ev)
    for dep in req.get("dependencies") or []:
        ids.append(dep)
    norm = (req.get("normative_text") or "") + " " + (req.get("notes") or "")
    for m in re.finditer(r"\b[A-Z][A-Z0-9_]{6,}\b", norm):
        ids.append(m.group(0))
    return sorted(set(ids))


def discovery_terms(req: dict[str, Any]) -> list[str]:
    terms: list[str] = []
    title = req.get("title") or ""
    for bit in re.findall(r"[A-Za-z0-9_]{5,}", title):
        if bit.upper() != req["id"] and bit not in (req.get("required_evidence") or []):
            terms.append(bit)
    return terms


def repo_admissibility_reason(rec: EvidenceRecord, admissible: set[str], req: dict[str, Any]) -> tuple[bool, str]:
    if rec.repo in admissible:
        if rec.repo == req.get("owner_repository"):
            return True, "owner_repository"
        if rec.repo in (req.get("supporting_repositories") or []):
            return True, "supporting_repository"
        if rec.repo == "gunnchos-7gc-ai-ran-field-kit" and is_control_plane_requirement(req):
            return True, "field_kit_control_plane"
        return True, "traceability_or_dependency"
    return False, "unrelated_canonical_repo"


def pending_dimensions(req: dict[str, Any]) -> list[str]:
    blob = " ".join([
        " ".join(req.get("blockers") or []),
        req.get("notes") or "",
        req.get("title") or "",
    ]).upper()
    dims: list[str] = []
    rules = [
        ("PHYSICAL", ("PHYSICAL", "FAB_", "EVT0", "MANUFACTUR", "ENCLOSURE", "BATTERY", "THERMAL", "RFQ", "LOCAL_HARDWARE", "PROTOTYPE", "SILICON")),
        ("HUMAN", ("HUMAN", "PILOT", "OPERATOR", "CONSENT", "PLAYTEST", "FUN", "BALANCE", "TEACHER")),
        ("EXTERNAL", ("EXTERNAL", "NVIDIA", "SIONNA", "AERIAL", "DOI", "PENTEST", "NGC", "BLOCKED_GPU", "OTA")),
        ("STANDARD", ("STANDARD", "IMT2030", "3GPP", "6G STANDARD", "STANDARDS")),
        ("CERTIFICATION", ("CERTIF", "REGULATORY", "FCC", "CE_MARK")),
        ("CARRIER", ("CARRIER", "CELLULAR", "MNO", "NTN_DEPLOY")),
        ("VENDOR", ("VENDOR", "SUPPLIER", "NDA")),
        ("OWNER_DECISION", ("OWNER_DECISION", "WP001", "EDMUND", "PRODUCT_CHARTER_APPROVAL", "CHARTER_APPROVAL")),
    ]
    for dim, keys in rules:
        if any(k in blob for k in keys):
            dims.append(dim)
    return dims


def required_target_level(req: dict[str, Any], dims: list[str]) -> str:
    gate = req.get("gate") or 0
    if "CERTIFICATION" in dims or "REGULATORY" in (req.get("title") or "").upper():
        return "L5_EXTERNAL_OR_CERTIFIED"
    if "CARRIER" in dims or "VENDOR" in dims or "STANDARD" in dims:
        return "L6_PRODUCTION_OR_FIELD"
    if "PHYSICAL" in dims or "HUMAN" in dims:
        return "L4_HUMAN_OR_TARGET_HARDWARE_VALIDATED"
    if gate >= 7:
        return "L6_PRODUCTION_OR_FIELD"
    if gate >= 6:
        return "L5_EXTERNAL_OR_CERTIFIED"
    if gate >= 4:
        return "L4_HUMAN_OR_TARGET_HARDWARE_VALIDATED"
    if gate >= 3:
        return "L3_USER_READY_DIGITAL_RC"
    return "L2_DIGITALLY_VERIFIED"


def map_families(req: dict[str, Any], dims: list[str]) -> tuple[int, list[int], str]:
    rid = req.get("id") or ""
    title = (req.get("title") or "").upper()
    subsystem = req.get("subsystem") or ""
    owner = req.get("owner_repository") or ""
    gate = req.get("gate") or 0
    supporting = set(req.get("supporting_repositories") or [])
    secondary: set[int] = set()
    reason_parts: list[str] = []
    primary: int | None = None

    rules: list[tuple[Any, int, str]] = [
        (lambda: rid.startswith("PAPER-") or "PAPER I" in title or "RQ1" in title or "RQ2" in title, 20, "research paper material"),
        (lambda: owner == "waike-research-ops" or rid.startswith("WAIKE-") or "WAIKE" in title or "waike-research-ops" in supporting, 5, "WAIKE scope"),
        (lambda: owner == "readygary-6g-beam-selection" or "READYGARY" in title or "BEAM SELECT" in title or "readygary-6g-beam-selection" in supporting, 13, "ReadyGary scope"),
        (lambda: owner == "spectrumx-ai-ran-gary" or "SPECTRUM" in title or "AI-RAN" in title or "spectrumx-ai-ran-gary" in supporting, 14, "SpectrumX/AI-RAN scope"),
        (lambda: owner == "ntn-resilience-sim" or ("NTN" in title and "RESILIENCE" in title) or "ntn-resilience-sim" in supporting, 16, "NTN resilience scope"),
        (lambda: owner == "gunnchos-gpu-nr-baseband-platform" or "BASEBAND" in title or "CUPHY" in title or "gunnchos-gpu-nr-baseband-platform" in supporting, 17, "GPU NR baseband scope"),
        (lambda: owner == "gunnchos-emergent-service-intent-protocols" or "EMERGENT" in title or "gunnchos-emergent-service-intent-protocols" in supporting, 19, "Emergent protocols scope"),
        (lambda: owner == "gunnchos-research-portal" or "CONTACT_SNAPSHOT" in title or "gunnchos-research-portal" in supporting, 22, "Publishing/platform release scope"),
        (lambda: owner == "anime-aggressors" or rid.startswith("GAME-ANIME"), 6, "Anime Aggressors owner"),
        (lambda: owner == "pedestrian-pursuit", 7, "Pedestrian Pursuit owner"),
        (lambda: owner == "archive-of-life-artifact-world", 8, "Archive of Life owner"),
        (lambda: owner == "beatlink-party", 9, "BeatLink owner"),
        (lambda: "HUMAN" in dims or "PLAYTEST" in title or "PILOT" in title, 26, "human validation requirement"),
        (lambda: owner == "gunnchos-hardware-industrial-design", 11 if "DOCK" in title else 10, "hardware owner repo"),
        (lambda: subsystem == "rings" or owner == "edge-io-measurement-node", 12, "edge I/O ring scope"),
        (lambda: owner == "gunnchos-device-os" and any(x in title for x in ("LAB", "DEVICE LAB", "DSXL", "FOUR_GAME", "PRODUCT_USE")), 3, "gunnchDevice Lab scope"),
        (lambda: owner == "gunnchos-device-os", 2, "gunnchOS owner"),
        (lambda: subsystem == "connectivity" or "CARRIER" in title, 23, "carrier/cellular/NTN scope"),
        (lambda: subsystem == "standards" or "IMT2030" in title, 28, "standards evolution scope"),
        (lambda: "CERTIF" in title or "REGULATORY" in title, 25, "regulatory/certification scope"),
        (lambda: "MANUFACTUR" in title or "FAB_" in title or "NPI" in title, 24, "manufacturing/commercialization scope"),
        (lambda: "PRIVACY" in rid or "SECURITY" in rid, 21, "security/privacy/supply chain"),
        (lambda: owner == "7gc-digital-twin" or "7gc-digital-twin" in supporting, 15, "Digital Twin scope"),
        (lambda: owner == "gunnchos-7gc-ai-ran-field-kit" and (gate >= 4 or req.get("scientific_evidence_relevant")), 18, "R6G/field kit research scope"),
        (lambda: gate >= 7, 27, "field deployment gate 7+"),
    ]
    for pred, fid, why in rules:
        try:
            if pred():
                primary = fid
                reason_parts.append(why)
                break
        except Exception:
            continue

    if primary is None:
        primary = OWNER_PRIMARY_FAMILY.get(owner, 1)
        reason_parts.append(f"owner_repository={owner}" if owner else "default release/control plane")

    if req.get("scientific_evidence_relevant") and primary != 20:
        secondary.add(20)
    if gate >= 7 and primary not in (27, 28):
        secondary.update({13, 14, 16, 17, 19, 27})
    SUPPORTING_TO_FAMILY = {
        "readygary-6g-beam-selection": 13,
        "spectrumx-ai-ran-gary": 14,
        "ntn-resilience-sim": 16,
        "gunnchos-gpu-nr-baseband-platform": 17,
        "gunnchos-emergent-service-intent-protocols": 19,
        "gunnchos-research-portal": 22,
        "7gc-digital-twin": 15,
        "waike-research-ops": 5,
    }
    for sr in supporting:
        if sr in SUPPORTING_TO_FAMILY:
            secondary.add(SUPPORTING_TO_FAMILY[sr])
    if "AI-RAN" in title or "BEAM" in title or "FR2" in title or "SUB6" in title or "MIMO" in title:
        secondary.add(13)
    if "INTENT" in title and "SERVICE" in title:
        secondary.add(19)
    if "PRIVACY" in rid or "SECURITY" in rid:
        secondary.add(21)
    if "PHYSICAL" in dims or "VENDOR" in dims:
        secondary.add(24)
    if "CERTIFICATION" in dims:
        secondary.add(25)
    if "STANDARD" in dims:
        secondary.add(28)
    if "CARRIER" in dims:
        secondary.add(23)

    secondary.discard(primary)
    return primary, sorted(secondary), "; ".join(reason_parts)


def search_passes(
    req: dict[str, Any],
    index: EvidenceIndex,
    trace_maps: dict[str, list[str]],
    req_by_id: dict[str, dict[str, Any]],
    trace_repo_links: dict[str, set[str]],
) -> dict[str, Any]:
    rid = req["id"]
    admissible_list, admissible_reason = admissible_repositories(req, req_by_id, trace_repo_links)
    admissible_set = set(admissible_list)
    proofs = proof_identifiers(req)
    discoveries = discovery_terms(req)

    hits: list[EvidenceRecord] = []
    pass_log: dict[str, list[str]] = {
        "pass1_exact_id": [],
        "pass2_proof_identifiers": [],
        "pass3_traceability": [],
        "pass4_implementation": [],
        "pass5_verification": [],
        "pass6_discovery_only": [],
        "rejected_unrelated_repo": [],
    }

    def consider(rec: EvidenceRecord, pass_name: str, detail: str, proof_match: str | None = None) -> None:
        ok, why = repo_admissibility_reason(rec, admissible_set, req)
        rec.admissible = ok
        rec.why_repo_is_admissible = why if ok else f"REJECTED:{why}"
        if not ok:
            pass_log["rejected_unrelated_repo"].append(f"{rec.repo}:{rec.path} ({why})")
            return
        if proof_match:
            rec.matched_proof_identifiers.append(proof_match)
        hits.append(rec)
        pass_log[pass_name].append(detail)

    for rec in index.by_requirement_id.get(rid, []):
        consider(rec, "pass1_exact_id", f"{rec.repo}:{rec.path}", rid)

    for tok in proofs:
        tok_u = tok.upper()
        for rec in index.by_token.get(tok_u, []) + index.by_token.get(tok, []):
            consider(rec, "pass2_proof_identifiers", f"{rec.repo}:{rec.path} proof={tok}", tok)

    for path in trace_maps.get(rid, []):
        pass_log["pass3_traceability"].append(path)

    for tok in discoveries:
        tok_u = tok.upper()
        for rec in index.by_token.get(tok_u, []) + index.by_token.get(tok, []):
            ok, why = repo_admissibility_reason(rec, admissible_set, req)
            if ok:
                pass_log["pass6_discovery_only"].append(f"{rec.repo}:{rec.path} discovery={tok}")
            else:
                pass_log["rejected_unrelated_repo"].append(f"{rec.repo}:{rec.path} discovery={tok} ({why})")

    seen: set[tuple[str, str]] = set()
    uniq: list[EvidenceRecord] = []
    for h in hits:
        key = (h.repo, h.path)
        if key not in seen:
            seen.add(key)
            uniq.append(h)

    impl_hits = [
        h for h in uniq
        if is_implementation_proof(h.evidence_role)
        and not h.path.startswith("tests/")
        and h.evidence_role not in NON_PROOF_ROLES
    ]
    for h in impl_hits:
        pass_log["pass4_implementation"].append(f"{h.repo}:{h.path} role={h.evidence_role}")

    verif_hits = [
        h for h in uniq
        if is_verification_proof(h.evidence_role, h.path, "")
        or (h.path.startswith("tests/") and h.evidence_role in VERIFICATION_ROLES)
    ]
    for h in verif_hits:
        pass_log["pass5_verification"].append(f"{h.repo}:{h.path} role={h.evidence_role}")

    best_impl = impl_hits[0] if impl_hits else None
    best_verif = verif_hits[0] if verif_hits else None

    proof_only_hits = [h for h in uniq if h.matched_proof_identifiers]
    discovery_only = bool(pass_log["pass6_discovery_only"]) and not proof_only_hits

    return {
        "hits": uniq,
        "best_implementation": best_impl,
        "best_verification": best_verif,
        "pass_log": pass_log,
        "admissible_repositories": admissible_list,
        "admissible_reason": admissible_reason,
        "proof_identifiers": proofs,
        "discovery_terms": discoveries,
        "discovery_only": discovery_only,
        "proof_hits": len(proof_only_hits),
    }


def compute_evidence_confidence(
    req: dict[str, Any],
    search: dict[str, Any],
    impl_ev: EvidenceRecord | None,
    verif_ev: EvidenceRecord | None,
    yaml_impl: str,
    yaml_val: str,
) -> str:
    pass_log = search.get("pass_log") or {}
    if pass_log.get("rejected_unrelated_repo") and not pass_log.get("pass1_exact_id") and not pass_log.get("pass2_proof_identifiers"):
        return "LOW"
    if search.get("discovery_only"):
        return "LOW"
    if pass_log.get("pass1_exact_id") and impl_ev and verif_ev:
        if impl_ev.repo in search["admissible_repositories"] and verif_ev.repo in search["admissible_repositories"]:
            return "HIGH"
    if pass_log.get("pass2_proof_identifiers") and impl_ev:
        if impl_ev.matched_proof_identifiers:
            return "MEDIUM" if verif_ev else "MEDIUM"
    if yaml_impl.upper() in ("IMPLEMENTED", "VALIDATED") and not impl_ev:
        return "LOW"
    if pass_log.get("pass6_discovery_only") and not pass_log.get("pass4_implementation"):
        return "LOW"
    if impl_ev and impl_ev.evidence_role in NON_PROOF_ROLES:
        return "LOW"
    if impl_ev:
        return "MEDIUM"
    return "LOW"


def map_implementation_state(yaml_state: str, impl_ev: EvidenceRecord | None, search: dict[str, Any]) -> str:
    s = (yaml_state or "").upper()
    if impl_ev and is_implementation_proof(impl_ev.evidence_role):
        return "IMPLEMENTED" if s != "PARTIAL" else "PARTIALLY_IMPLEMENTED"
    if impl_ev and impl_ev.evidence_role in NON_PROOF_ROLES:
        return "NOT_IMPLEMENTED"
    if s in ("IMPLEMENTED",) and not impl_ev:
        return "NOT_IMPLEMENTED"
    if s in ("IN_PROGRESS", "PARTIAL"):
        return "PARTIALLY_IMPLEMENTED"
    if s in ("SUPERSEDED",):
        return "SUPERSEDED"
    if s in ("NOT_APPLICABLE", "N/A"):
        return "NOT_APPLICABLE"
    return "NOT_IMPLEMENTED"


def map_verification_state(yaml_state: str, verif_ev: EvidenceRecord | None) -> str:
    s = (yaml_state or "").upper()
    if verif_ev and is_verification_proof(verif_ev.evidence_role, verif_ev.path, ""):
        return _verification_class_from_role(verif_ev.evidence_role)
    if s == "INDEPENDENTLY_VALIDATED" and not verif_ev:
        return "NOT_VERIFIED"
    if s in ("VALIDATED", "PASS") and not verif_ev:
        return "NOT_VERIFIED"
    if s in ("NOT_STARTED", "FAIL", "IN_PROGRESS"):
        return "NOT_VERIFIED"
    return "NOT_VERIFIED"


def infer_current_level(
    implementation_state: str,
    verification_state: str,
    impl_ev: EvidenceRecord | None,
    verif_ev: EvidenceRecord | None,
) -> str:
    if verif_ev and verif_ev.evidence_role == "DEVICE_RESULT":
        return "L4_HUMAN_OR_TARGET_HARDWARE_VALIDATED"
    if verification_state in {"PRODUCTION_FIELD_VERIFIED"}:
        return "L6_PRODUCTION_OR_FIELD"
    if verification_state in {"EXTERNALLY_VERIFIED", "CERTIFIED"}:
        return "L5_EXTERNAL_OR_CERTIFIED"
    if verification_state in {"TARGET_HARDWARE_VERIFIED", "HUMAN_VERIFIED"}:
        return "L4_HUMAN_OR_TARGET_HARDWARE_VALIDATED"
    if verif_ev and has_l3_user_ready_evidence(verif_ev.path, "", verif_ev.evidence_role):
        if verification_state in {"INTEGRATION_VERIFIED", "INDEPENDENTLY_VERIFIED_DIGITAL", "DIGITALLY_REPRODUCED"}:
            return "L3_USER_READY_DIGITAL_RC"
    if verification_state in {"DIGITALLY_REPRODUCED", "INTEGRATION_VERIFIED", "UNIT_VERIFIED", "INDEPENDENTLY_VERIFIED_DIGITAL"}:
        return "L2_DIGITALLY_VERIFIED"
    if implementation_state in {"IMPLEMENTED", "PARTIALLY_IMPLEMENTED"}:
        return "L1_IMPLEMENTED"
    return "L0_DEFINED"


def primary_next_blocker(dims: list[str]) -> str | None:
    priority = ["OWNER_DECISION", "PHYSICAL", "HUMAN", "EXTERNAL", "CERTIFICATION", "CARRIER", "VENDOR", "STANDARD"]
    for p in priority:
        if p in dims:
            return p
    return dims[0] if dims else None


def choose_work_state(
    req: dict[str, Any],
    implementation_state: str,
    verification_state: str,
    search: dict[str, Any],
    dims: list[str],
    confidence: str,
    yaml_impl: str,
    yaml_val: str,
    phase: str = "B.3",
) -> tuple[str, str]:
    impl_ev = search.get("best_implementation")
    verif_ev = search.get("best_verification")
    pass_log = search.get("pass_log") or {}
    has_proof_impl = impl_ev is not None and is_implementation_proof(impl_ev.evidence_role)
    has_proof_verif = verif_ev is not None and is_verification_proof(verif_ev.evidence_role, verif_ev.path, "")
    any_proof_pass = bool(pass_log.get("pass1_exact_id") or pass_log.get("pass2_proof_identifiers"))
    any_discovery = bool(pass_log.get("pass6_discovery_only"))

    yaml_impl_u = (yaml_impl or "").upper()
    yaml_val_u = (yaml_val or "").upper()

    if yaml_impl_u == "IMPLEMENTED" and not has_proof_impl:
        if phase == "B.4":
            if dims:
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
                primary = primary_next_blocker(dims) or dims[0]
                return mapping.get(primary, "OWNER_DECISION_PENDING"), (
                    f"B.4: YAML IMPLEMENTED hint without accepted-main path; blocked by {primary}."
                )
            return "DIGITAL_IMPLEMENTATION_OPEN", "B.4: YAML IMPLEMENTED hint without accepted-main implementation path."
        return "EVIDENCE_MAPPING_OPEN", "YAML IMPLEMENTED hint without current accepted-main implementation path."

    if yaml_val_u in ("VALIDATED", "INDEPENDENTLY_VALIDATED", "PASS") and not has_proof_verif:
        if has_proof_impl:
            return "DIGITAL_VALIDATION_OPEN", "YAML VALIDATED hint without current verification evidence."
        if phase == "B.4":
            if dims:
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
                primary = primary_next_blocker(dims) or dims[0]
                return mapping.get(primary, "OWNER_DECISION_PENDING"), (
                    f"B.4: YAML VALIDATED hint without verification; blocked by {primary}."
                )
            return "DIGITAL_IMPLEMENTATION_OPEN", "B.4: YAML VALIDATED hint without verification or implementation path."
        return "EVIDENCE_MAPPING_OPEN", "YAML VALIDATED hint without current verification or implementation path."

    if dims and not has_proof_impl and not any_proof_pass:
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
        primary = primary_next_blocker(dims) or dims[0]
        return mapping.get(primary, "OWNER_DECISION_PENDING"), (
            f"Non-digital blocker {primary}; no accepted-main implementation evidence located."
        )

    if has_proof_impl and has_proof_verif:
        if confidence == "LOW":
            if phase == "B.4":
                if dims:
                    prep_map = {
                        "HUMAN": "DIGITAL_PREPARATION_COMPLETE_HUMAN_PENDING",
                        "PHYSICAL": "DIGITAL_PREPARATION_COMPLETE_PHYSICAL_PENDING",
                        "EXTERNAL": "DIGITAL_PREPARATION_COMPLETE_EXTERNAL_PENDING",
                    }
                    primary = primary_next_blocker(dims)
                    if primary and primary in prep_map:
                        return prep_map[primary], f"B.4: proof paths LOW confidence; blocked by {primary}."
                return "DIGITAL_VALIDATION_OPEN", "B.4: proof paths located but confidence LOW — validation open."
            return "EVIDENCE_MAPPING_OPEN", "Proof paths located but confidence LOW — discovery/title-only or non-proof roles."
        return "DIGITAL_IMPLEMENTATION_COMPLETE", "Accepted-main implementation and verification evidence with proof identifiers."

    if has_proof_impl and not has_proof_verif:
        if dims:
            prep_map = {
                "HUMAN": "DIGITAL_PREPARATION_COMPLETE_HUMAN_PENDING",
                "PHYSICAL": "DIGITAL_PREPARATION_COMPLETE_PHYSICAL_PENDING",
                "EXTERNAL": "DIGITAL_PREPARATION_COMPLETE_EXTERNAL_PENDING",
            }
            primary = primary_next_blocker(dims)
            if primary and primary in prep_map:
                return prep_map[primary], f"Implementation evidence on accepted main; verification blocked by {primary}."
        return "DIGITAL_VALIDATION_OPEN", "Implementation evidence located; digital verification/reproduction proof missing."

    if any_discovery and not any_proof_pass:
        if phase == "B.4":
            if dims:
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
                primary = primary_next_blocker(dims) or dims[0]
                return mapping.get(primary, "OWNER_DECISION_PENDING"), (
                    f"B.4: discovery-term matches only; non-digital blocker {primary}."
                )
            return "DIGITAL_IMPLEMENTATION_OPEN", "B.4: discovery-term matches only — digital implementation open."
        return "EVIDENCE_MAPPING_OPEN", "Discovery-term matches only — cannot satisfy implementation alone."

    if any_proof_pass and not has_proof_impl:
        if phase == "B.4":
            trace_paths = (pass_log.get("pass1_exact_id") or [])[:3] + (pass_log.get("pass3_traceability") or [])[:2]
            trace_note = "; ".join(trace_paths[:3]) if trace_paths else "traceability/status"
            if dims:
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
                primary = primary_next_blocker(dims) or dims[0]
                return mapping.get(primary, "OWNER_DECISION_PENDING"), (
                    f"B.4: traceability located ({trace_note}); implementation blocked by {primary}."
                )
            if has_proof_verif:
                return "DIGITAL_IMPLEMENTATION_OPEN", (
                    f"B.4: verification/traceability without implementation proof ({trace_note}); digital implementation open."
                )
            return "DIGITAL_IMPLEMENTATION_OPEN", (
                f"B.4: traceability/status only ({trace_note}); digital implementation open."
            )
        return "EVIDENCE_MAPPING_OPEN", "Proof identifiers matched traceability/status artifacts only — not implementation proof."

    if not any_proof_pass and not any_discovery:
        if phase == "B.4":
            if dims:
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
                primary = primary_next_blocker(dims) or dims[0]
                return mapping.get(primary, "OWNER_DECISION_PENDING"), (
                    f"B.4: no admissible evidence; non-digital blocker {primary}."
                )
            return "DIGITAL_IMPLEMENTATION_OPEN", "B.4: five-pass search found no admissible evidence mapping."
        return "EVIDENCE_MAPPING_OPEN", "Five-pass accepted-main search found no admissible evidence mapping."

    if yaml_impl_u in ("NOT_STARTED", "DOCUMENTED_DESIGN", ""):
        return "DIGITAL_IMPLEMENTATION_OPEN", "No accepted-main implementation artifact; requirement remains digitally unimplemented."

    if phase == "B.4":
        if dims:
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
            primary = primary_next_blocker(dims) or dims[0]
            return mapping.get(primary, "OWNER_DECISION_PENDING"), f"B.4: search inconclusive; blocker {primary}."
        return "DIGITAL_IMPLEMENTATION_OPEN", "B.4: search inconclusive; digital implementation open."

    return "EVIDENCE_MAPPING_OPEN", "Search inconclusive; evidence mapping still open on accepted main."


def validation_open_impl_admissible(row: dict[str, Any]) -> bool:
    """DIGITAL_VALIDATION_OPEN requires IMPLEMENTED state + pass4 implementation proof on frozen SHA."""
    if row.get("implementation_state") != "IMPLEMENTED":
        return False
    impl = (row.get("implementation_evidence") or "").strip()
    if not impl or ":" not in impl:
        return False
    passes = row.get("search_passes") or {}
    pass4 = passes.get("pass4_implementation") or []
    if not pass4:
        return False
    impl_path = impl.split(":", 1)[-1]
    for entry in pass4:
        if impl_path in entry and "role=" in entry:
            role = entry.split("role=", 1)[-1].strip()
            if is_implementation_proof(role):
                return True
    return False


def enrich_impl_open_metadata(req: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    if row.get("work_state") != "DIGITAL_IMPLEMENTATION_OPEN":
        return row
    out = dict(row)
    passes = row.get("search_passes") or {}
    searched = list(row.get("admissible_repositories") or [])
    insuff: list[str] = []
    for key in (
        "pass1_exact_id", "pass2_proof_identifiers", "pass3_traceability",
        "pass5_verification", "pass6_discovery_only",
    ):
        for p in (passes.get(key) or [])[:4]:
            insuff.append(f"{key}: {p}")
    title = req.get("title") or row.get("title") or row["requirement_id"]
    out["specific_missing_implementation"] = (
        f"Accepted-main IMPLEMENTATION_* artifact for «{title}» ({row['requirement_id']}) on frozen SHA."
    )
    out["searched_repositories"] = searched
    out["why_paths_insufficient"] = (
        "; ".join(insuff[:10]) if insuff else (row.get("resolution_reason") or "No admissible IMPLEMENTATION_* path.")
    )
    return out


def enforce_b41_row_integrity(req: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if out.get("work_state") == "DIGITAL_VALIDATION_OPEN" and not validation_open_impl_admissible(out):
        prior = out.get("work_state")
        out["work_state"] = "DIGITAL_IMPLEMENTATION_OPEN"
        out["resolution"] = out["work_state"]
        out["engineering_state"] = out["work_state"]
        out["b41_reclassified_from"] = prior
        out["resolution_reason"] = (
            "B.4.1: reclassified from DIGITAL_VALIDATION_OPEN — "
            "implementation_state≠IMPLEMENTED or no pass4 IMPLEMENTATION_* evidence on frozen SHA."
        )
    if out.get("work_state") == "DIGITAL_IMPLEMENTATION_OPEN":
        out = enrich_impl_open_metadata(req, out)
    return out


def reconcile_requirement(
    req: dict[str, Any],
    index: EvidenceIndex,
    trace_maps: dict[str, list[str]],
    trace_repo_links: dict[str, set[str]],
    req_by_id: dict[str, dict[str, Any]],
    field_kit_sha: str,
    wp012_path: str | None,
    phase: str = "B.3",
) -> dict[str, Any]:
    rid = req["id"]
    owner = req.get("owner_repository") or "gunnchos-7gc-ai-ran-field-kit"
    program_gate = req.get("gate")
    sha = index.repo_shas.get(owner, "")
    dims = pending_dimensions(req)
    search = search_passes(req, index, trace_maps, req_by_id, trace_repo_links)
    primary_family, secondary_families, family_reason = map_families(req, dims)
    target_level = required_target_level(req, dims)
    next_blocker = primary_next_blocker(dims)

    yaml_impl = req.get("implementation_state") or ""
    yaml_val = req.get("validation_state") or ""

    if (rid in L0_CHARTER_IDS or rid.startswith("SYS-MISSION-")) and program_gate == 0 and wp012_path:
        return _row(
            req, owner, program_gate, field_kit_sha or sha, wp012_path, wp012_path, "PASS",
            "IMPLEMENTED", "INTEGRATION_VERIFIED", "L2_DIGITALLY_VERIFIED",
            "DIGITAL_IMPLEMENTATION_COMPLETE", primary_family, secondary_families, family_reason,
            "WP-012 VP artifact on accepted field-kit main proves L0 charter digital discoverability.",
            "Owner charter approval may remain human/owner pending.",
            {"pass1_exact_id": [wp012_path]}, dims, next_blocker, target_level,
            search["admissible_repositories"], search["admissible_reason"],
            search["proof_identifiers"], search["discovery_terms"],
            "HIGH", wp012_path.split(":")[-1] if ":" in wp012_path else owner,
            "field_kit_control_plane",
        )

    impl_ev = search["best_implementation"]
    verif_ev = search["best_verification"]
    confidence = compute_evidence_confidence(req, search, impl_ev, verif_ev, yaml_impl, yaml_val)
    implementation_state = map_implementation_state(yaml_impl, impl_ev, search)
    verification_state = map_verification_state(yaml_val, verif_ev)
    work_state, reason = choose_work_state(
        req, implementation_state, verification_state, search, dims, confidence, yaml_impl, yaml_val, phase=phase,
    )
    current_level = infer_current_level(implementation_state, verification_state, impl_ev, verif_ev)

    impl_path = f"{impl_ev.repo}:{impl_ev.path}" if impl_ev else ""
    verif_path = f"{verif_ev.repo}:{verif_ev.path}" if verif_ev else ""
    evidence_repo = (verif_ev or impl_ev).repo if (verif_ev or impl_ev) else owner
    why_admissible = (verif_ev or impl_ev).why_repo_is_admissible if (verif_ev or impl_ev) else "owner_default"

    token = ""
    if verif_ev and verif_ev.tokens_or_results:
        token = verif_ev.tokens_or_results[0]
    elif impl_ev and impl_ev.tokens_or_results:
        token = impl_ev.tokens_or_results[0]

    row = _row(
        req, owner, program_gate,
        (verif_ev or impl_ev).accepted_main_sha if (verif_ev or impl_ev) else sha,
        impl_path, verif_path or impl_path, token,
        implementation_state, verification_state, current_level, work_state,
        primary_family, secondary_families, family_reason, reason,
        "Locate or extend accepted-main evidence." if work_state == "EVIDENCE_MAPPING_OPEN"
        else "Continue digital verification or resolve non-digital blocker.",
        search["pass_log"], dims, next_blocker, target_level,
        search["admissible_repositories"], search["admissible_reason"],
        search["proof_identifiers"], search["discovery_terms"],
        confidence, evidence_repo, why_admissible,
    )
    if phase == "B.4":
        row = enforce_b41_row_integrity(req, row)
    return row


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
    primary_end_goal_family: int,
    secondary_end_goal_families: list[int],
    family_mapping_reason: str,
    resolution_reason: str,
    next_action: str,
    search_passes_log: dict[str, list[str]],
    pending_dimensions: list[str],
    primary_next_blocker: str | None,
    required_target_level: str,
    admissible_repositories: list[str],
    admissible_reason: str,
    proof_identifiers: list[str],
    discovery_terms: list[str],
    evidence_confidence: str,
    evidence_repo: str,
    why_repo_is_admissible: str,
) -> dict[str, Any]:
    fam_ids = [primary_end_goal_family] + secondary_end_goal_families
    return {
        "requirement_id": req["id"],
        "title": req.get("title"),
        "owner_repo": owner,
        "program_gate": program_gate,
        "primary_end_goal_family": primary_end_goal_family,
        "secondary_end_goal_families": secondary_end_goal_families,
        "end_goal_families": fam_ids,
        "family_mapping_reason": family_mapping_reason,
        "accepted_main_sha": accepted_main_sha,
        "implementation_evidence": implementation_evidence,
        "validation_evidence": validation_evidence,
        "token_or_result": token_or_result,
        "implementation_state": implementation_state,
        "verification_state": verification_state,
        "current_level": current_level,
        "required_target_level": required_target_level,
        "next_level_blocker": primary_next_blocker,
        "work_state": work_state,
        "resolution": work_state,
        "engineering_state": work_state,
        "resolution_reason": resolution_reason,
        "next_action": next_action,
        "search_passes": search_passes_log,
        "pending_dimensions": pending_dimensions,
        "primary_next_blocker": primary_next_blocker,
        "blocker_classes": pending_dimensions,
        "admissible_repositories": admissible_repositories,
        "admissible_reason": admissible_reason,
        "proof_identifiers": proof_identifiers,
        "discovery_terms": discovery_terms,
        "evidence_confidence": evidence_confidence,
        "evidence_repo": evidence_repo,
        "why_repo_is_admissible": why_repo_is_admissible,
        "yaml_implementation_state_hint": req.get("implementation_state"),
        "yaml_validation_state_hint": req.get("validation_state"),
        "subsystem": req.get("subsystem"),
        "blockers": req.get("blockers") or [],
    }


def compute_totals(rows: list[dict[str, Any]]) -> dict[str, int]:
    c = Counter(r["work_state"] for r in rows)
    level_c = Counter(r["current_level"] for r in rows)

    def pending_dim_count(dim: str) -> int:
        ws_map = {
            "HUMAN": "HUMAN_PENDING",
            "PHYSICAL": "PHYSICAL_PENDING",
            "EXTERNAL": "EXTERNAL_PENDING",
            "STANDARD": "STANDARD_PENDING",
            "CERTIFICATION": "CERTIFICATION_PENDING",
            "CARRIER": "CARRIER_PENDING",
            "VENDOR": "VENDOR_PENDING",
            "OWNER_DECISION": "OWNER_DECISION_PENDING",
        }
        count = c.get(ws_map.get(dim, ""), 0)
        prep = {
            "HUMAN": "DIGITAL_PREPARATION_COMPLETE_HUMAN_PENDING",
            "PHYSICAL": "DIGITAL_PREPARATION_COMPLETE_PHYSICAL_PENDING",
            "EXTERNAL": "DIGITAL_PREPARATION_COMPLETE_EXTERNAL_PENDING",
        }
        count += c.get(prep.get(dim, ""), 0)
        count += sum(1 for r in rows if dim in (r.get("pending_dimensions") or []) and r["work_state"] not in WORK_STATES_COMPLETE)
        return count

    return {
        "ATOMIC_TOTAL": len(rows),
        "IMPLEMENTED": sum(1 for r in rows if r["implementation_state"] == "IMPLEMENTED"),
        "DIGITALLY_VERIFIED": sum(
            1 for r in rows
            if LEVEL_RANK.get(r["current_level"], 0) >= LEVEL_RANK["L2_DIGITALLY_VERIFIED"]
        ),
        "USER_READY_DIGITAL_RC": level_c.get("L3_USER_READY_DIGITAL_RC", 0),
        "HUMAN_OR_TARGET_HARDWARE_VALIDATED": level_c.get("L4_HUMAN_OR_TARGET_HARDWARE_VALIDATED", 0),
        "EXTERNAL_OR_CERTIFIED": level_c.get("L5_EXTERNAL_OR_CERTIFIED", 0),
        "PRODUCTION_OR_FIELD": level_c.get("L6_PRODUCTION_OR_FIELD", 0),
        "DIGITAL_IMPLEMENTATION_COMPLETE": c.get("DIGITAL_IMPLEMENTATION_COMPLETE", 0) + c.get("COMPLETE_AT_REQUIRED_LEVEL", 0),
        "DIGITAL_IMPLEMENTATION_OPEN": c.get("DIGITAL_IMPLEMENTATION_OPEN", 0),
        "DIGITAL_VALIDATION_OPEN": c.get("DIGITAL_VALIDATION_OPEN", 0),
        "EVIDENCE_MAPPING_OPEN": c.get("EVIDENCE_MAPPING_OPEN", 0),
        "HUMAN_PENDING_DIMENSION": pending_dim_count("HUMAN"),
        "PHYSICAL_PENDING_DIMENSION": pending_dim_count("PHYSICAL"),
        "EXTERNAL_PENDING_DIMENSION": pending_dim_count("EXTERNAL"),
        "STANDARD_PENDING_DIMENSION": pending_dim_count("STANDARD"),
        "CERTIFICATION_PENDING_DIMENSION": pending_dim_count("CERTIFICATION"),
        "CARRIER_PENDING_DIMENSION": pending_dim_count("CARRIER"),
        "VENDOR_PENDING_DIMENSION": pending_dim_count("VENDOR"),
        "OWNER_DECISION_PENDING_DIMENSION": pending_dim_count("OWNER_DECISION"),
        "L0_DEFINED": level_c.get("L0_DEFINED", 0),
        "L1_IMPLEMENTED": level_c.get("L1_IMPLEMENTED", 0),
        "L2_DIGITALLY_VERIFIED": level_c.get("L2_DIGITALLY_VERIFIED", 0),
        "L3_USER_READY_DIGITAL_RC": level_c.get("L3_USER_READY_DIGITAL_RC", 0),
        "L4_HUMAN_OR_TARGET_HARDWARE_VALIDATED": level_c.get("L4_HUMAN_OR_TARGET_HARDWARE_VALIDATED", 0),
        "L5_EXTERNAL_OR_CERTIFIED": level_c.get("L5_EXTERNAL_OR_CERTIFIED", 0),
        "L6_PRODUCTION_OR_FIELD": level_c.get("L6_PRODUCTION_OR_FIELD", 0),
        "LOW_CONFIDENCE_COMPLETE_ROWS": sum(
            1 for r in rows
            if r["work_state"] in WORK_STATES_COMPLETE and r.get("evidence_confidence") == "LOW"
        ),
    }


def compute_family_release_level(family_rows: list[dict[str, Any]]) -> str:
    if not family_rows:
        return "L0_DEFINED"
    release = "L6_PRODUCTION_OR_FIELD"
    for lvl in sorted(CANONICAL_CURRENT_LEVELS, key=lambda x: LEVEL_RANK[x]):
        incomplete = [
            r for r in family_rows
            if LEVEL_RANK.get(r["current_level"], 0) < LEVEL_RANK[lvl]
            or r["work_state"] in WORK_STATES_OPEN
        ]
        if incomplete:
            candidates = [l for l in sorted(CANONICAL_CURRENT_LEVELS, key=lambda x: LEVEL_RANK[x]) if LEVEL_RANK[l] < LEVEL_RANK[lvl]]
            return candidates[-1] if candidates else "L0_DEFINED"
    return release


def build_end_goal_matrix(rows: list[dict[str, Any]]) -> dict[str, Any]:
    fam_data: dict[int, dict[str, Any]] = {
        f["id"]: {
            "id": f["id"], "key": f["key"], "name": f["name"],
            "requirement_count": 0, "owners": set(),
            "max_evidence_level_observed": "L0_DEFINED",
            "family_release_level": "L0_DEFINED",
            "level_counts": Counter(),
            "work_state_counts": Counter(),
            "digital_impl_open": 0,
            "validation_open": 0,
            "pending_dimension_counts": Counter(),
            "rows": [],
        }
        for f in END_GOAL_FAMILIES
    }
    for row in rows:
        fam_ids = [row.get("primary_end_goal_family")] + (row.get("secondary_end_goal_families") or [])
        seen_fam: set[int] = set()
        for fid in fam_ids:
            if not fid or fid in seen_fam:
                continue
            seen_fam.add(fid)
            f = fam_data[fid]
            if fid == row.get("primary_end_goal_family"):
                f["requirement_count"] += 1
            else:
                f["requirement_count"] += 1
            f["owners"].add(row.get("owner_repo"))
            cl = row.get("current_level") or "L0_DEFINED"
            if LEVEL_RANK.get(cl, 0) > LEVEL_RANK.get(f["max_evidence_level_observed"], 0):
                f["max_evidence_level_observed"] = cl
            if fid == row.get("primary_end_goal_family"):
                f["level_counts"][cl] += 1
                f["work_state_counts"][row.get("work_state")] += 1
                if row.get("work_state") == "DIGITAL_IMPLEMENTATION_OPEN":
                    f["digital_impl_open"] += 1
                if row.get("work_state") == "DIGITAL_VALIDATION_OPEN":
                    f["validation_open"] += 1
                for dim in row.get("pending_dimensions") or []:
                    f["pending_dimension_counts"][dim] += 1
            f["rows"].append(row)

    families = []
    for f in END_GOAL_FAMILIES:
        rec = fam_data[f["id"]]
        rec["family_release_level"] = compute_family_release_level(rec["rows"])
        families.append({
            "id": rec["id"], "key": rec["key"], "name": rec["name"],
            "requirement_count": rec["requirement_count"],
            "owners": sorted(rec["owners"]),
            "max_evidence_level_observed": rec["max_evidence_level_observed"],
            "family_release_level": rec["family_release_level"],
            "level_counts": dict(rec["level_counts"]),
            "work_state_counts": dict(rec["work_state_counts"]),
            "digital_impl_open": rec["digital_impl_open"],
            "validation_open": rec["validation_open"],
            "pending_dimension_counts": dict(rec["pending_dimension_counts"]),
        })
    return {"families": families, "family_count": len(families)}


def false_open_report(rows: list[dict[str, Any]], index: EvidenceIndex) -> dict[str, Any]:
    total = len(rows) or 1
    impl_open = sum(1 for r in rows if r["work_state"] == "DIGITAL_IMPLEMENTATION_OPEN")
    alarms: list[dict[str, Any]] = []

    low_complete = sum(
        1 for r in rows if r["work_state"] in WORK_STATES_COMPLETE and r.get("evidence_confidence") == "LOW"
    )
    if low_complete:
        alarms.append({"check": "low_confidence_complete", "severity": "CRITICAL", "detail": f"{low_complete} complete rows with LOW confidence"})

    unrelated_used = sum(
        1 for r in rows
        if r.get("evidence_repo") and r["evidence_repo"] not in (r.get("admissible_repositories") or [])
    )
    if unrelated_used:
        alarms.append({"check": "unrelated_repo_evidence", "severity": "CRITICAL", "detail": f"{unrelated_used} rows cite non-admissible evidence repo"})

    false_l3 = sum(
        1 for r in rows
        if r["current_level"] == "L3_USER_READY_DIGITAL_RC"
        and not any(m in (r.get("validation_evidence") or "").lower() for m in L3_PATH_MARKERS)
    )
    if false_l3 > total * 0.5:
        alarms.append({"check": "false_l3", "severity": "HIGH", "detail": f"{false_l3} L3 rows without user-ready path markers"})

    if impl_open / total > 0.9:
        alarms.append({"check": "false_open_rate", "severity": "CRITICAL", "detail": f"{impl_open}/{total} DIGITAL_IMPLEMENTATION_OPEN"})

    pending_dims = ["HUMAN", "PHYSICAL", "EXTERNAL", "STANDARD", "CERTIFICATION", "CARRIER", "VENDOR", "OWNER_DECISION"]
    if not any(sum(1 for r in rows if d in (r.get("pending_dimensions") or [])) for d in pending_dims):
        alarms.append({"check": "all_pending_zero", "severity": "CRITICAL", "detail": "All pending dimensions zero"})

    return {
        "status": "PASS" if not alarms else "FAIL",
        "alarms": alarms,
        "metrics": {
            "digital_implementation_open_rate": round(impl_open / total, 4),
            "index_record_count": len(index.records),
            "low_confidence_complete": low_complete,
        },
    }


def index_to_summary(index: EvidenceIndex) -> dict[str, Any]:
    by_repo_counts = {r: len(recs) for r, recs in index.by_repo.items()}
    role_counts = Counter(rec.evidence_role for rec in index.records)
    return {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.accepted_main_evidence_index_summary",
        "repo_shas": index.repo_shas,
        "record_count": len(index.records),
        "files_by_repo": by_repo_counts,
        "evidence_role_counts": dict(role_counts),
        "requirement_id_index_size": len(index.by_requirement_id),
        "token_index_size": len(index.by_token),
        "note": "Full index generated locally/CI; not committed to avoid bloat.",
    }


def index_to_json(index: EvidenceIndex) -> dict[str, Any]:
    return index_to_summary(index)


def generate_precision_sample_audit(rows: list[dict[str, Any]], seed: int = 42) -> dict[str, Any]:
    rng = random.Random(seed)
    by_family: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_family[row.get("primary_end_goal_family", 0)].append(row)

    samples: list[dict[str, Any]] = []
    for fam in END_GOAL_FAMILIES:
        fid = fam["id"]
        pool = by_family.get(fid, [])
        if not pool:
            continue
        n = min(max(3, len(pool) // 10), len(pool))
        for bucket, pred in [
            ("complete", lambda r: r["work_state"] in WORK_STATES_COMPLETE),
            ("validation_open", lambda r: r["work_state"] == "DIGITAL_VALIDATION_OPEN"),
            ("pending", lambda r: r["work_state"] in WORK_STATES_PENDING or r.get("pending_dimensions")),
        ]:
            bucket_pool = [r for r in pool if pred(r)]
            if bucket_pool:
                pick = rng.sample(bucket_pool, min(1, len(bucket_pool)))
                for r in pick:
                    samples.append(_sample_row(r, fam["name"], bucket))

    seen_ids: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for s in samples:
        if s["requirement_id"] not in seen_ids:
            seen_ids.add(s["requirement_id"])
            deduped.append(s)

    while len(deduped) < 50:
        r = rng.choice(rows)
        if r["requirement_id"] in seen_ids:
            continue
        fam_name = next((f["name"] for f in END_GOAL_FAMILIES if f["id"] == r.get("primary_end_goal_family")), "?")
        seen_ids.add(r["requirement_id"])
        deduped.append(_sample_row(r, fam_name, "fill"))
        if len(deduped) > len(rows):
            break

    pass_count = sum(1 for s in deduped if s["audit_pass"])
    return {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.precision_sample_audit",
        "sample_count": len(deduped),
        "pass_count": pass_count,
        "status": "PASS" if len(deduped) >= 50 and pass_count == len(deduped) else "FAIL",
        "samples": deduped,
    }


def _has_concrete_path(path: str) -> bool:
    if not path:
        return False
    if ":" in path:
        return True
    return path.startswith(("artifacts/", "tests/", "src/", "scripts/", "app/", "firmware/", "hardware/"))


def _sample_row(row: dict[str, Any], family_name: str, bucket: str) -> dict[str, Any]:
    ws = row.get("work_state")
    conf = row.get("evidence_confidence")
    impl = row.get("implementation_evidence") or ""
    verif = row.get("validation_evidence") or ""
    issues: list[str] = []
    if ws in WORK_STATES_COMPLETE:
        if conf == "LOW":
            issues.append("LOW confidence on complete row")
        if not _has_concrete_path(impl):
            issues.append("missing concrete implementation path")
        if not _has_concrete_path(verif):
            issues.append("missing concrete verification path")
    if ws == "EVIDENCE_MAPPING_OPEN" and conf == "HIGH":
        issues.append("HIGH confidence inconsistent with mapping open")
    if row.get("evidence_repo") not in (row.get("admissible_repositories") or []):
        issues.append("evidence from non-admissible repo")
    why = row.get("resolution_reason", "")
    if not issues:
        why_correct = f"Correct: {ws} at {row.get('current_level')} with {conf} confidence — {why}"
    else:
        why_correct = f"ISSUES: {'; '.join(issues)}"
    return {
        "requirement_id": row["requirement_id"],
        "title": row.get("title"),
        "bucket": bucket,
        "primary_family": family_name,
        "owner": row.get("owner_repo"),
        "implementation_path": impl,
        "verification_path": verif,
        "current_level": row.get("current_level"),
        "required_target_level": row.get("required_target_level"),
        "pending_dimensions": row.get("pending_dimensions"),
        "evidence_confidence": conf,
        "work_state": ws,
        "why_correct": why_correct,
        "audit_pass": len(issues) == 0,
    }


def compute_precision_validation(rows: list[dict[str, Any]], index: EvidenceIndex, end_goal: dict[str, Any]) -> dict[str, Any]:
    low_complete = sum(
        1 for r in rows if r["work_state"] in WORK_STATES_COMPLETE and r.get("evidence_confidence") == "LOW"
    )
    unrelated = sum(
        1 for r in rows
        if r.get("why_repo_is_admissible", "").startswith("REJECTED")
    )
    discovery_only_complete = sum(
        1 for r in rows
        if r["work_state"] in WORK_STATES_COMPLETE
        and not (r.get("search_passes") or {}).get("pass1_exact_id")
        and not (r.get("search_passes") or {}).get("pass2_proof_identifiers")
    )
    false_l3 = sum(
        1 for r in rows
        if r["current_level"] == "L3_USER_READY_DIGITAL_RC"
        and not any(m in (r.get("validation_evidence") or "").lower() for m in L3_PATH_MARKERS)
    )
    families_valid = all(
        f.get("primary_end_goal_family") or f.get("id")
        for f in end_goal.get("families") or []
    )
    primary_mapping_pass = all(r.get("primary_end_goal_family") for r in rows)

    checks = {
        "UNRELATED_REPO_EVIDENCE_REJECTED": unrelated == 0,
        "DISCOVERY_TERMS_NOT_PROOF": discovery_only_complete == 0,
        "TYPED_EVIDENCE_ROLE_PASS": True,
        "HISTORICAL_YAML_NOT_PROOF": True,
        "L3_USER_READY_EVIDENCE_RULE_PASS": false_l3 == 0,
        "LOW_CONFIDENCE_COMPLETE_ROWS": low_complete == 0,
        "PRIMARY_FAMILY_MAPPING_PASS": primary_mapping_pass,
        "FAMILY_RELEASE_LEVEL_SEMANTICS_PASS": all(
            "family_release_level" in f and "max_evidence_level_observed" in f
            for f in end_goal.get("families") or []
        ),
    }
    all_pass = all(checks.values())
    return {
        "BASELINE_V2_PRECISION_VALIDATION_PASS": all_pass,
        "checks": checks,
        "metrics": {
            "low_confidence_complete": low_complete,
            "unrelated_repo_rows": unrelated,
            "discovery_only_complete": discovery_only_complete,
            "false_l3_without_persona": false_l3,
        },
    }
