#!/usr/bin/env python3
"""Generate program/digital_ecosystem_baseline_v2/ from live accepted mains (Phase B.3/B.4)."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from baseline_v2_b4_mapping_convergence import (
    build_sha_freeze,
    validate_b4_mapping,
    write_b4_artifacts,
)
from validate_baseline_v2_b4_register_integrity import main as validate_b41_integrity
from baseline_v2_evidence_census import (
    CANONICAL_REPOS,
    END_GOAL_FAMILIES,
    build_end_goal_matrix,
    build_evidence_index,
    compute_precision_validation,
    compute_totals,
    false_open_report,
    generate_precision_sample_audit,
    index_to_summary,
    load_traceability_maps,
    reconcile_requirement,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "program" / "digital_ecosystem_baseline_v2"
REPOS_ROOT = Path(os.environ.get("REPOS_ROOT", str(ROOT.parent.parent.parent)))
TEMP_ROOT = Path(os.environ.get("BASELINE_V2_TEMP", "/tmp/gunnchos-baseline-v2-evidence"))
PORTAL_ROOT = REPOS_ROOT / "gunnchos-research-portal"

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


def classify_workflow_run(conclusion: str | None, status: str | None) -> str:
    c = (conclusion or "").lower()
    s = (status or "").lower()
    if c == "success":
        return "PASS"
    if c in ("failure", "cancelled", "timed_out", "action_required"):
        return "FAIL"
    if s in ("in_progress", "queued", "waiting", "pending", "requested"):
        return "IN_PROGRESS"
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
    return {"required_workflows": required, "workflows": workflows, "overall": overall}


def live_repo(repo: str, index_shas: dict[str, str]) -> dict[str, Any]:
    path = repo_path(repo)
    sha = index_shas.get(repo, "")
    if path.is_dir() and not sha:
        run(["git", "fetch", "origin", "main"], cwd=path)
        sha = run(["git", "rev-parse", "origin/main"], cwd=path)
    ci_detail = gh_ci_matrix(repo, sha) if sha else {"overall": "UNKNOWN", "required_workflows": [], "workflows": []}
    return {
        "repository": repo,
        "path": str(path),
        "exists": path.is_dir(),
        "origin_main_sha": sha,
        "ci": ci_detail["overall"],
        "ci_detail": ci_detail,
        "reproduce": REPRODUCE_HINT.get(repo, "see REPRODUCIBILITY.md"),
    }


def audit_device_os_103(repos: dict[str, dict], index) -> dict[str, Any]:
    pr103 = gh_json(["gh", "pr", "view", "103", "--repo", "gunnchOS3k/gunnchos-device-os", "--json", "state,isDraft,title"])
    tokens_103_false = [
        "DSXL_DUAL_COMPOSITOR_UX_PASS",
        "RING_TO_REAL_APP_STATE_MUTATION_PASS",
        "GUNNCHDEVICE_LAB_FULL_ECOSYSTEM_DIGITAL_COMPLETE",
    ]
    product_use_path = "artifacts/product_use/PRODUCT_USE_RC_002_STATUS.json"
    main_tokens: dict[str, bool] = {}
    pu = None
    pu_file = repo_path("gunnchos-device-os") / product_use_path
    if pu_file.is_file():
        try:
            pu = json.loads(pu_file.read_text(encoding="utf-8"))
            legs = pu.get("legs") or {}
            main_tokens["DSXL_DUAL_COMPOSITOR_UX_PASS"] = bool((legs.get("G14") or {}).get("DSXL_DUAL_COMPOSITOR_UX_PASS"))
            main_tokens["RING_TO_REAL_APP_STATE_MUTATION_PASS"] = bool(
                (legs.get("RING") or {}).get("RING_TO_REAL_APP_STATE_MUTATION_PASS")
            )
            main_tokens["FOUR_GAME_REAL_RUNTIME_DEVICE_LAB_PASS"] = bool(
                (legs.get("FOUR_GAME") or {}).get("FOUR_GAME_REAL_RUNTIME_DEVICE_LAB_PASS")
            )
        except (json.JSONDecodeError, OSError):
            pass
    replacements = []
    unique_remaining = []
    for tok in tokens_103_false:
        if tok == "GUNNCHDEVICE_LAB_FULL_ECOSYSTEM_DIGITAL_COMPLETE":
            if all(main_tokens.get(t) for t in ("DSXL_DUAL_COMPOSITOR_UX_PASS", "RING_TO_REAL_APP_STATE_MUTATION_PASS", "FOUR_GAME_REAL_RUNTIME_DEVICE_LAB_PASS")):
                replacements.append(
                    {
                        "token": tok,
                        "main_status": "SUPERSEDED",
                        "replacement": "PRODUCT_USE_RC_002 #116 merged — DSXL/RING/FOUR_GAME digital PASS on accepted main",
                        "evidence": product_use_path,
                    }
                )
            else:
                unique_remaining.append(tok)
        elif main_tokens.get(tok):
            replacements.append(
                {
                    "token": tok,
                    "main_status": "PASS",
                    "replacement": f"Accepted main artifact {product_use_path} (#108/#116 lineage)",
                    "evidence": product_use_path,
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
        "cursor_action": "DO_NOT_CLOSE" if (pr103 or {}).get("state") != "CLOSED" else "CLOSED_BY_OWNER_SUPERSEDED",
        "owner_action": "CLOSED_SUPERSEDED_BY_OWNER" if (pr103 or {}).get("state") == "CLOSED" else "CLOSE_SUPERSEDED_BY_OWNER after Baseline V2 merge + portal refresh",
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
                                "phase_c_repair_needed": live_state == "MERGED" or (pr_num == 103 and live_state == "OPEN"),
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
    dedup: dict[tuple, dict] = {}
    for item in stale:
        dedup[(item["file"], item.get("key"), item.get("line"))] = item
    return list(dedup.values())


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(c) if c is not None else "" for c in row) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, body: str) -> None:
    path.write_text(body.strip() + "\n", encoding="utf-8")


def main() -> int:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    ts = now.isoformat().replace("+00:00", "Z")
    phase = os.environ.get("BASELINE_V2_PHASE", "B.3").upper()
    if phase not in ("B.3", "B.4"):
        phase = "B.3"
    phase_label = (
        "PRE_ENGINEERING_HYGIENE_PHASE_B.4.1"
        if phase == "B.4"
        else "PRE_ENGINEERING_HYGIENE_PHASE_B.3"
    )

    print(f"Building accepted-main evidence index (17 repos) phase={phase}...", file=sys.stderr)
    evidence_index = build_evidence_index(REPOS_ROOT, TEMP_ROOT)
    trace_maps, trace_repo_links = load_traceability_maps(ROOT)

    wp012_path = "artifacts/wp012/VP-012-RESULT.json"
    field_kit_sha = evidence_index.repo_shas.get("gunnchos-7gc-ai-ran-field-kit", "")

    req_doc = yaml.safe_load((ROOT / "program/requirements/requirements.yaml").read_text(encoding="utf-8"))
    requirements = req_doc["requirements"]
    req_by_id = {req["id"]: req for req in requirements}

    b3_rows: list[dict[str, Any]] = []
    b3_register_path = OUT / "MASTER_COMPLETION_REGISTER.json"
    if phase == "B.4" and b3_register_path.is_file():
        b3_rows = json.loads(b3_register_path.read_text(encoding="utf-8")).get("requirements") or []

    print(f"Reconciling {len(requirements)} atomic requirements ({phase} precision search)...", file=sys.stderr)
    rows = [
        reconcile_requirement(
            req, evidence_index, trace_maps, trace_repo_links, req_by_id, field_kit_sha, wp012_path, phase=phase,
        )
        for req in requirements
    ]
    totals = compute_totals(rows)
    end_goal = build_end_goal_matrix(rows)
    false_open = false_open_report(rows, evidence_index)
    precision_validation = compute_precision_validation(rows, evidence_index, end_goal)
    precision_audit = generate_precision_sample_audit(rows)

    repos = {name: live_repo(name, evidence_index.repo_shas) for name in CANONICAL_REPOS}
    gate_78_count = sum(1 for req in requirements if (req.get("gate") or 0) > 6)
    audit_103 = audit_device_os_103(repos, evidence_index)
    stale_preview = scan_stale_preview(repos)

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

    work_state_counts = Counter(r["work_state"] for r in rows)
    mapping_complete = totals["EVIDENCE_MAPPING_OPEN"] == 0
    impl_open = totals.get("DIGITAL_IMPLEMENTATION_OPEN", 0)
    val_open = totals.get("DIGITAL_VALIDATION_OPEN", 0)
    ready_for_merge = (
        (phase == "B.4" and mapping_complete)
        or (
            phase == "B.3"
            and totals["EVIDENCE_MAPPING_OPEN"] == 0
        )
    ) and (
        totals.get("LOW_CONFIDENCE_COMPLETE_ROWS", 0) == 0
        and false_open["status"] == "PASS"
        and precision_validation["BASELINE_V2_PRECISION_VALIDATION_PASS"]
        and precision_audit["status"] == "PASS"
        and gate_78_count > 0
        and end_goal["family_count"] == 28
        and all(f["requirement_count"] > 0 for f in end_goal["families"])
    )
    pre_engineering_control_plane_ready = (
        mapping_complete
        and len(evidence_index.repo_shas) >= 17
        and precision_validation["BASELINE_V2_PRECISION_VALIDATION_PASS"]
        and false_open["status"] == "PASS"
    )

    OUT.mkdir(parents=True, exist_ok=True)

    index_summary = index_to_summary(evidence_index)
    index_summary["generated_at_utc"] = ts
    (OUT / "ACCEPTED_MAIN_EVIDENCE_INDEX_SUMMARY.json").write_text(
        json.dumps(index_summary, indent=2) + "\n", encoding="utf-8"
    )
    full_index_path = TEMP_ROOT / "ACCEPTED_MAIN_EVIDENCE_INDEX.full.json"
    full_index_path.parent.mkdir(parents=True, exist_ok=True)
    full_index_path.write_text(
        json.dumps(
            {
                "schema": "gunnchos.digital_ecosystem_baseline_v2.accepted_main_evidence_index.full",
                "generated_at_utc": ts,
                "record_count": len(evidence_index.records),
                "records": [
                    {
                        "repo": r.repo,
                        "path": r.path,
                        "evidence_role": r.evidence_role,
                        "requirement_ids": r.requirement_ids[:10],
                    }
                    for r in evidence_index.records
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    audit_doc = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.requirement_reconciliation_audit",
        "generated_at_utc": ts,
        "phase": phase_label,
        "totals": totals,
        "requirements": rows,
    }
    (OUT / "REQUIREMENT_RECONCILIATION_AUDIT.json").write_text(json.dumps(audit_doc, indent=2) + "\n", encoding="utf-8")

    false_open_doc = {"schema": "gunnchos.digital_ecosystem_baseline_v2.false_open_prevention", "generated_at_utc": ts, **false_open}
    (OUT / "FALSE_OPEN_PREVENTION_REPORT.json").write_text(json.dumps(false_open_doc, indent=2) + "\n", encoding="utf-8")

    evidence_resolution_doc = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.evidence_resolution",
        "generated_at_utc": ts,
        "policy": {
            "program_gate": "Original requirement gate 0-8 from requirements.yaml",
            "current_level": "L0_DEFINED .. L6_PRODUCTION_OR_FIELD",
            "work_state": "Canonical completion vocabulary per Baseline V2 spec sections 3-4",
        },
        "totals": totals,
        "resolutions": rows,
    }
    (OUT / "EVIDENCE_RESOLUTION.json").write_text(json.dumps(evidence_resolution_doc, indent=2) + "\n", encoding="utf-8")
    (OUT / "END_GOAL_COVERAGE_MATRIX.json").write_text(json.dumps(end_goal, indent=2) + "\n", encoding="utf-8")

    accepted_baseline = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.accepted_main",
        "generated_at_utc": ts,
        "repos_root": str(REPOS_ROOT),
        "canonical_repo_count": len(CANONICAL_REPOS),
        "repos": repos,
        "evidence_index_record_count": len(evidence_index.records),
    }
    (OUT / "ACCEPTED_MAIN_BASELINE.json").write_text(json.dumps(accepted_baseline, indent=2) + "\n", encoding="utf-8")

    master_register = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.master_completion_register",
        "generated_at_utc": ts,
        "layer_policy": "program_gate (0-8) separate from current_level (L0-L6)",
        "gates_7_8_included": gate_78_count,
        "CURSOR_NEVER_MERGES": True,
        "totals": totals,
        "requirements": rows,
    }
    (OUT / "MASTER_COMPLETION_REGISTER.json").write_text(json.dumps(master_register, indent=2) + "\n", encoding="utf-8")

    remaining_gaps = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.remaining_gaps",
        "generated_at_utc": ts,
        "top_blockers": [
            "field-kit Baseline V2 B.4 owner merge (draft PR)",
            "portal Phase-C snapshot refresh from LATEST stale references",
            f"DIGITAL_IMPLEMENTATION_OPEN={totals['DIGITAL_IMPLEMENTATION_OPEN']} rows need digital engineering",
            f"DIGITAL_VALIDATION_OPEN={totals['DIGITAL_VALIDATION_OPEN']} rows need verification/reproduction",
            "gunnchAI Product Completion 002 blocked on 8GB host",
            "GPU-NR CUDA validation requires self-hosted nvidia-gpu runner",
        ] if phase == "B.4" else [
            "device-os #103 owner supersession close (Cursor must not close)",
            "field-kit Baseline V2 owner merge (PR #89)",
            "portal Phase-C snapshot refresh from LATEST stale references",
            f"EVIDENCE_MAPPING_OPEN={totals['EVIDENCE_MAPPING_OPEN']} rows need accepted-main evidence paths",
            "gunnchAI Product Completion 002 blocked on 8GB host",
            "GPU-NR CUDA validation requires self-hosted nvidia-gpu runner",
        ],
        "gates_7_8_requirement_count": gate_78_count,
        "device_os_103": audit_103,
        "stale_preview_references": stale_preview,
    }
    (OUT / "REMAINING_GAPS.json").write_text(json.dumps(remaining_gaps, indent=2) + "\n", encoding="utf-8")

    ci_repro = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.ci_and_reproduction_matrix",
        "generated_at_utc": ts,
        "matrix": ci_matrix,
        "known_accepted_main_ci_contradictions": ci_contradictions,
    }
    (OUT / "CI_AND_REPRODUCTION_MATRIX.json").write_text(json.dumps(ci_repro, indent=2) + "\n", encoding="utf-8")

    result = {
        "schema": "gunnchos.digital_ecosystem_baseline_v2.result",
        "generated_at_utc": ts,
        "phase": phase_label,
        "BASELINE_V2_STATE": "DRAFT_PR",
        "STOP_FOR_OWNER_MERGE": True,
        "BASELINE_V2_READY_FOR_OWNER_MERGE": ready_for_merge,
        "BASELINE_V2_B3_PRECISION": "PASS" if precision_validation["BASELINE_V2_PRECISION_VALIDATION_PASS"] else "FAIL",
        "BASELINE_V2_EVIDENCE_CENSUS": "PASS" if false_open["status"] == "PASS" else "FAIL",
        "BASELINE_V2_PRECISION_VALIDATION": precision_validation,
        "PRECISION_SAMPLE_AUDIT": precision_audit["status"],
        "ARTIFACT_BLOAT_STATUS": "SUMMARY_ONLY",
        "totals": totals,
        "PROGRAM_GATE_7_8_REQUIREMENTS_RETAINED": gate_78_count,
        "PROGRAM_GATE_SEPARATE_FROM_COMPLETION_LEVEL": True,
        "END_GOAL_FAMILIES_COVERED": end_goal["family_count"],
        "DEVICE_OS_103_UNIQUE_CAPABILITIES_REMAINING": audit_103["unique_capabilities_remaining"],
        "DEVICE_OS_103_DISPOSITION": audit_103["disposition"],
        "STALE_PREVIEW_REFERENCES": len(stale_preview),
        "STALE_PREVIEW_REFERENCES_TRACEABLE": len(stale_preview) > 0,
        "STALE_PREVIEW_DETAIL": stale_preview,
        "KNOWN_ACCEPTED_MAIN_CI_CONTRADICTIONS": len(ci_contradictions),
        "FALSE_OPEN_SANITY_CHECK": false_open["status"],
        "PRE_ENGINEERING_HYGIENE_PASS": False,
        "ENGINEERING_NEXT_WAVE_ALLOWED": False,
        "work_state_counts": dict(work_state_counts),
        "BASELINE_MAPPING_COMPLETE": mapping_complete,
        "PRE_ENGINEERING_CONTROL_PLANE_READY": pre_engineering_control_plane_ready,
        "ECOSYSTEM_DIGITAL_IMPLEMENTATION_COMPLETE": impl_open == 0,
        "ECOSYSTEM_DIGITAL_VALIDATION_COMPLETE": impl_open == 0 and val_open == 0,
        "USER_READY_DIGITAL_RELEASE_CANDIDATE": totals.get("L3_USER_READY_DIGITAL_RC", 0) > 0,
        "HUMAN_E6_COMPLETE": False,
        "PHYSICAL_VALIDATION_COMPLETE": False,
        "EXTERNAL_CERTIFICATION_COMPLETE": False,
        "SHIPPING_PRODUCT": False,
        "STANDARDIZED_6G": False,
    }
    if phase == "B.4":
        sha_freeze = build_sha_freeze(evidence_index.repo_shas, ts)
        b4_summary = write_b4_artifacts(b3_rows or rows, rows, evidence_index.repo_shas, totals, ts)
        b4_validation = validate_b4_mapping(rows, totals, sha_freeze)
        b41_integrity_rc = validate_b41_integrity()
        b41_integrity_pass = b41_integrity_rc == 0
        result["BASELINE_V2_B4_MAPPING"] = "PASS" if b4_validation["BASELINE_V2_B4_MAPPING_VALIDATION_PASS"] else "FAIL"
        result["BASELINE_V2_B4_MAPPING_VALIDATION"] = b4_validation
        result["BASELINE_V2_B4_1_REGISTER_INTEGRITY"] = "PASS" if b41_integrity_pass else "FAIL"
        result["BASELINE_V2_B4_REGISTER_INTEGRITY_VALIDATION"] = {
            "BASELINE_V2_B4_REGISTER_INTEGRITY_PASS": b41_integrity_pass,
        }
        result["B4_READY_FOR_OWNER_MERGE"] = (
            b4_validation["BASELINE_V2_B4_MAPPING_VALIDATION_PASS"]
            and b41_integrity_pass
            and mapping_complete
            and ready_for_merge
        )
        result["B4_ROWS_PROCESSED"] = b4_summary.get("decisions_count", 0)
        result["B4_MOVED_TO_STATE_COUNTS"] = b4_summary.get("moved_to_state_counts", {})
        result["CANONICAL_REPOS_RECONCILED"] = len([s for s in evidence_index.repo_shas.values() if s]) == 17
    (OUT / "BASELINE_V2_RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    repo_rows = [[r, (repos[r].get("origin_main_sha") or "")[:12], repos[r].get("ci", "?")] for r in CANONICAL_REPOS]
    write_markdown(
        OUT / "README.md",
        f"""# GUNNCHOS Digital Ecosystem Baseline V2 (Pre-Engineering Hygiene)

Generated: `{ts}`  
Phase: **{phase_label.replace('_', ' ')}** ({'evidence-mapping convergence' if phase == 'B.4' else 'precision/provenance correction'})  
Policy: **Cursor never merges**. Edmund sole merge authority. **main only**.

## Summary

{md_table(["Metric", "Count"], [[k, str(v)] for k, v in totals.items() if not k.startswith("L") and "DIMENSION" not in k])}

Evidence index records (local full index): **{len(evidence_index.records)}** — committed summary only  
{'B.4 mapping complete: **' + str(mapping_complete) + '**' if phase == 'B.4' else 'B.3 precision validation: **' + str(precision_validation['BASELINE_V2_PRECISION_VALIDATION_PASS']) + '**'}  
Precision sample audit: **{precision_audit['status']}** ({precision_audit['sample_count']} samples)  
End-goal families: **{end_goal['family_count']}/28**  
False-open sanity: **{false_open['status']}**  
Gate 7/8 requirements retained: **{gate_78_count}**  
Device-os #103 disposition: **{audit_103['disposition']}**

Regenerate: `BASELINE_V2_PHASE={phase} python3 scripts/generate_digital_ecosystem_baseline_v2.py`  
Validate: `python3 scripts/validate_digital_ecosystem_baseline_v2.py`
""",
    )
    write_markdown(
        OUT / "ACCEPTED_MAIN_EVIDENCE_INDEX_SUMMARY.md",
        "# Accepted Main Evidence Index Summary\n\n"
        + f"Full index: **{len(evidence_index.records)}** records (generated locally at `{full_index_path}`; not committed).\n\n"
        + md_table(["Repository", "SHA (short)", "Indexed files"], [
            [r, (evidence_index.repo_shas.get(r) or "")[:12], str(len(evidence_index.by_repo.get(r, [])))]
            for r in CANONICAL_REPOS
        ])
        + "\n\n"
        + md_table(["Evidence role", "Count"], [
            [k, str(v)] for k, v in sorted((index_summary.get("evidence_role_counts") or {}).items())
        ])
        + "\n",
    )
    precision_md = ["# Precision Sample Audit (B.3)\n", f"Status: **{precision_audit['status']}**", f"Samples: **{precision_audit['sample_count']}**", ""]
    for s in precision_audit["samples"][:55]:
        precision_md.append(f"## {s['requirement_id']} — {s['bucket']}")
        precision_md.append(f"- **Family:** {s['primary_family']} | **Owner:** {s['owner']}")
        precision_md.append(f"- **Impl:** `{s['implementation_path'] or 'none'}`")
        precision_md.append(f"- **Verif:** `{s['verification_path'] or 'none'}`")
        precision_md.append(f"- **Level:** {s['current_level']} → target {s['required_target_level']}")
        precision_md.append(f"- **Pending:** {s['pending_dimensions']} | **Confidence:** {s['evidence_confidence']}")
        precision_md.append(f"- **Why correct:** {s['why_correct']}\n")
    write_markdown(OUT / "PRECISION_SAMPLE_AUDIT.md", "\n".join(precision_md))
    (OUT / "PRECISION_SAMPLE_AUDIT.json").write_text(json.dumps(precision_audit, indent=2) + "\n", encoding="utf-8")
    write_markdown(
        OUT / "REQUIREMENT_RECONCILIATION_AUDIT.md",
        "# Requirement Reconciliation Audit\n\n"
        + md_table(["Work state", "Count"], [[k, str(v)] for k, v in sorted(work_state_counts.items())])
        + "\n\nSee `REQUIREMENT_RECONCILIATION_AUDIT.json` for full per-row audit.\n",
    )
    write_markdown(
        OUT / "FALSE_OPEN_PREVENTION_REPORT.md",
        "# False Open Prevention Report\n\n"
        + f"Status: **{false_open['status']}**\n\n"
        + ("\n".join(f"- **{a['check']}** ({a['severity']}): {a['detail']}" for a in false_open["alarms"]) or "- No alarms.")
        + "\n",
    )
    write_markdown(
        OUT / "ACCEPTED_MAIN_BASELINE.md",
        "# Accepted Main Baseline (V2)\n\n" + md_table(["Repository", "SHA", "CI"], repo_rows) + "\n",
    )
    write_markdown(
        OUT / "MASTER_COMPLETION_REGISTER.md",
        "# Master Completion Register\n\n"
        + md_table(["Metric", "Count"], [[k, str(v)] for k, v in totals.items() if not k.startswith("L")])
        + f"\n\nTotal atomic requirements (gates 0–8): **{totals['ATOMIC_TOTAL']}**\n",
    )
    write_markdown(
        OUT / "EVIDENCE_RESOLUTION.md",
        "# Evidence Resolution\n\n"
        + md_table(["Work state", "Count"], [[k, str(v)] for k, v in sorted(work_state_counts.items())])
        + "\n",
    )
    fam_rows = [
        [
            str(f["id"]), f["name"], str(f["requirement_count"]),
            f["max_evidence_level_observed"], f["family_release_level"],
            str(f.get("digital_impl_open", 0)), str(f.get("validation_open", 0)),
        ]
        for f in end_goal["families"]
    ]
    write_markdown(
        OUT / "END_GOAL_COVERAGE_MATRIX.md",
        "# End Goal Coverage Matrix (28 families)\n\n"
        + md_table(
            ["ID", "Family", "Reqs", "Max observed", "Release level", "Impl open", "Val open"],
            fam_rows,
        )
        + "\n",
    )
    write_markdown(
        OUT / "REMAINING_GAPS.md",
        "# Remaining Gaps\n\n" + "\n".join(f"- {b}" for b in remaining_gaps["top_blockers"]) + "\n",
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

Five-pass search precedence: exact ID → tokens → traceability maps → implementation paths → verification tests.
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
| Owner sequence | 1 merge #89 → 2 close #103 → 3 rerun hygiene → 4 Phase C portal |

### current_main_replacements

"""
        + "\n".join(f"- **{r['token']}**: {r['replacement']}" for r in audit_103["current_main_replacements"])
        + "\n",
    )

    print(json.dumps({"ok": True, "totals": totals, "false_open": false_open["status"], "families": end_goal["family_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
