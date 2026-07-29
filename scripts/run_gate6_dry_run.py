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


REQUIRED_SIBLINGS = (
    "gunnchos-7gc-ai-ran-field-kit",
    "edge-io-measurement-node",
    "gunnchos-gpu-nr-baseband-platform",
    "gunnchos-hardware-industrial-design",
    "gunnchos-device-os",
)


def _validate_sibling_report(repo: Path, name: str) -> dict:
    """Fail closed: require a JSON dry-run report with correct evidence labels."""
    candidates = [
        repo / "physical_evidence" / "GATE6_DRY_RUN_REPORT.json",
        repo / "physical_evidence" / "gate6_dry_run_report.json",
        repo / "orchestration" / "gates_4_6" / "gate6" / "gate6_dry_run_report.json",
        repo / "results" / "gate6" / "gate6_dry_run_report.json",
        repo / "results" / "gate6" / "GATE6_DRY_RUN_REPORT.json",
    ]
    if name == "gunnchos-7gc-ai-ran-field-kit":
        candidates.insert(0, OUT / "gate6_dry_run_report.json")
        candidates.insert(1, PHYS / "gate6_dry_run_report.json")
        candidates.insert(2, PHYS / "GATE6_DRY_RUN_REPORT.json")
    report_path = next((p for p in candidates if p.is_file()), None)
    if report_path is None:
        return {"ok": False, "error": "missing_required_report", "repository": name}
    try:
        doc = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"ok": False, "error": f"malformed_report: {exc}", "repository": name}

    # Normalize legacy sibling reports into the completion contract.
    normalized = dict(doc)
    if "ok" not in normalized:
        harness = (normalized.get("statuses") or {}).get("GATE6_HARNESS", "")
        nested_ok = True
        for key in ("templates", "fixture", "fixtures", "files", "pilot_matrix"):
            nested = normalized.get(key)
            if isinstance(nested, dict) and "ok" in nested and nested.get("ok") is False:
                nested_ok = False
        normalized["ok"] = nested_ok and harness in (
            "GATE6_HARNESS_PASS",
            "GATE6_PARTIAL_HARNESS_PASS",
        )
    if "mode" not in normalized:
        return {
            "ok": False,
            "error": "missing_required_report_field",
            "fields": ["mode"],
            "path": str(report_path),
        }
    if "evidence_label" not in normalized:
        normalized["evidence_label"] = "SYNTHETIC_EXPERIMENT"
    label = str(normalized.get("evidence_label") or "")
    if label in ("PHYSICAL_PASS", "PHYSICAL_EVIDENCE_PASS", "AUTHENTIC_PHYSICAL"):
        return {
            "ok": False,
            "error": "wrong_evidence_label",
            "evidence_label": label,
            "path": str(report_path),
        }
    if normalized.get("physical_pass") is True:
        return {
            "ok": False,
            "error": "physical_pass_from_dry_run_forbidden",
            "path": str(report_path),
        }
    # Synthetic fixtures claiming physical PASS via status strings
    statuses = normalized.get("statuses") or {}
    for k, v in statuses.items():
        if "PHYSICAL" in str(k).upper() and str(v).endswith("_PASS") and "PENDING" not in str(v):
            if "HARNESS" not in str(k).upper():
                return {
                    "ok": False,
                    "error": "physical_PASS_from_synthetic_fixture",
                    "status_key": k,
                    "status_value": v,
                    "path": str(report_path),
                }
    if not normalized.get("ok"):
        return {
            "ok": False,
            "error": "sibling_report_ok_false",
            "path": str(report_path),
        }
    return {
        "ok": True,
        "path": str(report_path),
        "evidence_label": label,
        "mode": normalized.get("mode"),
    }


def invoke_sibling_dry_runs() -> dict:
    """Fail closed — never convert missing/failed Make targets into ok:true."""
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
            results[name] = {"ok": False, "error": "missing_required_repository"}
            continue
        if not (repo / "Makefile").exists():
            results[name] = {"ok": False, "error": "no Makefile"}
            continue
        r = run_cmd(cmd, cwd=repo)
        if not r.get("ok"):
            results[name] = {
                "ok": False,
                "error": "sibling_make_nonzero_or_missing_target",
                "make": r,
            }
            continue
        report = _validate_sibling_report(repo, name)
        results[name] = {"ok": bool(report.get("ok")), "make": r, "report": report}
    return results


def siblings_ok(siblings: dict) -> bool:
    for name in REQUIRED_SIBLINGS:
        if name == "gunnchos-7gc-ai-ran-field-kit":
            continue  # validated after local report write
        entry = siblings.get(name)
        if not entry or not entry.get("ok"):
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    matrix = validate_pilot_matrix()
    fixtures = write_synthetic_fixtures()
    siblings = invoke_sibling_dry_runs()

    local_body = {
        "ok": bool(matrix.get("ok") and fixtures.get("ok")),
        "mode": "dry_run",
        "evidence_label": "SYNTHETIC_EXPERIMENT",
        "physical_pass": False,
        "gate": "6",
        "pilot_matrix": matrix,
        "fixtures": fixtures,
        "claim": "dry-run harness only",
    }
    write_json(OUT / "gate6_dry_run_report.json", local_body)
    # Also write under physical_evidence for sibling-style discovery.
    write_json(PHYS / "gate6_dry_run_report.json", local_body)
    local_report = _validate_sibling_report(ROOT, "gunnchos-7gc-ai-ran-field-kit")
    siblings["gunnchos-7gc-ai-ran-field-kit"] = {
        "ok": bool(local_report.get("ok")),
        "report": local_report,
    }

    harness_ok = (
        bool(matrix.get("ok"))
        and bool(fixtures.get("ok"))
        and siblings_ok(siblings)
        and bool(local_report.get("ok"))
    )
    statuses = {
        "GATE6_HARNESS": (
            "GATE6_PARTIAL_HARNESS_PASS" if harness_ok else "GATE6_HARNESS_FAIL"
        ),
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
        "ok": harness_ok,
        "gate": "6",
        "mode": "dry_run",
        "evidence_label": "SYNTHETIC_EXPERIMENT",
        "physical_pass": False,
        "started": utc_now(),
        "host": host_manifest(),
        "pilot_matrix": matrix,
        "fixtures": fixtures,
        "siblings": siblings,
        "statuses": statuses,
        "finished": utc_now(),
        "claim": "GATE6_PARTIAL_HARNESS_PASS only when all sibling dry-runs succeed — no physical completion claimed",
    }
    write_json(OUT / "gate6_dry_run_report.json", report)
    write_json(PHYS / "gate6_dry_run_report.json", report)

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
