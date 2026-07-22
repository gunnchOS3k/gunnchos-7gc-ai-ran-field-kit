#!/usr/bin/env python3
"""Evaluate Gate 2 status honestly from an integrated run directory."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_ARTIFACTS = [
    "01_edge_measurements.json",
    "02_twin_state.json",
    "03_airan_static_decision.json",
    "03_airan_network_only_decision.json",
    "03_airan_service_priority_decision.json",
    "03_airan_optimization_decision.json",
    "03_airan_twin_informed_decision.json",
    "04_resilience_decision.json",
    "benchmark_results.csv",
    "ablation_results.csv",
    "sensitivity_results.csv",
    "checksums.sha256",
    "environment.txt",
    "validation_report.json",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--external-evidence",
        type=Path,
        default=None,
        help="Optional JSON checklist of external evidence flags",
    )
    args = parser.parse_args(argv)

    unmet = []
    for name in REQUIRED_ARTIFACTS:
        if not (args.run_dir / name).is_file():
            unmet.append(f"missing artifact: {name}")

    edge = {}
    if (args.run_dir / "01_edge_measurements.json").is_file():
        edge = json.loads((args.run_dir / "01_edge_measurements.json").read_text())

    automated_ok = not unmet
    status = "FAIL"
    if automated_ok:
        status = "AUTOMATED_PIPELINE_PASS"

    external = {
        "physical_device_measurement": edge.get("evidence_level")
        == "controlled_device_measurement",
        "real_consent_metadata": bool((edge.get("consent") or {}).get("receipt_id"))
        and edge.get("evidence_level") == "controlled_device_measurement",
        "clean_checkout_reproduction": False,
        "non_author_reproduction": False,
        "immutable_candidate_release": False,
        "doi_or_archived_dataset": False,
    }
    if args.external_evidence and args.external_evidence.is_file():
        external.update(json.loads(args.external_evidence.read_text()))

    external_unmet = [k for k, v in external.items() if not v]
    if status == "AUTOMATED_PIPELINE_PASS" and not external_unmet:
        status = "GATE_2_PASS"
    elif status == "AUTOMATED_PIPELINE_PASS":
        unmet.extend([f"external evidence missing: {k}" for k in external_unmet])

    payload = {
        "status": status,
        "automated_pipeline_pass": status in {"AUTOMATED_PIPELINE_PASS", "GATE_2_PASS"},
        "unmet_criteria": unmet,
        "external_evidence": external,
        "evidence_level_edge": edge.get("evidence_level"),
        "notes": (
            "GATE_2_PASS requires physical-device evidence, independent reproduction, "
            "candidate release, and DOI/archive evidence. Automated software completion "
            "alone yields AUTOMATED_PIPELINE_PASS."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
