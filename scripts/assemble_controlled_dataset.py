#!/usr/bin/env python3
"""Assemble controlled dataset from sanitized physical sessions only."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_collection_coverage import audit  # noqa: E402
from gate3_common import (  # noqa: E402
    EVIDENCE_PHYSICAL,
    canonical_json_bytes,
    load_json,
    recursive_privacy_scan,
    sha256_bytes,
    sha256_file,
    write_json,
)
from validate_session import validate_session  # noqa: E402


def git_sha(repo: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    except Exception:
        return "0" * 40


def assemble(
    sessions_dir: Path,
    matrix_path: Path,
    output_root: Path,
    contracts_dir: Path,
    repos_root: Path,
) -> dict:
    coverage = audit(matrix_path, sessions_dir)
    dataset_id = f"gate3-controlled-{datetime.now(timezone.utc).strftime('%Y%m%d')}"
    out = output_root / dataset_id / "controlled_dataset"
    sess_out = out / "sessions"
    sess_out.mkdir(parents=True, exist_ok=True)

    session_hashes = {}
    eligible_docs = []
    privacy_reports = []
    consent_summary = {"active": 0, "withdrawn": 0, "pending": 0, "rejected": 0}
    withdrawal_count = 0
    deletion_count = 0

    for path in sorted(sessions_dir.glob("*.json")):
        doc = load_json(path)
        batch = doc.get("measurement_batch") or doc
        ctx = doc.get("session_context") or {}
        evidence = ctx.get("evidence_level") or batch.get("evidence_level")
        if evidence != EVIDENCE_PHYSICAL:
            consent_summary["rejected"] += 1
            continue
        if (batch.get("provenance") or {}).get("collector") == "deterministic_emulator":
            consent_summary["rejected"] += 1
            continue
        if doc.get("deleted"):
            deletion_count += 1
            continue
        status = (batch.get("consent") or {}).get("status")
        if status == "withdrawn":
            withdrawal_count += 1
            consent_summary["withdrawn"] += 1
            continue
        if status != "active":
            consent_summary["rejected"] += 1
            continue
        result = validate_session(path, contracts_dir)
        findings = recursive_privacy_scan(doc)
        privacy_reports.append({"path": str(path), "ok": not findings, "findings": findings})
        if not result["ok"] or findings:
            consent_summary["rejected"] += 1
            continue
        dest = sess_out / path.name
        shutil.copyfile(path, dest)
        h = sha256_file(dest)
        session_hashes[path.name] = h
        eligible_docs.append(doc)
        consent_summary["active"] += 1

    # completed matrix
    completed_rows = []
    with matrix_path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        cell = row["cell_id"]
        match = None
        for name, h in session_hashes.items():
            doc = load_json(sess_out / name)
            ctx = doc.get("session_context") or {}
            batch = doc.get("measurement_batch") or doc
            cid = f"{ctx.get('collection_day_id')}_{ctx.get('named_test_zone')}_{ctx.get('network_condition')}_{ctx.get('workload_profile') or (batch.get('workload') or {}).get('profile')}"
            if cid == cell:
                match = name
                break
        nrow = dict(row)
        if match:
            nrow["status"] = "complete"
            nrow["session_file"] = match
            nrow["validation_status"] = "pass"
            nrow["privacy_status"] = "pass"
        completed_rows.append(nrow)

    completed_csv = out / "collection_matrix_completed.csv"
    with completed_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(completed_rows[0].keys()))
        w.writeheader()
        w.writerows(completed_rows)

    days = sorted({(d.get("session_context") or {}).get("collection_day_id") for d in eligible_docs if (d.get("session_context") or {}).get("collection_day_id")})
    zones = sorted({(d.get("session_context") or {}).get("named_test_zone") for d in eligible_docs if (d.get("session_context") or {}).get("named_test_zone")})
    nets = sorted({(d.get("session_context") or {}).get("network_condition") for d in eligible_docs if (d.get("session_context") or {}).get("network_condition")})
    locs = sorted({(d.get("session_context") or {}).get("location_category") for d in eligible_docs if (d.get("session_context") or {}).get("location_category")})
    workloads = {"learn": 0, "create": 0, "sense": 0}
    devices = set()
    collectors = set()
    for d in eligible_docs:
        ctx = d.get("session_context") or {}
        batch = d.get("measurement_batch") or d
        wl = ctx.get("workload_profile") or (batch.get("workload") or {}).get("profile")
        if wl in workloads:
            workloads[wl] += 1
        if ctx.get("device_category"):
            devices.add(ctx["device_category"])
        if ctx.get("collector_version"):
            collectors.add(ctx["collector_version"])

    privacy_pass = all(r["ok"] for r in privacy_reports) if privacy_reports else True
    commits = {
        "gunnchos-7gc-ai-ran-field-kit": git_sha(ROOT),
        "edge-io-measurement-node": git_sha(repos_root / "edge-io-measurement-node"),
    }
    manifest = {
        "schema_name": "gunnchos.controlled_dataset_manifest",
        "schema_version": "1.0.0",
        "dataset_id": dataset_id,
        "collection_start_date": days[0] if days else "",
        "collection_end_date": days[-1] if days else "",
        "n_sessions": len(eligible_docs),
        "n_locations": len(zones),
        "location_categories": locs,
        "n_network_conditions": len(nets),
        "network_conditions": nets,
        "n_distinct_days": len(days),
        "workload_profile_coverage": workloads,
        "device_model_categories": sorted(devices),
        "collector_versions": sorted(collectors),
        "repository_commits": commits,
        "consent_status_summary": consent_summary,
        "withdrawal_count": withdrawal_count,
        "deletion_count": deletion_count,
        "privacy_review_result": "pass" if privacy_pass else "fail",
        "prohibited_field_scan_result": "pass" if privacy_pass else "fail",
        "raw_data_storage_policy": "local_only_gitignored",
        "sanitized_data_path": str(sess_out),
        "session_hashes": session_hashes,
        "dataset_hash": "0" * 64,  # filled below
        "evidence_level": EVIDENCE_PHYSICAL,
        "missing_cells": coverage["missing_cells"],
        "protocol_deviations": [],
        "known_limitations": [
            "Counts are computed from eligible sanitized session files only.",
            "Raw device files remain gitignored until human publication approval.",
        ],
        "counts_computed_from_sessions": True,
    }
    # temporary write then hash without circularity
    man_path = out / "dataset_manifest.json"
    write_json(man_path, manifest)
    # hash session set + matrix
    payload = {
        "session_hashes": session_hashes,
        "missing_cells": coverage["missing_cells"],
        "n_sessions": len(eligible_docs),
    }
    manifest["dataset_hash"] = sha256_bytes(canonical_json_bytes(payload))
    write_json(man_path, manifest)

    write_json(out / "privacy_review.json", {"reports": privacy_reports, "result": manifest["privacy_review_result"]})
    write_json(out / "consent_summary.json", consent_summary)
    with (out / "protocol_deviations.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["session", "deviation"])
        w.writeheader()
    checksum_lines = []
    for p in sorted(out.rglob("*")):
        if p.is_file() and p.name != "checksums.sha256":
            checksum_lines.append(f"{sha256_file(p)}  {p.relative_to(out)}")
    (out / "checksums.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    (out / "DATASET_CARD.md").write_text(
        f"# Controlled Dataset Card\n\n"
        f"- dataset_id: `{dataset_id}`\n"
        f"- eligible sessions: {len(eligible_docs)}\n"
        f"- missing cells: {len(coverage['missing_cells'])}\n"
        f"- evidence_level: controlled_device_measurement\n"
        f"- publication: not approved by default\n",
        encoding="utf-8",
    )
    return {
        "dataset_id": dataset_id,
        "manifest": str(man_path),
        "eligible_sessions": len(eligible_docs),
        "missing_cells": len(coverage["missing_cells"]),
        "coverage": coverage,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--sessions", default=str(ROOT / "datasets/controlled/sanitized"))
    p.add_argument("--matrix", default=str(ROOT / "protocols/controlled_pilot_matrix.csv"))
    p.add_argument("--output-root", default=str(ROOT / "results/gate3"))
    p.add_argument("--contracts-dir", default=str(ROOT / "contracts"))
    p.add_argument("--repos-root", default=str(ROOT.parent))
    args = p.parse_args(argv)
    result = assemble(
        Path(args.sessions),
        Path(args.matrix),
        Path(args.output_root),
        Path(args.contracts_dir),
        Path(args.repos_root),
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
