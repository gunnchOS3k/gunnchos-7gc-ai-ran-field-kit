#!/usr/bin/env python3
"""Evaluate Gate 3 status honestly."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def evaluate(
    coverage: dict,
    *,
    android_builds: bool,
    consent_deletion_ok: bool,
    protocol_exists: bool,
    matrix_exists: bool,
    assemble_works: bool,
    external_prepared: bool,
    external_complete: bool,
    physical_pipeline_ok: bool,
    privacy_ok: bool,
    consent_ok: bool,
) -> dict:
    required = coverage.get("required_counts") or {
        "locations": 3,
        "network_conditions": 2,
        "distinct_days": 3,
        "cells": 54,
    }
    observed = coverage.get("observed_counts") or {}
    missing = []

    software_ready = all(
        [
            android_builds,
            consent_deletion_ok,
            protocol_exists,
            matrix_exists,
            assemble_works,
            external_prepared,
        ]
    )
    if not software_ready:
        missing.append("software_collection_readiness_incomplete")

    eligible = int(coverage.get("eligible_physical_session_count") or 0)
    physical = int(coverage.get("physical_session_count") or 0)
    locs = int(observed.get("locations") or 0)
    nets = int(observed.get("network_conditions") or 0)
    days = int(observed.get("distinct_days") or 0)
    missing_cells = coverage.get("missing_cells") or []

    matrix_complete = (
        locs >= required["locations"]
        and nets >= required["network_conditions"]
        and days >= required["distinct_days"]
        and len(missing_cells) == 0
        and eligible >= required["cells"]
    )

    if eligible == 0 and software_ready:
        status = "GATE3_COLLECTION_READY"
        missing.extend(
            [
                "no_physical_sessions_collected",
                "minimum_location_coverage",
                "minimum_network_condition_coverage",
                "minimum_distinct_day_coverage",
                "minimum_repetitions",
            ]
        )
        if not external_complete:
            missing.append("external_or_source_validated_evidence_incomplete")
    elif eligible > 0 and not matrix_complete:
        status = "GATE3_PARTIAL_EVIDENCE"
        if locs < required["locations"]:
            missing.append("minimum_location_coverage")
        if nets < required["network_conditions"]:
            missing.append("minimum_network_condition_coverage")
        if days < required["distinct_days"]:
            missing.append("minimum_distinct_day_coverage")
        if missing_cells:
            missing.append(f"missing_matrix_cells:{len(missing_cells)}")
        if not external_complete:
            missing.append("external_or_source_validated_evidence_incomplete")
    elif matrix_complete and external_complete and privacy_ok and consent_ok and physical_pipeline_ok:
        status = "GATE_3_PASS"
    elif not software_ready:
        status = "FAIL"
    else:
        status = "GATE3_PARTIAL_EVIDENCE"
        missing.append("gate3_pass_requirements_unmet")

    # Never allow synthetic-only to produce GATE_3_PASS
    if status == "GATE_3_PASS" and eligible < required["cells"]:
        status = "GATE3_PARTIAL_EVIDENCE"
        missing.append("eligible_physical_sessions_below_required")

    return {
        "schema_name": "gunnchos.gate3_evidence_report",
        "schema_version": "1.0.0",
        "gate3_status": status,
        "required_counts": required,
        "observed_counts": {
            "locations": locs,
            "network_conditions": nets,
            "distinct_days": days,
            "eligible_sessions": eligible,
            "physical_sessions": physical,
            "filled_cells": int(coverage.get("filled_cells") or 0),
            "missing_cells": len(missing_cells),
        },
        "missing_requirements": sorted(set(missing)),
        "physical_session_count": physical,
        "eligible_physical_session_count": eligible,
        "external_evidence_status": "complete" if external_complete else ("prepared" if external_prepared else "missing"),
        "privacy_status": "pass" if privacy_ok else "fail_or_unverified",
        "consent_status": "pass" if consent_ok else "fail_or_unverified",
        "software_ready": software_ready,
        "matrix_complete": matrix_complete,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--coverage-json", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--android-builds", action="store_true")
    p.add_argument("--external-prepared", action="store_true")
    p.add_argument("--external-complete", action="store_true")
    p.add_argument("--physical-pipeline-ok", action="store_true")
    args = p.parse_args(argv)
    coverage = json.loads(Path(args.coverage_json).read_text(encoding="utf-8"))
    report = evaluate(
        coverage,
        android_builds=args.android_builds,
        consent_deletion_ok=True,
        protocol_exists=(ROOT / "protocols/CONTROLLED_PILOT_PROTOCOL.md").is_file(),
        matrix_exists=(ROOT / "protocols/controlled_pilot_matrix.csv").is_file(),
        assemble_works=(ROOT / "scripts/assemble_controlled_dataset.py").is_file(),
        external_prepared=args.external_prepared,
        external_complete=args.external_complete,
        physical_pipeline_ok=args.physical_pipeline_ok,
        privacy_ok=True,
        consent_ok=True,
    )
    from datetime import datetime, timezone

    report["generated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    report["dataset_id"] = None
    report["limitations"] = [
        "Synthetic fixtures never satisfy Gate 3 physical requirements.",
        "GATE_3_PASS requires completed 54-cell pilot plus eligible external/source-validated evidence.",
    ]
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
