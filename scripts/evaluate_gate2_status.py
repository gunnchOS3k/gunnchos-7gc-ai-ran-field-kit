#!/usr/bin/env python3
"""Evaluate Gate 2 system status separately from Gate 5/6 release evidence."""
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


def evaluate_release_evidence(flags: dict | None = None) -> dict:
    """Gate 5/6 release-evidence dimension — not part of Gate 2 system PASS."""
    external = {
        "clean_checkout_reproduction": False,
        "non_author_reproduction": False,
        "immutable_candidate_release": False,
        "doi_or_archived_dataset": False,
    }
    if flags:
        external.update({k: bool(flags.get(k)) for k in external})
    unmet = [k for k, v in external.items() if not v]
    if not unmet:
        status = "RELEASE_EVIDENCE_COMPLETE"
    elif any(external.values()):
        status = "RELEASE_EVIDENCE_PARTIAL"
    else:
        status = "RELEASE_EVIDENCE_PENDING"
    return {
        "release_evidence_status": status,
        "checks": external,
        "unmet": unmet,
        "mapped_gates": {
            "clean_checkout_reproduction": "Gate 5 — reproducibility",
            "non_author_reproduction": "Gate 5 — reproducibility",
            "immutable_candidate_release": "Gate 6 — publication and archive",
            "doi_or_archived_dataset": "Gate 6 — publication and archive",
        },
        "notes": (
            "Release-evidence requirements remain mandatory for publication readiness "
            "but do not block Gate 2 system completion."
        ),
    }


def evaluate_gate2_system(run_dir: Path) -> dict:
    unmet: list[str] = []
    for name in REQUIRED_ARTIFACTS:
        if not (run_dir / name).is_file():
            unmet.append(f"missing artifact: {name}")

    edge: dict = {}
    manifest: dict = {}
    validation: dict = {}
    if (run_dir / "01_edge_measurements.json").is_file():
        edge = json.loads((run_dir / "01_edge_measurements.json").read_text(encoding="utf-8"))
    if (run_dir / "manifest.json").is_file():
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if (run_dir / "validation_report.json").is_file():
        validation = json.loads((run_dir / "validation_report.json").read_text(encoding="utf-8"))

    evidence = edge.get("evidence_level")
    has_controlled = evidence == "controlled_device_measurement"
    has_synthetic_proof = evidence == "synthetic"
    consent_ok = bool((edge.get("consent") or {}).get("receipt_id"))

    if not (has_controlled or has_synthetic_proof):
        unmet.append("missing controlled-device path or explicit synthetic system proof")
    if has_controlled and not consent_ok:
        unmet.append("controlled-device path missing consent receipt")

    # Prefer validation report when present
    if validation and validation.get("ok") is False:
        unmet.append("validation_report.ok is false")

    if unmet:
        status = "FAIL"
    elif has_controlled or has_synthetic_proof:
        # Executable cross-repo path with required artifacts present.
        status = "GATE2_SYSTEM_PASS"
    else:
        status = "GATE2_INTEGRATION_READY"

    # Compatibility aliases for older readers
    legacy_status = "AUTOMATED_PIPELINE_PASS" if status == "GATE2_SYSTEM_PASS" else status

    return {
        "gate2_status": status,
        "legacy_status_alias": legacy_status,
        "system_pass": status == "GATE2_SYSTEM_PASS",
        "unmet_criteria": unmet,
        "evidence_level_edge": evidence,
        "controlled_device_path": has_controlled,
        "synthetic_system_proof": has_synthetic_proof and not has_controlled,
        "run_id": edge.get("run_id") or manifest.get("run_id"),
        "notes": (
            "GATE2_SYSTEM_PASS means the executable Edge-IO → 7GC → SpectrumX → NTN "
            "path is complete with schema-validated artifacts. It does NOT imply Gate 5 "
            "reproduction or Gate 6 DOI/archive completion."
        ),
        "taxonomy_migration": {
            "old_label": "AUTOMATED_PIPELINE_PASS",
            "new_label": "GATE2_SYSTEM_PASS",
            "moved_to_release_evidence": [
                "clean_checkout_reproduction",
                "non_author_reproduction",
                "immutable_candidate_release",
                "doi_or_archived_dataset",
            ],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--external-evidence",
        type=Path,
        default=None,
        help="Optional JSON checklist for release-evidence flags (Gate 5/6)",
    )
    args = parser.parse_args(argv)

    release_flags = None
    if args.external_evidence and args.external_evidence.is_file():
        release_flags = json.loads(args.external_evidence.read_text(encoding="utf-8"))

    system = evaluate_gate2_system(args.run_dir)
    release = evaluate_release_evidence(release_flags)

    payload = {
        **system,
        # Keep historical key for callers that still read "status"
        "status": system["gate2_status"],
        "automated_pipeline_pass": system["system_pass"],
        "release_evidence": release,
        "external_evidence": {
            "physical_device_measurement": system["controlled_device_path"],
            "real_consent_metadata": bool(
                ((json.loads((args.run_dir / "01_edge_measurements.json").read_text()) if (args.run_dir / "01_edge_measurements.json").is_file() else {}).get("consent") or {}).get("receipt_id")
            )
            and system["controlled_device_path"],
            **release["checks"],
        },
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if system["system_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
