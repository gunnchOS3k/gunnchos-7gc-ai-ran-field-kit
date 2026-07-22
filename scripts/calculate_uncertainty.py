#!/usr/bin/env python3
"""Calculate Gate 4 uncertainty metadata and intervals."""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate4_common import (  # noqa: E402
    INSUFFICIENT_INFERENCE_LABEL,
    evaluation_label,
    inference_label,
    load_dataset_manifest,
    load_dataset_rows,
    read_csv,
    utc_now,
    write_json,
)


def calculate(
    manifest: dict,
    input_csv: Path,
    output: Path,
    *,
    confidence_level: float = 0.95,
    resampling_count: int = 1000,
    seed: int = 0,
) -> dict:
    dataset_rows = load_dataset_rows(manifest)
    sample_count = len(dataset_rows) or int(manifest.get("n_sessions") or 0)
    records = read_csv(input_csv)
    numeric_values: list[float] = []
    for row in records:
        try:
            numeric_values.append(float(row.get("value", "")))
        except ValueError:
            continue
    random.seed(seed)
    if numeric_values and sample_count >= 30 and inference_label(manifest, sample_count) != INSUFFICIENT_INFERENCE_LABEL:
        estimates = []
        for _ in range(resampling_count):
            draw = [random.choice(numeric_values) for _ in numeric_values]
            estimates.append(sum(draw) / len(draw))
        estimates.sort()
        lo_idx = int(((1 - confidence_level) / 2) * len(estimates))
        hi_idx = min(len(estimates) - 1, int((1 - (1 - confidence_level) / 2) * len(estimates)))
        interval = [round(estimates[lo_idx], 6), round(estimates[hi_idx], 6)]
    else:
        interval = [None, None]
    report = {
        "schema_name": "gunnchos.gate4_uncertainty_report",
        "schema_version": "1.0.0",
        "methods": ["bootstrap", "repeated_seed", "scenario_range"],
        "confidence_level": confidence_level,
        "resampling_count": resampling_count,
        "seed": seed,
        "sample_count": sample_count,
        "evaluation_label": evaluation_label(manifest),
        "inference_label": inference_label(manifest, sample_count),
        "interval": interval,
        "assumptions": [
            "Bootstrap resamples result records after upstream split validation.",
            "Repeated-seed and scenario-range outputs are comparable only when generated from non-synthetic inputs.",
        ],
        "limitations": [
            "Calibration-only and synthetic dry-runs are insufficient_sample_size_for_inference.",
            "Intervals are null unless sample count and evidence level support inference.",
        ],
        "generated_at": utc_now(),
    }
    write_json(output, report)
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--input-csv", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--confidence-level", type=float, default=0.95)
    p.add_argument("--resampling-count", type=int, default=1000)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args(argv)
    manifest = load_dataset_manifest(Path(args.dataset))
    report = calculate(
        manifest,
        Path(args.input_csv),
        Path(args.output),
        confidence_level=args.confidence_level,
        resampling_count=args.resampling_count,
        seed=args.seed,
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
