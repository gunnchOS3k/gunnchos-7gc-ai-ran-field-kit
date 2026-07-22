"""Shared Gate 4 evaluation helpers.

Gate 4 readiness is intentionally separate from a scientific pass. Synthetic
and calibration-only runs can validate infrastructure, but cannot satisfy
inferential requirements or produce GATE_4_PASS.
"""
from __future__ import annotations

import csv
import hashlib
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

EVIDENCE_PHYSICAL = "controlled_device_measurement"
EVIDENCE_SYNTHETIC = "synthetic"
EVIDENCE_CALIBRATION_ONLY = "calibration_only"
EVIDENCE_OPEN = "open_data"
EVIDENCE_SOURCE_VALIDATED = "source_validated_simulation"

INFRASTRUCTURE_LABEL = "infrastructure_validation_only"
INSUFFICIENT_INFERENCE_LABEL = "insufficient_sample_size_for_inference"

GATE4_STATUSES = {
    "FAIL",
    "GATE4_EVALUATION_READY",
    "GATE4_PARTIAL_EVALUATION",
    "GATE_4_PASS",
}

AI_RAN_BASELINES = [
    "static_uniform",
    "network_only",
    "service_priority",
    "optimization_based",
    "twin_informed",
]

RESILIENCE_BASELINES = [
    "terrestrial_only",
    "terrestrial_then_offline",
    "always_ntn_on_terrestrial_failure",
    "priority_class_fallback",
    "service_aware_multi_access",
    "oracle_hindsight_analysis_only",
]

ABLATIONS = [
    "remove_edge_io_observations",
    "remove_digital_twin_context",
    "remove_service_continuity_objective",
    "remove_fairness_constraint",
    "remove_energy_constraint",
    "remove_local_edge_availability",
    "remove_uncertainty_inputs",
    "remove_external_source_validated_context",
    "remove_ntn_option",
    "remove_privacy_constraint_simulated_decision_constraint_only",
]

SENSITIVITY_PARAMETERS = [
    "latency",
    "jitter",
    "packet_loss",
    "capacity",
    "energy",
    "local_edge",
    "outage_duration",
    "recovery_delay",
    "ntn_latency",
    "ntn_capacity",
    "ntn_availability",
    "handover_delay",
    "mobility",
    "blockage",
    "service_class",
    "fairness_threshold",
    "continuity_threshold",
]

SPLIT_TYPES = [
    "leave_one_day_out",
    "leave_one_zone_out",
    "leave_one_network_condition_out",
    "leave_one_workload_profile_out",
    "stress_scenario_holdout",
]

MIN_GATE4_SESSIONS = 54
MIN_INFERENCE_SESSIONS = 30


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    return path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys: list[str] = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys or ["empty"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    return path


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def evidence_level(manifest: dict[str, Any]) -> str:
    return str(manifest.get("evidence_level") or EVIDENCE_SYNTHETIC)


def is_synthetic_like(manifest: dict[str, Any]) -> bool:
    level = evidence_level(manifest)
    return level in {EVIDENCE_SYNTHETIC, EVIDENCE_CALIBRATION_ONLY} or bool(
        manifest.get("infrastructure_validation_only")
    )


def inference_label(manifest: dict[str, Any], sample_count: int) -> str:
    if is_synthetic_like(manifest) or sample_count < MIN_INFERENCE_SESSIONS:
        return INSUFFICIENT_INFERENCE_LABEL
    return "inferential_evaluation"


def evaluation_label(manifest: dict[str, Any]) -> str:
    if is_synthetic_like(manifest):
        return INFRASTRUCTURE_LABEL
    return "scientific_evaluation"


def session_id_for(path: Path, doc: dict[str, Any], index: int) -> str:
    ctx = doc.get("session_context") or {}
    batch = doc.get("measurement_batch") or doc
    return str(ctx.get("session_id") or batch.get("run_id") or path.stem or f"session_{index:04d}")


def session_rows_from_dir(sessions_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not sessions_dir.is_dir():
        return rows
    for index, path in enumerate(sorted(sessions_dir.glob("*.json")), start=1):
        doc = load_json(path)
        ctx = doc.get("session_context") or {}
        batch = doc.get("measurement_batch") or doc
        workload = ctx.get("workload_profile") or (batch.get("workload") or {}).get("profile") or "unknown"
        rows.append(
            {
                "session_id": session_id_for(path, doc, index),
                "path": str(path),
                "hash": sha256_file(path),
                "collection_day_id": ctx.get("collection_day_id") or "unknown_day",
                "zone_id": ctx.get("named_test_zone") or ctx.get("zone_id") or "unknown_zone",
                "network_condition": ctx.get("network_condition") or "unknown_network",
                "workload_profile": workload,
                "evidence_level": ctx.get("evidence_level") or batch.get("evidence_level") or EVIDENCE_SYNTHETIC,
                "is_stress": bool(ctx.get("protocol_deviation")) or "stress" in str(ctx.get("network_condition", "")),
                "consent_status": (batch.get("consent") or {}).get("status"),
                "collector": (batch.get("provenance") or {}).get("collector"),
            }
        )
    return rows


def fallback_rows_from_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    session_hashes = manifest.get("session_hashes") or {}
    rows: list[dict[str, Any]] = []
    if isinstance(session_hashes, dict) and session_hashes:
        days = list(range(max(1, int(manifest.get("n_distinct_days") or 1))))
        zones = manifest.get("location_categories") or ["zone_unknown"]
        networks = manifest.get("network_conditions") or ["network_unknown"]
        workloads = list((manifest.get("workload_profile_coverage") or {"unknown": 1}).keys())
        for index, (name, digest) in enumerate(sorted(session_hashes.items())):
            rows.append(
                {
                    "session_id": Path(name).stem,
                    "path": name,
                    "hash": digest,
                    "collection_day_id": f"day_{days[index % len(days)] + 1:02d}",
                    "zone_id": str(zones[index % len(zones)]),
                    "network_condition": str(networks[index % len(networks)]),
                    "workload_profile": str(workloads[index % len(workloads)]),
                    "evidence_level": evidence_level(manifest),
                    "is_stress": False,
                }
            )
    return rows


def load_dataset_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    manifest["_manifest_path"] = str(path)
    return manifest


def load_dataset_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    sessions_dir = manifest.get("sanitized_data_path") or manifest.get("sessions_dir")
    rows: list[dict[str, Any]] = []
    if sessions_dir:
        candidate = Path(str(sessions_dir))
        if not candidate.is_absolute():
            manifest_path = Path(manifest.get("_manifest_path", ROOT)).resolve()
            candidate = (manifest_path.parent / candidate).resolve()
        rows = session_rows_from_dir(candidate)
    if not rows:
        rows = fallback_rows_from_manifest(manifest)
    return rows


def duplicate_hashes(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    seen: dict[str, list[str]] = {}
    for row in rows:
        digest = str(row.get("hash") or "")
        if digest:
            seen.setdefault(digest, []).append(str(row.get("session_id") or row.get("path")))
    return {digest: ids for digest, ids in seen.items() if len(ids) > 1}


def split_groups(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    values = sorted({str(row.get(key) or "unknown") for row in rows})
    all_ids = {str(row["session_id"]) for row in rows}
    for value in values:
        test_ids = {str(row["session_id"]) for row in rows if str(row.get(key) or "unknown") == value}
        train_ids = all_ids - test_ids
        groups.append(
            {
                "holdout_value": value,
                "train_session_ids": sorted(train_ids),
                "test_session_ids": sorted(test_ids),
                "leakage_detected": bool(train_ids & test_ids),
            }
        )
    return groups


def deterministic_score(name: str, sample_count: int, offset: float = 0.0) -> float:
    seed = sum(ord(c) for c in name) % 97
    base = 0.45 + (seed / 300.0) + min(sample_count, 100) / 1000.0 + offset
    return round(min(base, 0.95), 4)


def mean_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return round(statistics.mean(values), 6)


def required_gate4_artifacts(run_dir: Path) -> dict[str, Path]:
    return {
        "experiment_manifest": run_dir / "experiment_manifest.json",
        "split_summary": run_dir / "splits" / "split_summary.json",
        "baseline_results": run_dir / "raw_results" / "baseline_results.csv",
        "ablation_results": run_dir / "raw_results" / "ablation_results.csv",
        "uncertainty_report": run_dir / "raw_results" / "uncertainty_report.json",
        "sensitivity_results": run_dir / "raw_results" / "sensitivity_results.csv",
        "failure_boundaries": run_dir / "raw_results" / "failure_boundaries.csv",
        "negative_results": run_dir / "reports" / "NEGATIVE_RESULTS_REGISTER.md",
        "tables": run_dir / "tables" / "gate4_summary_table.csv",
        "figures": run_dir / "figures" / "gate4_sensitivity.svg",
        "evaluation_report": run_dir / "reports" / "GATE4_EVALUATION_REPORT.md",
    }


def evaluate_artifact_status(
    *,
    manifest: dict[str, Any],
    sample_count: int,
    split_summary: dict[str, Any],
    run_dir: Path,
) -> dict[str, Any]:
    artifacts = required_gate4_artifacts(run_dir)
    missing = [name for name, path in artifacts.items() if not path.is_file()]
    duplicates = split_summary.get("duplicate_hashes") or {}
    leakage = split_summary.get("leakage_detected") is True
    split_ok = split_summary.get("ok") is True
    synthetic_like = is_synthetic_like(manifest)
    label = evaluation_label(manifest)
    inf_label = inference_label(manifest, sample_count)
    reasons: list[str] = []

    if missing:
        reasons.append("missing_required_artifacts:" + ",".join(sorted(missing)))
    if duplicates:
        reasons.append("duplicate_session_hashes_detected")
    if leakage:
        reasons.append("session_train_test_leakage_detected")
    if not split_ok:
        reasons.append("split_validation_failed")
    if sample_count < MIN_GATE4_SESSIONS:
        reasons.append("sample_count_below_gate4_minimum")
    if synthetic_like:
        reasons.append("synthetic_or_calibration_run_not_eligible_for_gate4_pass")
    if inf_label == INSUFFICIENT_INFERENCE_LABEL:
        reasons.append("insufficient_sample_size_for_inference")

    if missing or duplicates or leakage or not split_ok:
        status = "FAIL"
    elif synthetic_like:
        status = "GATE4_EVALUATION_READY"
    elif sample_count < MIN_GATE4_SESSIONS or inf_label == INSUFFICIENT_INFERENCE_LABEL:
        status = "GATE4_PARTIAL_EVALUATION"
    else:
        status = "GATE_4_PASS"

    if synthetic_like and status == "GATE_4_PASS":
        status = "GATE4_EVALUATION_READY"
    return {
        "schema_name": "gunnchos.gate4_evaluation_status",
        "schema_version": "1.0.0",
        "gate4_status": status,
        "evaluation_label": label,
        "inference_label": inf_label,
        "sample_count": sample_count,
        "missing_requirements": sorted(set(reasons)),
        "artifacts": {name: str(path) for name, path in artifacts.items()},
        "limitations": [
            "Synthetic and calibration-only fixtures never produce GATE_4_PASS.",
            "Oracle hindsight resilience baseline is analysis-only and never deployable.",
            "GATE_4_PASS requires eligible non-synthetic data, no leakage, no duplicate hashes, and sufficient sample size.",
        ],
        "generated_at": utc_now(),
    }
