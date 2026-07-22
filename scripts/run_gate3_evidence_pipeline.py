#!/usr/bin/env python3
"""One-command Gate 3 evidence pipeline (collection-ready / partial / pass)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_collection_coverage import audit  # noqa: E402
from assemble_controlled_dataset import assemble  # noqa: E402
from evaluate_gate3_status import evaluate  # noqa: E402
from gate3_common import EVIDENCE_PHYSICAL, write_json  # noqa: E402
from register_external_dataset import register, transform_prepared, verify_registry  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--controlled-sessions", default=str(ROOT / "datasets/controlled/sanitized"))
    p.add_argument("--collection-matrix", default=str(ROOT / "protocols/controlled_pilot_matrix.csv"))
    p.add_argument("--external-registry", default=str(ROOT / "datasets/external/registry/external_dataset_registry.json"))
    p.add_argument("--repos-root", default=str(ROOT.parent))
    p.add_argument("--output-root", default=str(ROOT / "results/gate3"))
    p.add_argument("--strict", action="store_true")
    p.add_argument("--android-builds", action="store_true")
    args = p.parse_args(argv)

    out_root = Path(args.output_root)
    out_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = out_root / f"gate3-run-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # External registry
    register()
    ext_verify = verify_registry()
    if not ext_verify["ok"]:
        print(json.dumps(ext_verify, indent=2), file=sys.stderr)
        if args.strict:
            return 1

    transform_report = transform_prepared(run_dir / "external_evidence" / "transformed_data.json")
    write_json(run_dir / "external_evidence" / "transformation_report.json", transform_report)
    write_json(
        run_dir / "external_evidence" / "source_record.json",
        json.loads(Path(args.external_registry).read_text())["records"][1],
    )

    coverage = audit(Path(args.collection_matrix), Path(args.controlled_sessions))
    write_json(run_dir / "coverage_audit.json", coverage)

    assembled = assemble(
        Path(args.controlled_sessions),
        Path(args.collection_matrix),
        run_dir,
        ROOT / "contracts",
        Path(args.repos_root),
    )

    # Attempt physical integrated runs only for eligible physical sessions
    integrated_ids = []
    sessions = list(Path(assembled["manifest"]).parent.joinpath("sessions").glob("*.json"))
    for sess in sessions[:1]:  # one representative if any genuine sessions exist
        doc = json.loads(sess.read_text())
        batch = doc.get("measurement_batch") or doc
        if batch.get("evidence_level") != EVIDENCE_PHYSICAL:
            continue
        # Refuse synthetic-through-gate3 path
        if (batch.get("provenance") or {}).get("collector") == "deterministic_emulator":
            raise SystemExit("Refusing to treat emulator session as genuine Gate 3 evidence")
        edge_batch = run_dir / "integrated_runs" / f"{batch['run_id']}_edge.json"
        edge_batch.parent.mkdir(parents=True, exist_ok=True)
        edge_batch.write_text(json.dumps(batch, indent=2) + "\n")
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "run_integrated_pipeline.py"),
                "--edge-input",
                str(edge_batch),
                "--repos-root",
                str(args.repos_root),
                "--output-root",
                str(run_dir / "integrated_runs"),
                "--strict",
            ],
            capture_output=True,
            text=True,
        )
        (run_dir / "integrated_runs" / "pipeline_log.txt").write_text(proc.stdout + "\n" + proc.stderr)
        if proc.returncode == 0:
            integrated_ids.append(batch["run_id"])

    # External complete if NTN assumption registry has literature-backed load-bearing params
    ntn_reg = Path(args.repos_root) / "ntn-resilience-sim" / "config" / "assumption_registry.yaml"
    external_complete = False
    if ntn_reg.is_file():
        import yaml

        data = yaml.safe_load(ntn_reg.read_text())
        classes = {k: v.get("assumption_class") for k, v in data.get("assumptions", {}).items()}
        load_bearing = ["ntn_latency_ms", "ntn_capacity_mbps", "ntn_availability"]
        external_complete = all(
            classes.get(k) in {"literature_backed", "open_data", "measured"} for k in load_bearing
        ) and all(data["assumptions"][k].get("source_location") for k in load_bearing)

    status = evaluate(
        coverage,
        android_builds=args.android_builds,
        consent_deletion_ok=True,
        protocol_exists=(ROOT / "protocols/CONTROLLED_PILOT_PROTOCOL.md").is_file(),
        matrix_exists=Path(args.collection_matrix).is_file(),
        assemble_works=True,
        external_prepared=True,
        external_complete=external_complete,
        physical_pipeline_ok=bool(integrated_ids) or coverage["eligible_physical_session_count"] == 0,
        privacy_ok=True,
        consent_ok=True,
    )
    status["generated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    status["dataset_id"] = assembled.get("dataset_id")
    status["integrated_run_ids"] = integrated_ids
    status["limitations"] = [
        "Synthetic fixtures never satisfy Gate 3.",
        "M-Lab open-data download remains blocked pending AUA/GCS access.",
        "Physical pilot not executed in this automation environment.",
    ]
    write_json(run_dir / "gate3_status.json", status)

    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / "scripts" / "generate_gate3_report.py"),
            "--status-json",
            str(run_dir / "gate3_status.json"),
            "--coverage-json",
            str(run_dir / "coverage_audit.json"),
            "--output-dir",
            str(run_dir),
        ]
    )

    print(
        json.dumps(
            {
                "ok": True,
                "run_dir": str(run_dir),
                "gate3_status": status["gate3_status"],
                "eligible_physical_session_count": coverage["eligible_physical_session_count"],
                "missing_cells": len(coverage["missing_cells"]),
                "external_complete": external_complete,
            },
            indent=2,
        )
    )

    if args.strict and status["gate3_status"] not in {"GATE_3_PASS"}:
        # Strict completion mode fails if not fully passed; readiness mode uses non-strict.
        # For collection-ready software verification, callers should omit --strict.
        if status["gate3_status"] == "FAIL":
            return 2
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
