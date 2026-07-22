#!/usr/bin/env python3
"""Register / verify / transform external Gate 3 evidence sources."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate3_common import sha256_file, write_json  # noqa: E402

REGISTRY = ROOT / "datasets/external/registry/external_dataset_registry.json"


def default_registry() -> dict:
    return {
        "schema_name": "gunnchos.external_dataset_registry",
        "schema_version": "1.0.0",
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "records": [
            {
                "schema_name": "gunnchos.external_dataset_record",
                "schema_version": "1.0.0",
                "record_id": "mlab-ndt-cc0",
                "title": "Measurement Lab NDT Data Set",
                "publisher": "Measurement Lab (M-Lab)",
                "source_location": "https://www.measurementlab.net/tests/ndt/",
                "version_or_retrieval_date": "2026-07-22",
                "license_or_terms": "Creative Commons Zero (CC0) / No Rights Reserved as stated by M-Lab",
                "citation": "The M-Lab NDT Data Set. https://measurementlab.net/tests/ndt",
                "intended_gate3_use": "Open-data latency/throughput/loss priors for twin-state calibration comparisons",
                "original_checksum": None,
                "download_command": (
                    "Requires M-Lab Acceptable Use Agreement + GCS/BigQuery access; "
                    "see https://www.measurementlab.net/data/docs/archival-data/"
                ),
                "original_file_list": [],
                "transformation_script": "scripts/transform_external_dataset.py",
                "transformed_checksum": None,
                "field_mapping": {
                    "MinRTT": "latency_ms",
                    "Download": "download_mbps",
                    "Upload": "upload_mbps",
                    "Loss": "packet_loss_pct",
                },
                "unit_mapping": {
                    "latency_ms": "ms",
                    "download_mbps": "Mbps",
                    "upload_mbps": "Mbps",
                    "packet_loss_pct": "percent",
                },
                "missing_data_behavior": "drop_row_if_required_metric_absent",
                "limitations": [
                    "Raw archive download requires AUA acceptance; not completed in this automation environment.",
                    "Do not claim open-data integration complete until checksummed files are retrieved.",
                ],
                "evidence_class": "open_data",
                "status": "blocked_pending_access",
            },
            {
                "schema_name": "gunnchos.external_dataset_record",
                "schema_version": "1.0.0",
                "record_id": "ntn-source-validated-sim-v1",
                "title": "NTN resilience source-validated simulation parameter pack",
                "publisher": "gunnchos ntn-resilience-sim (parameters sourced from 3GPP TR 38.821 and configured ranges)",
                "source_location": "https://www.3gpp.org/ (TR 38.821 Solutions for NR to support non-terrestrial networks)",
                "version_or_retrieval_date": "2026-07-22",
                "license_or_terms": "3GPP documents subject to 3GPP copyright; parameter values used under research citation practice",
                "citation": "3GPP TR 38.821: Solutions for NR to support non-terrestrial networks (NTN).",
                "intended_gate3_use": "Source-validated simulation assumptions for NTN latency/availability sensitivity",
                "original_checksum": None,
                "download_command": "Documented in ntn-resilience-sim/config/assumption_registry.yaml",
                "original_file_list": ["ntn-resilience-sim/config/assumption_registry.yaml"],
                "transformation_script": "ntn-resilience-sim (native assumption registry)",
                "transformed_checksum": None,
                "field_mapping": {
                    "ntn_latency_ms": "estimated_latency_ms",
                    "ntn_capacity_mbps": "estimated_capacity_mbps",
                    "ntn_availability": "path_availability",
                },
                "unit_mapping": {
                    "ntn_latency_ms": "ms",
                    "ntn_capacity_mbps": "Mbps",
                    "ntn_availability": "fraction",
                },
                "missing_data_behavior": "reject_unsupported_parameters",
                "limitations": [
                    "Qualifies as source_validated_simulation only when all load-bearing parameters include verified source_id metadata.",
                    "Configured/synthetic classes alone do not qualify.",
                ],
                "evidence_class": "source_validated_simulation",
                "status": "prepared",
            },
        ],
    }


def register() -> Path:
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    if not REGISTRY.exists():
        write_json(REGISTRY, default_registry())
    return REGISTRY


def verify_registry() -> dict:
    reg = json.loads(register().read_text(encoding="utf-8"))
    errors = []
    for rec in reg.get("records", []):
        if not rec.get("license_or_terms"):
            errors.append(f"{rec.get('record_id')}: missing license_or_terms")
        if not rec.get("source_location"):
            errors.append(f"{rec.get('record_id')}: missing source_location")
        if rec.get("status") == "verified" and not rec.get("original_checksum"):
            errors.append(f"{rec.get('record_id')}: verified without checksum")
    return {"ok": not errors, "errors": errors, "records": len(reg.get("records", []))}


def transform_prepared(output: Path) -> dict:
    """Deterministic transform placeholder for prepared simulation pack metadata."""
    reg = json.loads(register().read_text(encoding="utf-8"))
    sim = next(r for r in reg["records"] if r["record_id"] == "ntn-source-validated-sim-v1")
    payload = {
        "evidence_level": "source_validated_simulation",
        "record_id": sim["record_id"],
        "citation": sim["citation"],
        "parameters": list(sim["field_mapping"].keys()),
        "unit_mapping": sim["unit_mapping"],
        "status": sim["status"],
        "note": "Metadata transform only; values live in NTN assumption registry.",
    }
    write_json(output, payload)
    report = {
        "source_record_id": sim["record_id"],
        "transformed_path": str(output),
        "transformed_checksum": sha256_file(output),
        "row_count_before": 0,
        "row_count_after": len(payload["parameters"]),
        "dropped_records": 0,
        "unit_conversions": sim["unit_mapping"],
        "missing_value_handling": sim["missing_data_behavior"],
    }
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("register")
    sub.add_parser("verify")
    tr = sub.add_parser("transform")
    tr.add_argument("--output", default=str(ROOT / "datasets/external/transformed/ntn_sim_metadata.json"))
    args = p.parse_args(argv)
    if args.cmd == "register":
        path = register()
        print(json.dumps({"wrote": str(path)}, indent=2))
        return 0
    if args.cmd == "verify":
        result = verify_registry()
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1
    if args.cmd == "transform":
        report = transform_prepared(Path(args.output))
        write_json(Path(args.output).with_name("transformation_report.json"), report)
        print(json.dumps(report, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
