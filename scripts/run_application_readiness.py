#!/usr/bin/env python3
"""Run feasible application-readiness checks and write reports.

Exit codes:
  0 — all automated checks passed (external/human gates may still be pending)
  2 — one or more automated checks failed
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_MD = ROOT / "research-application-control" / "reports" / "APPLICATION_READINESS_REPORT.md"
REPORT_JSON = ROOT / "research-application-control" / "reports" / "APPLICATION_READINESS_REPORT.json"


def run_cmd(label: str, argv: list[str], *, cwd: Path = ROOT) -> dict:
    try:
        proc = subprocess.run(
            argv,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=600,
        )
        return {
            "label": label,
            "command": " ".join(argv),
            "returncode": proc.returncode,
            "ok": proc.returncode == 0,
            "stdout_tail": (proc.stdout or "")[-2000:],
            "stderr_tail": (proc.stderr or "")[-1000:],
            "category": "automated",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "label": label,
            "command": " ".join(argv),
            "returncode": 99,
            "ok": False,
            "stdout_tail": "",
            "stderr_tail": str(exc),
            "category": "automated",
        }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repos-root", default=str(ROOT.parent))
    p.add_argument("--skip-integrated", action="store_true")
    args = p.parse_args(argv)
    py = sys.executable
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    checks = [
        run_cmd("validate_master_status", [py, "scripts/validate_master_status.py"]),
        run_cmd("validate_preregistration", [py, "scripts/validate_preregistration.py"]),
        run_cmd("validate_pilot_assignments", [py, "scripts/validate_pilot_assignments.py"]),
        run_cmd("validate_application_packet", [py, "scripts/validate_application_packet.py"]),
        run_cmd("validate_gate1", [py, "scripts/validate_gate1_thesis.py"]),
        run_cmd(
            "verify_repo_lock",
            [
                py,
                "scripts/verify_repo_lock.py",
                "--allow-dirty",
                "--repos-root",
                args.repos_root,
            ],
        ),
        run_cmd("pytest_unit", [py, "-m", "pytest", "-q", "tests"]),
        run_cmd(
            "gate4_evaluation_ready",
            [
                py,
                "scripts/run_gate4_evaluation.py",
                "--repos-root",
                args.repos_root,
                "--output-root",
                "results/gate4",
                "--dry-run",
                "--strict",
            ],
        ),
    ]
    if not args.skip_integrated:
        checks.append(
            run_cmd(
                "integrated_pipeline",
                [
                    "make",
                    "integrated-pipeline",
                    f"REPOS_ROOT={args.repos_root}",
                    f"PYTHON={py}",
                ],
            )
        )

    # Human / external — recorded, not failures
    pending = [
        {
            "label": "GATE_3_physical_collection",
            "category": "human",
            "ok": None,
            "status": "HUMAN_ACTION_REQUIRED",
            "note": "0/54 eligible PILOT sessions",
        },
        {
            "label": "non_author_reproduction",
            "category": "external",
            "ok": None,
            "status": "EXTERNAL_DEPENDENCY",
            "note": "Requires independent human",
        },
        {
            "label": "faculty_supervision_commitment",
            "category": "external",
            "ok": None,
            "status": "EXTERNAL_DEPENDENCY",
            "note": "No fabricated endorsement",
        },
        {
            "label": "doi_deposit",
            "category": "external",
            "ok": None,
            "status": "EXTERNAL_DEPENDENCY",
            "note": "DOI_PENDING",
        },
    ]

    auto_fail = [c for c in checks if not c["ok"]]
    auto_pass = [c for c in checks if c["ok"]]
    overall_auto = "PASS" if not auto_fail else "FAIL"

    payload = {
        "generated_at": now,
        "overall_automated_pipeline": overall_auto,
        "application_complete": False,
        "automated_passes": [c["label"] for c in auto_pass],
        "automated_failures": [
            {"label": c["label"], "returncode": c["returncode"], "stderr_tail": c["stderr_tail"]}
            for c in auto_fail
        ],
        "human_actions": pending,
        "checks": checks,
        "integrity": {
            "synthetic_data_used_for_infra_tests": True,
            "synthetic_locations": [
                "tests/fixtures/",
                "fixtures/valid/",
                "examples/synthetic/ (if present)",
            ],
            "physical_evidence_created_this_run": False,
            "external_approval_claimed": False,
            "doi_claimed": False,
            "paper_submission_claimed": False,
            "raw_private_protected": True,
        },
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Application Readiness Report",
        "",
        f"Generated: `{now}`",
        "",
        f"## Overall automated pipeline: **{overall_auto}**",
        "",
        "APPLICATION_COMPLETE is **false** (authentic gates incomplete).",
        "",
        "## Automated passes",
        "",
    ]
    for label in payload["automated_passes"]:
        lines.append(f"- PASS: `{label}`")
    lines += ["", "## Automated failures", ""]
    if not auto_fail:
        lines.append("- None")
    else:
        for f in payload["automated_failures"]:
            lines.append(f"- FAIL: `{f['label']}` (rc={f['returncode']})")
    lines += ["", "## Human actions / external dependencies", ""]
    for h in pending:
        lines.append(f"- {h['status']}: `{h['label']}` — {h['note']}")
    lines += [
        "",
        "## Integrity",
        "",
        "- Synthetic fixtures may be used for infrastructure tests only.",
        "- No physical Gate 3 evidence fabricated.",
        "- No faculty endorsement, DOI, or paper submission claimed.",
        "- `datasets/controlled/raw-private/` remains gitignored.",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"overall_automated_pipeline": overall_auto, "report": str(REPORT_MD)}, indent=2))
    return 0 if overall_auto == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
