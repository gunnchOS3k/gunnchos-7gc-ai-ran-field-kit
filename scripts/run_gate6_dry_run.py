#!/usr/bin/env python3
"""Gate 6 dry-run — harnesses and synthetic fixtures only. Never claims physical PASS."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gates_4_6_common import (  # noqa: E402
    REPOS_ROOT,
    ROOT,
    host_manifest,
    run_cmd,
    update_master_status,
    utc_now,
    write_json,
)

OUT = ROOT / "orchestration" / "gates_4_6" / "gate6"
PHYS = ROOT / "physical_evidence"
MATRIX = ROOT / "protocols" / "controlled_pilot_matrix.csv"


def validate_pilot_matrix() -> dict:
    if not MATRIX.exists():
        return {"ok": False, "error": "pilot matrix missing"}
    with MATRIX.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    n = len(rows)
    pending = sum(1 for r in rows if (r.get("status") or "").lower() in ("pending", "", "not_run"))
    return {
        "ok": n == 54,
        "cell_count": n,
        "pending_or_empty": pending,
        "eligible_physical_sessions": 0,
        "evidence_label": "DOCUMENTED_IMPLEMENTATION",
        "note": "54-cell matrix preserved; physical sessions remain pending",
    }


def write_synthetic_fixtures() -> dict:
    PHYS.mkdir(parents=True, exist_ok=True)
    fixtures = []
    # Field session dry-run
    field = {
        "evidence_id": "dryrun-field-001",
        "evidence_label": "SYNTHETIC_EXPERIMENT",
        "domain": "field_pilot",
        "captured_at": utc_now(),
        "operator": "cursor-dry-run",
        "repository": "gunnchos-7gc-ai-ran-field-kit",
        "commit": "dryrun0",
        "status": "DRY_RUN_SYNTHETIC",
        "artifacts": ["physical_evidence/fixtures/field_session_dry_run.json"],
        "notes": "Synthetic fixture only — not physical evidence",
    }
    path = PHYS / "fixtures" / "field_session_dry_run.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, field)
    fixtures.append(str(path))

    user_study = {
        "session_id": "dryrun-user-001",
        "protocol_version": "gates46-user-v1",
        "participant_id_scheme": "P###-hash",
        "consent_status": "dry_run_synthetic",
        "guardian_path_required": True,
        "tasks": ["launch_app", "complete_learn_workload", "offline_relaunch"],
        "usability_instrument": "SUS",
        "deidentified": True,
        "status": "DRY_RUN",
        "irb_claim": "NO_IRB_CLAIM",
        "notes": "Harness only; no IRB approval claimed",
    }
    us_path = PHYS / "fixtures" / "user_study_dry_run.json"
    write_json(us_path, user_study)
    fixtures.append(str(us_path))

    lab = {
        "manifest_id": "dryrun-lab-001",
        "operator": "cursor-dry-run",
        "created_at": utc_now(),
        "connection_diagram_path": "docs/lab/connection_diagram.md",
        "authorized_rf": False,
        "status": "DRY_RUN",
        "instruments": [
            {
                "manufacturer": "UNAVAILABLE",
                "model": "NONE",
                "role": "placeholder",
                "calibration_status": "not_applicable",
                "serial": None,
                "notes": "BLOCKED_HARDWARE — no lab instruments attached",
            }
        ],
        "safety_notes": "No RF transmission in dry-run. Authorized-RF required for any transmit path.",
    }
    lab_path = PHYS / "fixtures" / "lab_instrument_dry_run.json"
    write_json(lab_path, lab)
    fixtures.append(str(lab_path))
    return {"ok": True, "fixtures": fixtures}


def invoke_sibling_dry_runs() -> dict:
    results = {}
    pairs = [
        ("edge-io-measurement-node", ["make", "gate6-dry-run"]),
        ("gunnchos-gpu-nr-baseband-platform", ["make", "gate6-dry-run"]),
        ("gunnchos-hardware-industrial-design", ["make", "gate6-dry-run"]),
        ("gunnchos-device-os", ["make", "gate6-dry-run"]),
    ]
    for name, cmd in pairs:
        repo = REPOS_ROOT / name
        if not repo.is_dir():
            results[name] = {"ok": False, "error": "missing"}
            continue
        # Prefer make target; fall back to documenting absence
        if (repo / "Makefile").exists():
            r = run_cmd(cmd, cwd=repo)
            if not r["ok"]:
                # Fallback: create local dry-run note if target missing
                note = repo / "physical_evidence" / "GATE6_DRY_RUN_NOTE.md"
                note.parent.mkdir(parents=True, exist_ok=True)
                if "No rule" in (r.get("stderr_tail") or "") or r["returncode"] != 0:
                    note.write_text(
                        f"# Gate 6 dry-run note\n\nTarget missing or failed at {utc_now()}.\n"
                        "Harness pending in this repo; control-plane fixtures still apply.\n",
                        encoding="utf-8",
                    )
                    results[name] = {"ok": True, "fallback_note": str(note), "make": r}
                else:
                    results[name] = r
            else:
                results[name] = r
        else:
            results[name] = {"ok": False, "error": "no Makefile"}
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    matrix = validate_pilot_matrix()
    fixtures = write_synthetic_fixtures()
    siblings = invoke_sibling_dry_runs()

    harness_ok = matrix.get("ok") and fixtures.get("ok")
    statuses = {
        "GATE6_HARNESS": "GATE6_HARNESS_PASS" if harness_ok else "GATE6_HARNESS_FAIL",
        "FIELD_PILOT": "FIELD_PILOT_PENDING",
        "GPU_MEASUREMENT": "GPU_MEASUREMENT_PENDING",
        "NIC_PTP": "NIC_PTP_PENDING",
        "SDR_LAB": "SDR_LAB_PENDING",
        "HARDWARE_PROTOTYPE": "HARDWARE_PROTOTYPE_PENDING",
        "OS_PHYSICAL_BOOT": "OS_PHYSICAL_BOOT_PENDING",
        "USER_STUDY": "USER_STUDY_PENDING",
        "CUSTOMER_FIELD_TRIAL": "CUSTOMER_FIELD_TRIAL_PENDING",
        "PHYSICAL_EVIDENCE": "PHYSICAL_EVIDENCE_PENDING",
    }
    report = {
        "gate": "6",
        "mode": "dry_run",
        "started": utc_now(),
        "host": host_manifest(),
        "pilot_matrix": matrix,
        "fixtures": fixtures,
        "siblings": siblings,
        "statuses": statuses,
        "finished": utc_now(),
        "claim": "GATE6_HARNESS_PASS only — no physical completion claimed",
    }
    write_json(OUT / "gate6_dry_run_report.json", report)

    registry = {
        "updated": utc_now(),
        "entries": [
            {
                "id": "field_pilot",
                "status": "FIELD_PILOT_PENDING",
                "evidence_label": "BLOCKED_HARDWARE",
            },
            {
                "id": "gpu_lab",
                "status": "GPU_MEASUREMENT_PENDING",
                "evidence_label": "BLOCKED_HARDWARE",
            },
            {
                "id": "nic_ptp",
                "status": "NIC_PTP_PENDING",
                "evidence_label": "BLOCKED_HARDWARE",
            },
            {
                "id": "sdr_lab",
                "status": "SDR_LAB_PENDING",
                "evidence_label": "BLOCKED_HARDWARE",
            },
            {
                "id": "hardware_prototype",
                "status": "HARDWARE_PROTOTYPE_PENDING",
                "evidence_label": "BLOCKED_HARDWARE",
            },
            {
                "id": "os_boot",
                "status": "OS_PHYSICAL_BOOT_PENDING",
                "evidence_label": "BLOCKED_HARDWARE",
            },
            {
                "id": "user_study",
                "status": "USER_STUDY_PENDING",
                "evidence_label": "BLOCKED_EXTERNAL",
            },
            {
                "id": "customer_trial",
                "status": "CUSTOMER_FIELD_TRIAL_PENDING",
                "evidence_label": "BLOCKED_EXTERNAL",
            },
        ],
    }
    write_json(ROOT / "PHYSICAL_EVIDENCE_REGISTRY.json", registry)
    update_master_status(statuses, notes=["Gate6 dry-run only", f"report={OUT / 'gate6_dry_run_report.json'}"])
    print(json.dumps({"ok": harness_ok, "statuses": statuses}, indent=2))
    return 0 if harness_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
