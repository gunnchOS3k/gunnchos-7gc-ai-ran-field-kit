#!/usr/bin/env python3
"""Build Gate 4 held-out evaluation splits with leakage checks."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate4_common import (  # noqa: E402
    EVIDENCE_SYNTHETIC,
    INFRASTRUCTURE_LABEL,
    MIN_GATE4_SESSIONS,
    SPLIT_TYPES,
    duplicate_hashes,
    evaluation_label,
    is_synthetic_like,
    load_dataset_manifest,
    load_dataset_rows,
    split_groups,
    utc_now,
    write_json,
)


def synthetic_manifest(path: Path) -> dict:
    return {
        "schema_name": "gunnchos.gate4_synthetic_dataset_manifest",
        "schema_version": "1.0.0",
        "dataset_id": "gate4-infrastructure-validation-fixture",
        "evidence_level": EVIDENCE_SYNTHETIC,
        "infrastructure_validation_only": True,
        "n_sessions": 6,
        "n_distinct_days": 2,
        "location_categories": ["zone_a", "zone_b", "zone_c"],
        "network_conditions": ["wifi_normal", "wifi_degraded"],
        "workload_profile_coverage": {"learn": 2, "create": 2, "sense": 2},
        "session_hashes": {f"synthetic_session_{i}.json": f"{i:064x}" for i in range(1, 7)},
        "known_limitations": [
            "Synthetic fixture for infrastructure validation only.",
            "Insufficient sample size for scientific inference.",
        ],
        "_manifest_path": str(path),
    }


def build_splits(manifest: dict, output_dir: Path, *, allow_small: bool = False) -> dict:
    rows = load_dataset_rows(manifest)
    if not rows and is_synthetic_like(manifest):
        rows = [
            {
                "session_id": f"synthetic_session_{i}",
                "hash": f"{i:064x}",
                "collection_day_id": f"day_{1 + (i % 2):02d}",
                "zone_id": f"zone_{chr(97 + (i % 3))}",
                "network_condition": "wifi_degraded" if i % 2 else "wifi_normal",
                "workload_profile": ["learn", "create", "sense"][i % 3],
                "evidence_level": EVIDENCE_SYNTHETIC,
                "is_stress": i in {4, 5},
            }
            for i in range(6)
        ]
    dupes = duplicate_hashes(rows)
    split_specs = {
        "leave_one_day_out": ("collection_day_id", split_groups(rows, "collection_day_id")),
        "leave_one_zone_out": ("zone_id", split_groups(rows, "zone_id")),
        "leave_one_network_condition_out": ("network_condition", split_groups(rows, "network_condition")),
        "leave_one_workload_profile_out": ("workload_profile", split_groups(rows, "workload_profile")),
    }
    stress_test = [str(r["session_id"]) for r in rows if r.get("is_stress")]
    if not stress_test and rows:
        stress_test = [str(rows[-1]["session_id"])]
    stress_train = sorted({str(r["session_id"]) for r in rows} - set(stress_test))
    split_specs["stress_scenario_holdout"] = (
        "is_stress",
        [
            {
                "holdout_value": "stress",
                "train_session_ids": stress_train,
                "test_session_ids": sorted(stress_test),
                "leakage_detected": bool(set(stress_train) & set(stress_test)),
            }
        ],
    )

    leakage = False
    for split_name, (key, groups) in split_specs.items():
        payload = {
            "schema_name": "gunnchos.gate4_split",
            "schema_version": "1.0.0",
            "split_type": split_name,
            "held_out_key": key,
            "evaluation_label": evaluation_label(manifest),
            "groups": groups,
        }
        leakage = leakage or any(g["leakage_detected"] for g in groups)
        write_json(output_dir / f"{split_name}.json", payload)

    too_small = len(rows) < MIN_GATE4_SESSIONS
    ok = not dupes and not leakage and (allow_small or not too_small)
    summary = {
        "schema_name": "gunnchos.gate4_split_summary",
        "schema_version": "1.0.0",
        "ok": ok,
        "evaluation_label": evaluation_label(manifest),
        "sample_count": len(rows),
        "minimum_gate4_sessions": MIN_GATE4_SESSIONS,
        "allow_small": allow_small,
        "too_small": too_small,
        "leakage_detected": leakage,
        "duplicate_hashes": dupes,
        "split_types": SPLIT_TYPES,
        "generated_at": utc_now(),
        "limitations": [
            "Small synthetic/calibration split sets are valid only for infrastructure validation."
            if allow_small
            else "Dataset must meet Gate 4 minimum sample size for evaluation."
        ],
    }
    write_json(output_dir / "split_summary.json", summary)
    return summary


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--allow-small", action="store_true")
    p.add_argument("--write-synthetic-manifest", action="store_true")
    args = p.parse_args(argv)
    dataset = Path(args.dataset)
    if args.write_synthetic_manifest and not dataset.exists():
        write_json(dataset, synthetic_manifest(dataset))
    manifest = load_dataset_manifest(dataset)
    summary = build_splits(manifest, Path(args.output_dir), allow_small=args.allow_small)
    print(json.dumps(summary, indent=2))
    return 0 if summary["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
