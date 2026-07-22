#!/usr/bin/env python3
"""Generate Gate 4 failure-boundary artifacts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate4_common import (  # noqa: E402
    SENSITIVITY_PARAMETERS,
    deterministic_score,
    evaluation_label,
    inference_label,
    load_dataset_manifest,
    load_dataset_rows,
    utc_now,
    write_csv,
)


def analyze(manifest: dict, output_csv: Path, report_md: Path, *, experiment_id: str) -> list[dict]:
    sample_count = len(load_dataset_rows(manifest)) or int(manifest.get("n_sessions") or 0)
    eval_label = evaluation_label(manifest)
    inf_label = inference_label(manifest, sample_count)
    rows = []
    for parameter in SENSITIVITY_PARAMETERS:
        threshold = round(1.0 - deterministic_score(parameter, sample_count), 4)
        rows.append(
            {
                "experiment_id": experiment_id,
                "parameter": parameter,
                "boundary_metric": "first_threshold_where_policy_degrades",
                "boundary_value": threshold,
                "unit": "normalized",
                "evaluation_label": eval_label,
                "inference_label": inf_label,
                "action": "record_for_followup",
            }
        )
    write_csv(output_csv, rows)
    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_md.write_text(
        "# Failure Boundary Report\n\n"
        f"Generated: {utc_now()}\n\n"
        f"Evaluation label: `{eval_label}`\n\n"
        f"Inference label: `{inf_label}`\n\n"
        "These boundaries are retained to expose regimes where policies degrade. "
        "For synthetic/calibration dry-runs they validate report plumbing only and "
        "must not be interpreted as physical measurements.\n",
        encoding="utf-8",
    )
    return rows


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--output-csv", required=True)
    p.add_argument("--report-md", required=True)
    p.add_argument("--experiment-id", default="gate4-experiment")
    args = p.parse_args(argv)
    manifest = load_dataset_manifest(Path(args.dataset))
    rows = analyze(manifest, Path(args.output_csv), Path(args.report_md), experiment_id=args.experiment_id)
    print(json.dumps({"wrote": args.output_csv, "records": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
