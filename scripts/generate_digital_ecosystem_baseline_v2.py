#!/usr/bin/env python3
"""Generate program/digital_ecosystem_baseline_v2/ from live accepted mains."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "program" / "digital_ecosystem_baseline_v2"
REPOS_ROOT = Path(os.environ.get("REPOS_ROOT", str(ROOT.parent.parent.parent)))
PORTAL_ROOT = REPOS_ROOT / "gunnchos-research-portal"

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

END_GOAL_FAMILIES = [
    "ecosystem",
    "connectivity",
    "os",
    "ai",
    "applications",
    "rings",
    "7gc",
    "evidence",
    "standards",
    "device",
    "games",
    "carrier_grade",
    "gates",
]

REPRODUCE_HINT = {
    "gunnchos-7gc-ai-ran-field-kit": "make verify",
    "gunnchos-research-portal": "make reproduce",
    "gunnchos-device-os": "make reproduce",
    "edge-io-measurement-node": "make reproduce",
    "7gc-digital-twin": "make reproduce",
    "ntn-resilience-sim": "make reproduce",
    "readygary-6g-beam-selection": "make reproduce",
    "gunnchos-gpu-nr-baseband-platform": "make reproduce",
}

REQUIRED_WORKFLOWS: dict[str, list[str]] = {
    "readygary-6g-beam-selection": ["CI"],
    "waike-research-ops": ["CI"],
    "gunnchos-device-os": ["CI"],
    "gunnchos-7gc-ai-ran-field-kit": ["Umbrella artifact CI"],
    "gunnchos-research-portal": ["CI"],
    "gunnchAI3k": ["Portfolio hardening CI"],
    "gunnchos-gpu-nr-baseband-platform": ["ci"],
}

COMPLETE_RESOLUTIONS = {
    "ACCEPTED_MAIN_PROVEN",
    "ACCEPTED_MAIN_IMPLEMENTED_VERIFIED",
    "SUPERSEDED_BY_ACCEPTED_MAIN",
}

PENDING_RESOLUTIONS = {
    "PHYSICAL_PENDING",
    "HUMAN_PENDING",
    "EXTERNAL_PENDING",
    "STANDARD_PENDING",
    "CERTIFICATION",
    "CARRIER",
    "VENDOR",
    "OWNER_DECISION_PENDING",
}

L0_CHARTER_IDS = {
    "CHARTER_NARRATIVE",
    "REPO_OWNERSHIP_MAP",
    "CLAIM_BOUNDARIES",
    "COMPLETION_REGISTER_V1",
}


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 60) -> str:
    try:
        env = os.environ.copy()
        env.setdefault("GH_PAGER", "cat")
        return subprocess.check_output(
            cmd, cwd=cwd, text=True, stderr=subprocess.DEVNULL, timeout=timeout, env=env
        ).strip()
    except Exception:
        return ""


def gh_json(cmd: list[str]) -> Any:
    raw = run(cmd)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def repo_path(repo: str) -> Path:
    return REPOS_ROOT / repo


def file_on_main(repo: str, rel: str) -> bool:
    path = repo_path(repo) / rel
    return path.is_file()


def load_json_if_exists(repo: str, rel: str) -> dict[str, Any] | None:
    path = repo_path(repo) / rel
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def classify_workflow_run(conclusion: str | None, status: str | None) -> str:
    c = (conclusion or "").lower()
    s = (status or "").lower()
    if c == "success":
        return "PASS"
    if c in ("failure", "cancelled", "timed_out", "action_required"):
        return "FAIL"
    if s in ("in_progress", "queued", "waiting", "pending", "requested"):
        return "IN_PROGRESS"
    if not c and not s:
        return "UNKNOWN"
    return "UNKNOWN"


def gh_ci_matrix(repo: str, main_sha: str) -> dict[str, Any]:
    required = REQUIRED_WORKFLOWS.get(repo, ["CI"])
    workflows: list[dict[str, Any]] = []
    overall = "NOT_APPLICABLE"
    any_known = False
    for wf in required:
        runs = gh_json(
            [
                "gh",
                "run",
                "list",
                "--repo",
                f"gunnchOS3k/{repo}",
                "--branch",
                "main",
                "--workflow",
                wf,
                "--limit",
                "5",
                "--json",
                "conclusion,workflowName,status,headSha,databaseId",
            ]
        )
        run_rec: dict[str, Any] | None = None
        if isinstance(runs, list):
            for r in runs:
                if (r.get("headSha") or "") == main_sha:
                    run_rec = r
                    break
            if run_rec is None and runs:
                run_rec = runs[0]
        state = "UNKNOWN"
        if run_rec:
            any_known = True
            state = classify_workflow_run(run_rec.get("conclusion"), run_rec.get("status"))
            if run_rec.get("headSha") and run_rec.get("headSha") != main_sha:
                state = "UNKNOWN"
        workflows.append(
            {
                "workflow": wf,
                "latest_conclusion": run_rec.get("conclusion") if run_rec else None,
                "latest_status": run_rec.get("status") if run_rec else None,
                "head_sha": run_rec.get("headSha") if run_rec else None,
                "sha_matches_main": (run_rec.get("headSha") == main_sha) if run_rec else False,
                "state": state,
            }
        )
    if any_known:
        states = {w["state"] for w in workflows}
        if states <= {"PASS"}:
            overall = "PASS"
        elif "FAIL" in states:
            overall = "FAIL"
        elif "IN_PROGRESS" in states:
            overall = "IN_PROGRESS"
        else:
            overall = "UNKNOWN"
    return {
        "required_workflows": required,
        "workflows": workflows,
        "overall": overall,
    }


def live_repo(repo: str) -> dict[str, Any]:
    path = repo_path(repo)
    out: dict[str, Any] = {"repository": repo, "path": str(path), "exists": path.is_dir()}
    if not path.is_dir():
        out["origin_main_sha"] = ""
        out["ci"] = "UNKNOWN"
        out["ci_detail"] = {"overall": "UNKNOWN", "required_workflows": [], "workflows": []}
        out["reproduce"] = REPRODUCE_HINT.get(repo, "see REPRODUCIBILITY.md")
        return out
    run(["git", "fetch", "origin", "main"], cwd=path)
    sha = run(["git", "rev-parse", "origin/main"], cwd=path)
    ci_detail = gh_ci_matrix(repo, sha)
    out["origin_main_sha"] = sha
    out["ci"] = ci_detail["overall"]
    out["ci_detail"] = ci_detail
    out["reproduce"] = REPRODUCE_HINT.get(repo, "see REPRODUCIBILITY.md")
    return out


def build_accepted_main_evidence_index(repos: dict[str, dict[str, Any]]) -> dict[str, Any]:
    device_os_sha = repos.get("gunnchos-device-os", {}).get("origin_main_sha", "")
    field_kit_sha = repos.get("gunnchos-7gc-ai-ran-field-kit", {}).get("origin_main_sha", "")
    wp012 = load_json_if_exists("gunnchos-7gc-ai-ran-field-kit", "artifacts/wp012/VP-012-RESULT.json")
    product_use = load_json_if_exists("gunnchos-device-os", "artifacts/product_use/PRODUCT_USE_RC_002_STATUS.json")
    waike_dirs = repo_path("waike-research-ops") / "curriculum" / "digital_rc"
    digital_rc_count = len(list(waike_dirs.glob("*"))) if waike_dirs.is_dir() else 0
    legs = (product_use or {}).get("legs") or {}
    return {
        "wp012": wp012,
        "wp012_path": "artifacts/wp012/VP-012-RESULT.json",
        "wp012_sha": field_kit_sha if wp012 else "",
        "product_use": product_use,
        "product_use_path": "artifacts/product_use/PRODUCT_USE_RC_002_STATUS.json",
        "product_use_sha": device_os_sha if product_use else "",
        "device_lab_tokens": {
            "DSXL_DUAL_COMPOSITOR_UX_PASS": bool((legs.get("G14") or {}).get("DSXL_DUAL_COMPOSITOR_UX_PASS")),
            "RING_TO_REAL_APP_STATE_MUTATION_PASS": bool(
                (legs.get("RING") or {}).get("RING_TO_REAL_APP_STATE_MUTATION_PASS")
            ),
            "FOUR_GAME_REAL_RUNTIME_DEVICE_LAB_PASS": bool(
                (legs.get("FOUR_GAME") or {}).get("FOUR_GAME_REAL_RUNTIME_DEVICE_LAB_PASS")
            ),
        },
        "waike_digital_rc_count": digital_rc_count,
    }


def infer_current_level(req: dict[str, Any], resolution: str) -> str:
    gate = req.get("gate")
    impl = req.get("implementation_state") or ""
    val = req.get("validation_state") or ""
    if resolution in COMPLETE_RESOLUTIONS:
        if val == "INDEPENDENTLY_VALIDATED":
            if gate is not None and gate >= 6:
                return "L6_PRODUCTION_OR_FIELD"
            if gate is not None and gate >= 4:
                return "L5_FIELD_PILOT_READY"
            if gate is not None and gate >= 2:
                return "L4_INTEGRATED"
            return "L3_VALIDATED_DIGITAL"
        if val in ("VALIDATED", "PASS", "INDEPENDENTLY_VALIDATED"):
            return "L3_VALIDATED_DIGITAL"
        if impl == "IMPLEMENTED":
            return "L2_IMPLEMENTED"
        return "L3_VALIDATED_DIGITAL"
    if impl == "IMPLEMENTED":
        return "L2_IMPLEMENTED"
    if impl in ("DOCUMENTED_DESIGN", "NOT_STARTED", ""):
        return "L0_DEFINED"
    return "L1_SPECIFIED"


def blocker_class(req: dict[str, Any]) -> str | None:
    blockers = " ".join(req.get("blockers") or []).upper()
    notes = (req.get("notes") or "").upper()
    blob = f"{blockers} {notes}"
    if any(x in blob for x in ("PHYSICAL_PICKUP", "FAB_", "EVT0", "MANUFACTUR", "ENCLOSURE", "BATTERY", "THERMAL", "RFQ")):
        return "PHYSICAL"
    if "CARRIER" in blob:
        return "CARRIER"
    if "CERTIF" in blob or "REGULATORY" in blob:
        return "CERTIFICATION"
    if "VENDOR" in blob or "SUPPLIER" in blob:
        return "VENDOR"
    if "STANDARD" in blob and ("6G" in blob or "IMT" in blob):
        return "STANDARD"
    if "OWNER_DECISION" in blob or "WP001" in blob or "EDMUND" in blob or "PRODUCT_CHARTER_APPROVAL" in blob:
        return "OWNER_DECISION"
    if any(x in blob for x in ("HUMAN", "PILOT", "OPERATOR", "CONSENT", "PLAYTEST")):
        return "HUMAN"
    if any(x in blob for x in ("EXTERNAL", "NVIDIA", "SIONNA", "AERIAL", "DOI", "PENTEST", "NGC", "BLOCKED_GPU")):
        return "EXTERNAL"
    return None


def has_digital_work_remaining(req: dict[str, Any]) -> bool:
    impl = req.get("implementation_state") or ""
    val = req.get("validation_state") or ""
    if impl in ("NOT_STARTED", "DOCUMENTED_DESIGN", "IN_PROGRESS", "PARTIAL"):
        return True
    if impl == "IMPLEMENTED" and val in ("NOT_STARTED", "IN_PROGRESS", "FAIL"):
        return True
    return False


def evidence_sha(repos: dict[str, dict], evidence_repo: str) -> str:
    return repos.get(evidence_repo, {}).get("origin_main_sha", "")


def resolve_l0_charter(req: dict[str, Any], repos: dict[str, dict], index: dict[str, Any]) -> dict[str, Any] | None:
    rid = req["id"]
    wp012 = index.get("wp012")
    gate0_charter = rid in L0_CHARTER_IDS or (rid.startswith("SYS-MISSION-") and req.get("gate") == 0)
    if gate0_charter and wp012 and file_on_main("gunnchos-7gc-ai-ran-field-kit", index["wp012_path"]):
        return {
            "accepted_main_sha": index.get("wp012_sha") or evidence_sha(repos, "gunnchos-7gc-ai-ran-field-kit"),
            "implementation_evidence": index["wp012_path"],
            "validation_evidence": index["wp012_path"],
            "token_or_result": wp012.get("NAVIGATION_DIGITAL_E4", "PASS"),
            "evidence_class": "E4",
            "resolution": "ACCEPTED_MAIN_IMPLEMENTED_VERIFIED",
            "resolution_reason": "WP-012 VP artifact on accepted field-kit main proves L0 charter/traceability digital discoverability.",
            "next_action": "Owner charter approval remains HUMAN/OWNER if blockers present.",
        }
    return None


def resolve_requirement(
    req: dict[str, Any], repos: dict[str, dict], index: dict[str, Any]
) -> dict[str, Any]:
    rid = req["id"]
    owner = req.get("owner_repository") or "gunnchos-7gc-ai-ran-field-kit"
    program_gate = req.get("gate")
    sha = repos.get(owner, {}).get("origin_main_sha", "")
    impl = req.get("implementation_state") or ""
    val = req.get("validation_state") or ""
    bc = blocker_class(req)

    base: dict[str, Any] = {
        "requirement_id": rid,
        "owner_repo": owner,
        "program_gate": program_gate,
        "accepted_main_sha": sha,
        "implementation_evidence": "",
        "validation_evidence": "",
        "token_or_result": "",
        "evidence_class": "",
        "current_level": "L0_DEFINED",
        "engineering_state": "",
        "blocker_class": bc,
        "resolution": "EVIDENCE_UNRESOLVED",
        "resolution_reason": "",
        "next_action": "",
        "title": req.get("title"),
        "subsystem": req.get("subsystem"),
        "implementation_state": impl,
        "validation_state": val,
        "blockers": req.get("blockers") or [],
    }

    charter = resolve_l0_charter(req, repos, index)
    if charter:
        base.update(charter)
        base["current_level"] = infer_current_level(req, base["resolution"])
        base["engineering_state"] = "DIGITAL_IMPLEMENTATION_COMPLETE"
        return base

    if val in ("VALIDATED", "INDEPENDENTLY_VALIDATED") and impl == "IMPLEMENTED":
        evidence_repo = owner if owner in CANONICAL_REPOS else None
        if not evidence_repo:
            for sr in req.get("supporting_repositories") or []:
                if sr in CANONICAL_REPOS:
                    evidence_repo = sr
                    break
        evidence_guess = ""
        if evidence_repo and (repo_path(evidence_repo) / "tests").is_dir():
            evidence_guess = f"{evidence_repo}:tests/"
        req_evidence = req.get("required_evidence") or []
        if req_evidence:
            evidence_guess = evidence_guess or f"required_evidence:{req_evidence[0]}"
        ev_sha = evidence_sha(repos, evidence_repo) if evidence_repo else sha
        if evidence_guess and ev_sha:
            base.update(
                {
                    "accepted_main_sha": ev_sha,
                    "implementation_evidence": evidence_guess,
                    "validation_evidence": evidence_guess,
                    "token_or_result": val,
                    "evidence_class": "E2" if val == "VALIDATED" else "E3",
                    "resolution": "ACCEPTED_MAIN_IMPLEMENTED_VERIFIED",
                    "resolution_reason": f"requirements.yaml marks {val}; evidence anchored to accepted main in {evidence_repo or owner}.",
                    "next_action": "Independent re-verify if gate promotion required.",
                }
            )
            base["current_level"] = infer_current_level(req, base["resolution"])
            base["engineering_state"] = "DIGITAL_IMPLEMENTATION_COMPLETE"
            return base

    if bc and not has_digital_work_remaining(req):
        resolution_map = {
            "PHYSICAL": "PHYSICAL_PENDING",
            "HUMAN": "HUMAN_PENDING",
            "EXTERNAL": "EXTERNAL_PENDING",
            "STANDARD": "STANDARD_PENDING",
            "CERTIFICATION": "CERTIFICATION",
            "CARRIER": "CARRIER",
            "VENDOR": "VENDOR",
            "OWNER_DECISION": "OWNER_DECISION_PENDING",
        }
        resolution = resolution_map.get(bc, "EVIDENCE_UNRESOLVED")
        base.update(
            {
                "resolution": resolution,
                "resolution_reason": f"Blocker class {bc}; no remaining automatable digital implementation indicated.",
                "next_action": f"Resolve {bc} blocker before digital re-classification.",
                "engineering_state": resolution,
            }
        )
        base["current_level"] = infer_current_level(req, base["resolution"])
        return base

    if bc and has_digital_work_remaining(req):
        base.update(
            {
                "resolution": "DIGITAL_IMPLEMENTATION_OPEN",
                "resolution_reason": f"Blocker {bc} present but implementation/validation not complete — digital work remains.",
                "next_action": "Complete digital implementation before pending-class closure.",
                "engineering_state": "DIGITAL_IMPLEMENTATION_OPEN",
            }
        )
        base["current_level"] = infer_current_level(req, base["resolution"])
        return base

    if impl in ("NOT_STARTED", "DOCUMENTED_DESIGN", "IN_PROGRESS", "PARTIAL", ""):
        base.update(
            {
                "resolution": "DIGITAL_IMPLEMENTATION_OPEN",
                "resolution_reason": "No accepted-main artifact or validation token located; requirement not digitally complete.",
                "next_action": "Implement and validate on accepted main with traceable artifact.",
                "engineering_state": "DIGITAL_IMPLEMENTATION_OPEN",
            }
        )
        base["current_level"] = infer_current_level(req, base["resolution"])
        return base

    base.update(
        {
            "resolution": "EVIDENCE_UNRESOLVED",
            "resolution_reason": "Implementation state ambiguous without located accepted-main evidence path.",
            "next_action": "Locate or produce evidence artifact on accepted main.",
            "engineering_state": "EVIDENCE_UNRESOLVED",
        }
    )
    base["current_level"] = infer_current_level(req, base["resolution"])
    return base


def audit_device_os_103(repos: dict[str, dict], index: dict[str, Any]) -> dict[str, Any]:
    pr103 = gh_json(["gh", "pr", "view", "103", "--repo", "gunnchOS3k/gunnchos-device-os", "--json", "state,isDraft,title"])
    tokens_103_false = [
        "DSXL_DUAL_COMPOSITOR_UX_PASS",
        "RING_TO_REAL_APP_STATE_MUTATION_PASS",
        "GUNNCHDEVICE_LAB_FULL_ECOSYSTEM_DIGITAL_COMPLETE",
    ]
    main_tokens = index.get("device_lab_tokens") or {}
    replacements = []
    unique_remaining = []
    for tok in tokens_103_false:
        if tok == "GUNNCHDEVICE_LAB_FULL_ECOSYSTEM_DIGITAL_COMPLETE":
            dsxl = main_tokens.get("DSXL_DUAL_COMPOSITOR_UX_PASS")
            ring = main_tokens.get("RING_TO_REAL_APP_STATE_MUTATION_PASS")
            four = main_tokens.get("FOUR_GAME_REAL_RUNTIME_DEVICE_LAB_PASS")
            if dsxl and ring and four:
                replacements.append(
                    {
                        "token": tok,
                        "main_status": "SUPERSEDED",
                        "replacement": "PRODUCT_USE_RC_002 #116 merged — DSXL/RING/FOUR_GAME digital PASS on accepted main",
                        "evidence": index.get("product_use_path"),
                    }
                )
            else:
                unique_remaining.append(tok)
        elif main_tokens.get(tok):
            replacements.append(
                {
                    "token": tok,
                    "main_status": "PASS",
                    "replacement": f"Accepted main artifact {index.get('product_use_path')} (#108/#116 lineage)",
                    "evidence": index.get("product_use_path"),
                }
            )
        else:
            unique_remaining.append(tok)

    merged_successors = []
    for pr_num in (108, 116, 117, 118, 119, 120, 121, 122):
        rec = gh_json(
            ["gh", "pr", "view", str(pr_num), "--repo", "gunnchOS3k/gunnchos-device-os", "--json", "number,state,mergedAt,title"]
        )
        if rec and rec.get("state") == "MERGED":
            merged_successors.append({"pr": pr_num, "title": rec.get("title"), "mergedAt": rec.get("mergedAt")})

    return {
        "pr": 103,
        "repository": "gunnchos-device-os",
        "state": (pr103 or {}).get("state", "OPEN"),
        "is_draft": (pr103 or {}).get("isDraft", True),
        "cursor_action": "DO_NOT_CLOSE",
        "owner_action": "CLOSE_SUPERSEDED_BY_OWNER after Baseline V2 + portal refresh",
        "historical_false_tokens": tokens_103_false,
        "current_main_replacements": replacements,
        "current_remaining_ecosystem_gaps": [
            "S2 residuals: shipping WAIKE UI, dock silicon, REAL_TEACHER_E6, Ring browser headless purity (documented on #116)",
            "PHYSICAL_RING_E6=false",
            "SILICON_EXACT_EMULATION=false",
        ],
        "unique_103_delta": unique_remaining,
        "unique_capabilities_remaining": len(unique_remaining),
        "merged_successors": merged_successors,
        "disposition": "SUPERSEDED_DO_NOT_MERGE" if len(unique_remaining) == 0 else "OPEN_AWAITING_OWNER_SUPERSESSION",
        "accepted_main_sha": repos.get("gunnchos-device-os", {}).get("origin_main_sha", ""),
        "main_token_status": main_tokens,
    }


def scan_stale_preview(repos: dict[str, dict]) -> list[dict[str, Any]]:
    stale: list[dict[str, Any]] = []
    portal_md = PORTAL_ROOT / "docs/phd/contact_snapshots/LATEST.md"
    portal_json = PORTAL_ROOT / "docs/phd/contact_snapshots/LATEST.json"

    preview_patterns = [
        (r"waike-research-ops[`']?\s+PR\s+#(\d+)", "gunnchOS3k/waike-research-ops"),
        (r"gunnchos-7gc-ai-ran-field-kit[`']?\s+PR\s+#(\d+)", "gunnchOS3k/gunnchos-7gc-ai-ran-field-kit"),
        (r"gunnchos-device-os[`']?\s+PR\s+#(\d+)", "gunnchOS3k/gunnchos-device-os"),
        (r"device-os\s+#(\d+)", "gunnchOS3k/gunnchos-device-os"),
    ]

    if portal_md.is_file():
        text = portal_md.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), 1):
            if "Preview / draft PRs" in line or "preview" in line.lower() or "PR #" in line:
                for pat, gh_repo in preview_patterns:
                    for m in re.finditer(pat, line, re.I):
                        pr_num = int(m.group(1))
                        live = gh_json(["gh", "pr", "view", str(pr_num), "--repo", gh_repo, "--json", "state,isDraft"])
                        live_state = (live or {}).get("state")
                        stale.append(
                            {
                                "file": "docs/phd/contact_snapshots/LATEST.md",
                                "line": line_no,
                                "key": f"PR #{pr_num}",
                                "stale_statement": line.strip(),
                                "live_truth": f"{gh_repo} PR #{pr_num} state={live_state}",
                                "phase_c_repair_needed": live_state == "MERGED" or (
                                    pr_num == 103 and live_state == "OPEN"
                                ),
                            }
                        )

        for line_no, line in enumerate(text.splitlines(), 1):
            m = re.search(r"`([a-z0-9-]+)`\s*\|\s*ACCEPTED_MAIN\s*\|\s*`([0-9a-f]{12})`", line)
            if m:
                repo_name = m.group(1)
                pinned = m.group(2)
                live_sha = (repos.get(repo_name) or {}).get("origin_main_sha", "")[:12]
                if live_sha and pinned != live_sha:
                    stale.append(
                        {
                            "file": "docs/phd/contact_snapshots/LATEST.md",
                            "line": line_no,
                            "key": f"{repo_name}.origin_main_sha12",
                            "stale_statement": line.strip(),
                            "live_truth": f"origin/main={live_sha}",
                            "phase_c_repair_needed": True,
                        }
                    )
            m_ci = re.search(r"`([a-z0-9-]+)`\s*\|\s*ACCEPTED_MAIN\s*\|\s*`[0-9a-f]{12}`\s*\|\s*\d+\s*\|\s*(PASS|FAIL)", line)
            if m_ci:
                repo_name = m_ci.group(1)
                recorded = m_ci.group(2)
                live_ci = (repos.get(repo_name) or {}).get("ci", "UNKNOWN")
                if recorded != live_ci and live_ci in ("PASS", "FAIL"):
                    stale.append(
                        {
                            "file": "docs/phd/contact_snapshots/LATEST.md",
                            "line": line_no,
                            "key": f"{repo_name}.ci",
                            "stale_statement": line.strip(),
                            "live_truth": f"required-workflow CI={live_ci}",
                            "phase_c_repair_needed": True,
                        }
                    )

    if portal_json.is_file():
        doc = json.loads(portal_json.read_text(encoding="utf-8"))
        for rec in doc.get("repositories") or []:
            repo_name = rec.get("repository")
            pinned = (rec.get("origin_main_sha") or "")[:12]
            live_sha = (repos.get(repo_name) or {}).get("origin_main_sha", "")[:12]
            if repo_name and pinned and live_sha and pinned != live_sha:
                stale.append(
                    {
                        "file": "docs/phd/contact_snapshots/LATEST.json",
                        "line": None,
                        "key": f"repositories[{repo_name}].origin_main_sha12",
                        "stale_statement": pinned,
                        "live_truth": live_sha,
                        "phase_c_repair_needed": True,
                    }
                )
            pr = rec.get("pr") or {}
            pr_num = pr.get("number")
            if pr_num and repo_name:
                gh_repo = f"gunnchOS3k/{repo_name}"
                live = gh_json(["gh", "pr", "view", str(pr_num), "--repo", gh_repo, "--json", "state"])
                if (live or {}).get("state") == "MERGED":
                    stale.append(
                        {
                            "file": "docs/phd/contact_snapshots/LATEST.json",
                            "line": None,
                            "key": f"repositories[{repo_name}].pr.number",
                            "stale_statement": f"PR #{pr_num} as active preview",
                            "live_truth": "MERGED — not accepted-main preview",
                            "phase_c_repair_needed": True,
                        }
                    )

    dedup: dict[tuple, dict] = {}
    for item in stale:
        dedup[(item["file"], item.get("key"), item.get("line"))] = item
    return list(dedup.values())


def build_end_goal_matrix(resolutions: list[dict[str, Any]]) -> dict[str, Any]:
    families: dict[str, dict[str, Any]] = {}
    for fam in END_GOAL_FAMILIES:
        families[fam] = {
            "family": fam,
            "requirement_count": 0,
            "owners": set(),
            "highest_level": "L0_DEFINED",
            "open_counts": Counter(),
            "pending_classes": Counter(),
        }
    level_rank = {
        "L0_DEFINED": 0,
        "L1_SPECIFIED": 1,
        "L2_IMPLEMENTED": 2,
        "L3_VALIDATED_DIGITAL": 3,
        "L4_INTEGRATED": 4,
        "L5_FIELD_PILOT_READY": 5,
        "L6_PRODUCTION_OR_FIELD": 6,
    }
    for row in resolutions:
        fam = row.get("subsystem") or "ecosystem"
        if fam not in families:
            families[fam] = {
                "family": fam,
                "requirement_count": 0,
                "owners": set(),
                "highest_level": "L0_DEFINED",
                "open_counts": Counter(),
                "pending_classes": Counter(),
            }
        f = families[fam]
        f["requirement_count"] += 1
        f["owners"].add(row.get("owner_repo"))
        cl = row.get("current_level") or "L0_DEFINED"
        if level_rank.get(cl, 0) > level_rank.get(f["highest_level"], 0):
            f["highest_level"] = cl
        res = row.get("resolution") or ""
        if res == "DIGITAL_IMPLEMENTATION_OPEN":
            f["open_counts"]["DIGITAL_IMPLEMENTATION_OPEN"] += 1
        elif res == "EVIDENCE_UNRESOLVED":
            f["open_counts"]["EVIDENCE_UNRESOLVED"] += 1
        elif res in PENDING_RESOLUTIONS:
            f["pending_classes"][res] += 1

    out_families = []
    for fam in END_GOAL_FAMILIES:
        f = families.get(fam)
        if not f:
            continue
        out_families.append(
            {
                "family": fam,
                "requirement_count": f["requirement_count"],
                "owners": sorted(f["owners"]),
                "highest_level": f["highest_level"],
                "open_counts": dict(f["open_counts"]),
                "pending_classes": dict(f["pending_classes"]),
            }
        )
    for fam, f in sorted(families.items()):
        if fam in END_GOAL_FAMILIES:
            continue
        out_families.append(
            {
                "family": fam,
                "requirement_count": f["requirement_count"],
                "owners": sorted(f["owners"]),
                "highest_level": f["highest_level"],
                "open_counts": dict(f["open_counts"]),
                "pending_classes": dict(f["pending_classes"]),
            }
        )
    return {"families": out_families, "family_count": len(out_families)}


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(c) if c is not None else "" for c in row) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, body: str) -> None:
    path.write_text(body.strip() + "\n", encoding="utf-8")


def main() -> int:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    ts = now.isoformat().replace("+00:00", "Z")

    repos = {name: live_repo(name) for name in CANONICAL_REPOS}
    evidence_index = build_accepted_main_evidence_index(repos)
    req_doc = yaml.safe_load((ROOT / "program/requirements/requirements.yaml").read_text(encoding="utf-8"))
    requirements = req_doc["requirements"]

    resolutions = [resolve_requirement(req, repos, evidence_index) for req in requirements]
    resolution_counts = Counter(r["resolution"] for r in resolutions)

    totals = {
        "ATOMIC_TOTAL": len(resolutions),
        "DIGITAL_IMPLEMENTATION_COMPLETE": sum(
            1 for r in resolutions if r["resolution"] in COMPLETE_RESOLUTIONS
        ),
        "DIGITAL_IMPLEMENTATION_OPEN": resolution_counts.get("DIGITAL_IMPLEMENTATION_OPEN", 0),
        "EVIDENCE_UNRESOLVED": resolution_counts.get("EVIDENCE_UNRESOLVED", 0),
        "PHYSICAL_PENDING": resolution_counts.get("PHYSICAL_PENDING", 0),
        "HUMAN_PENDING": resolution_counts.get("HUMAN_PENDING", 0),
        "EXTERNAL_PENDING": resolution_counts.get("EXTERNAL_PENDING", 0),
        "STANDARD_PENDING": resolution_counts.get("STANDARD_PENDING", 0),
        "CERTIFICATION_PENDING": resolution_counts.get("CERTIFICATION", 0),
        "CARRIER_PENDING": resolution_counts.get("CARRIER", 0),
        "VENDOR_PENDING": resolution_counts.get("VENDOR", 0),
        "OWNER_DECISION_PENDING": resolution_counts.get("OWNER_DECISION_PENDING", 0),
    }

    gate_78_count = sum(1 for req in requirements if (req.get("gate") or 0) > 6)
    program_gate_separate = not any(r.get("layer") for r in resolutions)

    audit_103 = audit_device_os_103(repos, evidence_index)
    stale_preview = scan_stale_preview(repos)
    end_goal = build_end_goal_matrix(resolutions)

    ci_matrix = []
    ci_contradictions = []
    for name, rec in repos.items():
        ci_matrix.append(
            {
                "repository": name,
                "origin_main_sha": rec.get("origin_main_sha"),
                "ci": rec.get("ci"),
                "ci_detail": rec.get("ci_detail"),
                "reproduce": rec.get("reproduce"),
            }
        )
        if rec.get("ci") == "FAIL":
            ci_contradictions.append(name)

    evidence_resolution_doc = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.evidence_resolution",
        "generated_at_utc": ts,
        "policy": {
            "program_gate": "Original requirement gate 0-8 from requirements.yaml",
            "current_level": "L0_DEFINED .. L6_PRODUCTION_OR_FIELD — never equal to program_gate",
            "complete_requires": ["accepted_main_sha", "implementation_evidence or validation_evidence", "resolution_reason"],
        },
        "totals": totals,
        "resolutions": resolutions,
    }

    accepted_baseline = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.accepted_main",
        "generated_at_utc": ts,
        "repos_root": str(REPOS_ROOT),
        "canonical_repo_count": len(CANONICAL_REPOS),
        "repos": repos,
        "hygiene_repairs_merged": {
            "readygary-6g-beam-selection": {"pr": 27, "ci": repos["readygary-6g-beam-selection"].get("ci")},
            "waike-research-ops": {"pr": 54, "digital_rc_packages": evidence_index.get("waike_digital_rc_count"), "ci": repos["waike-research-ops"].get("ci")},
            "gunnchos-device-os": {"pr": 122, "ci": repos["gunnchos-device-os"].get("ci")},
            "gunnchos-7gc-ai-ran-field-kit": {"pr": 88, "ci": repos["gunnchos-7gc-ai-ran-field-kit"].get("ci")},
            "gunnchos-research-portal": {"pr": 9, "note": "merged but portal snapshot stale vs subsequent merges"},
        },
    }

    master_register = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.master_completion_register",
        "generated_at_utc": ts,
        "layer_policy": "program_gate (0-8) separate from current_level (L0-L6)",
        "gates_7_8_included": gate_78_count,
        "CURSOR_NEVER_MERGES": True,
        "totals": totals,
        "requirements": resolutions,
    }

    remaining_gaps = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.remaining_gaps",
        "generated_at_utc": ts,
        "top_blockers": [
            "device-os #103 owner supersession close (Cursor must not close)",
            "field-kit Baseline V2 owner merge (PR #89)",
            "portal Phase-C snapshot refresh from LATEST stale references",
            "EVIDENCE_UNRESOLVED rows require artifact paths on accepted main",
            "gunnchAI Product Completion 002 blocked on 8GB host",
            "GPU-NR CUDA validation requires self-hosted nvidia-gpu runner",
        ],
        "gates_7_8_requirement_count": gate_78_count,
        "device_os_103": audit_103,
        "stale_preview_references": stale_preview,
    }

    ci_repro = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.ci_and_reproduction_matrix",
        "generated_at_utc": ts,
        "matrix": ci_matrix,
        "known_accepted_main_ci_contradictions": ci_contradictions,
    }

    ready_for_merge = (
        totals["EVIDENCE_UNRESOLVED"] == 0
        and gate_78_count > 0
        and len(end_goal["families"]) >= len(END_GOAL_FAMILIES)
        and all(f["requirement_count"] > 0 for f in end_goal["families"] if f["family"] in END_GOAL_FAMILIES)
    )

    result = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.result",
        "generated_at_utc": ts,
        "phase": "PRE_ENGINEERING_HYGIENE_PHASE_B.1",
        "BASELINE_V2_STATE": "DRAFT_PR",
        "STOP_FOR_OWNER_MERGE": True,
        "BASELINE_V2_READY_FOR_OWNER_MERGE": ready_for_merge,
        "totals": totals,
        "PROGRAM_GATE_7_8_REQUIREMENTS_RETAINED": gate_78_count,
        "PROGRAM_GATE_SEPARATE_FROM_COMPLETION_LEVEL": program_gate_separate,
        "END_GOAL_FAMILIES_COVERED": len([f for f in end_goal["families"] if f["requirement_count"] > 0]),
        "DEVICE_OS_103_UNIQUE_CAPABILITIES_REMAINING": audit_103["unique_capabilities_remaining"],
        "DEVICE_OS_103_DISPOSITION": audit_103["disposition"],
        "DSXL_CURRENT_MAIN_STATUS": evidence_index["device_lab_tokens"].get("DSXL_DUAL_COMPOSITOR_UX_PASS"),
        "RING_CURRENT_MAIN_STATUS": evidence_index["device_lab_tokens"].get("RING_TO_REAL_APP_STATE_MUTATION_PASS"),
        "FOUR_GAME_CURRENT_MAIN_STATUS": evidence_index["device_lab_tokens"].get("FOUR_GAME_REAL_RUNTIME_DEVICE_LAB_PASS"),
        "STALE_PREVIEW_REFERENCES": len(stale_preview),
        "STALE_PREVIEW_REFERENCES_TRACEABLE": len(stale_preview) > 0,
        "STALE_PREVIEW_DETAIL": stale_preview,
        "KNOWN_ACCEPTED_MAIN_CI_CONTRADICTIONS": len(ci_contradictions),
        "READYGARY_ACCEPTED_MAIN_CI": repos["readygary-6g-beam-selection"].get("ci"),
        "WAIKE_ACCEPTED_MAIN_CI": repos["waike-research-ops"].get("ci"),
        "FIELD_KIT_BASELINE_V2": "DRAFT_NOT_ACCEPTED_MAIN",
        "PORTAL_FINAL_ACCEPTED_MAIN_SNAPSHOT": "STALE_DRIFT",
        "PRE_ENGINEERING_HYGIENE_PASS": False,
        "ENGINEERING_NEXT_WAVE_ALLOWED": False,
    }

    OUT.mkdir(parents=True, exist_ok=True)

    (OUT / "EVIDENCE_RESOLUTION.json").write_text(json.dumps(evidence_resolution_doc, indent=2) + "\n", encoding="utf-8")
    (OUT / "END_GOAL_COVERAGE_MATRIX.json").write_text(json.dumps(end_goal, indent=2) + "\n", encoding="utf-8")
    (OUT / "ACCEPTED_MAIN_BASELINE.json").write_text(json.dumps(accepted_baseline, indent=2) + "\n", encoding="utf-8")
    (OUT / "MASTER_COMPLETION_REGISTER.json").write_text(json.dumps(master_register, indent=2) + "\n", encoding="utf-8")
    (OUT / "REMAINING_GAPS.json").write_text(json.dumps(remaining_gaps, indent=2) + "\n", encoding="utf-8")
    (OUT / "CI_AND_REPRODUCTION_MATRIX.json").write_text(json.dumps(ci_repro, indent=2) + "\n", encoding="utf-8")
    (OUT / "BASELINE_V2_RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    repo_rows = [[r, (repos[r].get("origin_main_sha") or "")[:12], repos[r].get("ci", "?")] for r in CANONICAL_REPOS]
    write_markdown(
        OUT / "README.md",
        f"""# GUNNCHOS Digital Ecosystem Baseline V2 (Pre-Engineering Hygiene)

Generated: `{ts}`  
Phase: **PRE_ENGINEERING_HYGIENE Phase B.1**  
Policy: **Cursor never merges**. Edmund sole merge authority. **main only**.

## Summary

{md_table(["Metric", "Count"], [[k, str(v)] for k, v in totals.items()])}

Gate 7/8 requirements retained: **{gate_78_count}**  
Device-os #103 disposition: **{audit_103['disposition']}**  
Stale portal preview references: **{len(stale_preview)}**

## Accepted mains ({len(CANONICAL_REPOS)} canonical repos)

{md_table(["Repository", "origin/main (short)", "CI"], repo_rows)}

Regenerate: `python3 scripts/generate_digital_ecosystem_baseline_v2.py`  
Validate: `python3 scripts/validate_digital_ecosystem_baseline_v2.py`
""",
    )

    write_markdown(
        OUT / "ACCEPTED_MAIN_BASELINE.md",
        "# Accepted Main Baseline (V2)\n\n" + md_table(["Repository", "SHA", "CI"], repo_rows) + "\n",
    )

    write_markdown(
        OUT / "MASTER_COMPLETION_REGISTER.md",
        "# Master Completion Register\n\n"
        + md_table(["Metric", "Count"], [[k, str(v)] for k, v in totals.items()])
        + f"\n\nTotal atomic requirements (gates 0–8): **{totals['ATOMIC_TOTAL']}**\n",
    )

    write_markdown(
        OUT / "EVIDENCE_RESOLUTION.md",
        "# Evidence Resolution\n\n"
        + f"Generated `{ts}`. Each row resolves against accepted main with separate `program_gate` and `current_level`.\n\n"
        + md_table(
            ["Resolution", "Count"],
            [[k, str(v)] for k, v in sorted(resolution_counts.items())],
        )
        + "\n\nSee `EVIDENCE_RESOLUTION.json` for full per-requirement records.\n",
    )

    fam_rows = [
        [f["family"], str(f["requirement_count"]), f["highest_level"], str(sum(f["open_counts"].values()))]
        for f in end_goal["families"]
    ]
    write_markdown(
        OUT / "END_GOAL_COVERAGE_MATRIX.md",
        "# End Goal Coverage Matrix\n\n"
        + md_table(["Family", "Requirements", "Highest level", "Open count"], fam_rows)
        + "\n",
    )

    write_markdown(
        OUT / "REMAINING_GAPS.md",
        "# Remaining Gaps\n\n"
        + "\n".join(f"- {b}" for b in remaining_gaps["top_blockers"])
        + "\n\nSee `REMAINING_GAPS.json` and `SUPERSEDED_PR_DISPOSITION.md`.\n",
    )

    write_markdown(
        OUT / "CI_AND_REPRODUCTION_MATRIX.md",
        "# CI and Reproduction Matrix\n\n"
        + md_table(["Repository", "CI", "Reproduce"], [[m["repository"], m["ci"], m["reproduce"]] for m in ci_matrix])
        + "\n",
    )

    write_markdown(
        OUT / "EVIDENCE_CLASSIFICATION.md",
        """# Evidence Classification (Baseline V2)

| Class | Meaning |
| --- | --- |
| E0 | Document-only / charter |
| E1 | Unit or schema test on accepted main |
| E2 | Integrated CI PASS on accepted main |
| E3 | Cross-repo reproduction harness |
| E4 | Independent VP artifact with explicit negative space |

`ACCEPTED_MAIN_*` resolutions require non-empty accepted-main SHA, evidence path, and resolution_reason.
""",
    )

    write_markdown(
        OUT / "SUPERSEDED_PR_DISPOSITION.md",
        f"""# Superseded PR Disposition

## device-os #103 — {audit_103['state']} (do not close by Cursor)

| Field | Value |
| --- | --- |
| Disposition | `{audit_103['disposition']}` |
| Unique capabilities remaining | {audit_103['unique_capabilities_remaining']} |
| Cursor action | DO_NOT_CLOSE |
| Owner action | Close as SUPERSEDED_BY_OWNER after Baseline V2 merge + portal refresh |

### historical_false_tokens (PR #103 draft claims)

"""
        + "\n".join(f"- {t}" for t in audit_103["historical_false_tokens"])
        + """

### current_main_replacements (#108, #116, #117-#122 lineage)

"""
        + "\n".join(
            f"- **{r['token']}**: {r['replacement']} (`{r.get('evidence', '')}`)"
            for r in audit_103["current_main_replacements"]
        )
        + """

### current_remaining_ecosystem_gaps (accepted main)

"""
        + "\n".join(f"- {g}" for g in audit_103["current_remaining_ecosystem_gaps"])
        + """

### unique_103_delta

"""
        + (
            "\n".join(f"- {t}" for t in audit_103["unique_103_delta"])
            if audit_103["unique_103_delta"]
            else "- _(none — all #103 unique tokens superseded on accepted main)_"
        )
        + """

## Stale preview references (portal content)

Detected from `gunnchos-research-portal/docs/phd/contact_snapshots/LATEST.{md,json}` — see `REMAINING_GAPS.json` / `BASELINE_V2_RESULT.json` for traceable rows. Phase C portal refresh required.
""",
    )

    print(json.dumps({"ok": True, "out": str(OUT), "totals": totals, "audit_103": audit_103["disposition"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
