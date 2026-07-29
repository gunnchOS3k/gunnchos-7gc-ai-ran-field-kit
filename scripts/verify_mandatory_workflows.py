#!/usr/bin/env python3
"""Verify mandatory field-kit workflows succeeded for an accepted commit.

Fail closed on skipped / cancelled / missing / stale / pending mandatory workflows.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANDATORY = [
    "Gate 2 Integrated System",
    "Application readiness CI",
    "Gate 3 Evidence Readiness",
    "Gate 4 Evaluation Readiness",
    "Umbrella Artifact CI",
]

# Map workflow display names → dependency graph keys
NAME_TO_KEY = {
    "Gate 2 Integrated System": "gate2_integrated_system",
    "Application readiness CI": "application_readiness",
    "Gate 3 Evidence Readiness": "gate3_evidence_readiness",
    "Gate 4 Evaluation Readiness": "gate4_evaluation_readiness",
    "Umbrella Artifact CI": "umbrella_artifact_ci",
}


def evaluate(runs: list[dict], *, accepted_sha: str) -> dict:
    """runs: [{name, head_sha, conclusion, status, html_url, database_id}]"""
    by_name: dict[str, dict] = {}
    for run in runs:
        name = run.get("name") or run.get("workflow_name")
        if name not in MANDATORY:
            continue
        # Prefer newest matching accepted sha
        if run.get("head_sha") != accepted_sha:
            continue
        prev = by_name.get(name)
        if prev is None or int(run.get("database_id") or 0) > int(prev.get("database_id") or 0):
            by_name[name] = run

    failures = []
    details = {}
    for name in MANDATORY:
        key = NAME_TO_KEY[name]
        run = by_name.get(name)
        if run is None:
            failures.append(name)
            details[key] = {
                "status": "missing",
                "conclusion": None,
                "error": "missing_mandatory_workflow_for_accepted_sha",
            }
            continue
        status = (run.get("status") or "").lower()
        conclusion = (run.get("conclusion") or "").lower()
        entry = {
            "run_id": run.get("database_id"),
            "url": run.get("html_url"),
            "head_sha": run.get("head_sha"),
            "status": status,
            "conclusion": conclusion,
        }
        details[key] = entry
        if status in ("queued", "in_progress", "pending", "waiting"):
            failures.append(name)
            entry["error"] = "still_running"
        elif conclusion in ("skipped", "cancelled", "canceled", "startup_failure", "timed_out"):
            failures.append(name)
            entry["error"] = f"invalid_conclusion:{conclusion}"
        elif conclusion != "success":
            failures.append(name)
            entry["error"] = f"not_success:{conclusion}"

    ok = not failures
    return {
        "ok": ok,
        "accepted_sha": accepted_sha,
        "failures": failures,
        "workflows": details,
        "status": "CONTROL_PLANE_REMOTE_CI_PASS" if ok else "CONTROL_PLANE_IMPLEMENTED_BUT_REMOTE_CI_RED",
        "rule": "all five mandatory workflows must succeed on the same accepted commit",
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--accepted-sha", default=os.environ.get("GITHUB_SHA") or "")
    p.add_argument("--runs-json", default=None, help="Path to gh run list JSON dump")
    p.add_argument("--output", default=str(ROOT / "orchestration/gates_4_6/mandatory_workflow_status.json"))
    args = p.parse_args(argv)
    if not args.accepted_sha:
        print(json.dumps({"ok": False, "error": "accepted_sha_required"}, indent=2))
        return 2
    runs: list[dict] = []
    if args.runs_json:
        runs = json.loads(Path(args.runs_json).read_text())
        if isinstance(runs, dict) and "workflow_runs" in runs:
            runs = runs["workflow_runs"]
    else:
        # Local/CI without dump → fail closed unless explicitly empty file provided
        print(
            json.dumps(
                {
                    "ok": False,
                    "status": "CONTROL_PLANE_IMPLEMENTED_BUT_REMOTE_CI_RED",
                    "error": "runs_json_required",
                    "note": "Pass --runs-json from `gh run list --json ...` for the accepted SHA",
                },
                indent=2,
            )
        )
        return 2
    result = evaluate(runs, accepted_sha=args.accepted_sha)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
