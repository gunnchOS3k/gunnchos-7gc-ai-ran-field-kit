#!/usr/bin/env python3
"""Generate Gate 4 ablation records."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate4_common import (  # noqa: E402
    ABLATIONS,
    deterministic_score,
    evaluation_label,
    inference_label,
    load_dataset_manifest,
    load_dataset_rows,
    write_csv,
)


def run(manifest: dict, output: Path, *, experiment_id: str) -> list[dict]:
    sample_count = len(load_dataset_rows(manifest)) or int(manifest.get("n_sessions") or 0)
    eval_label = evaluation_label(manifest)
    inf_label = inference_label(manifest, sample_count)
    rows = []
    for ablation in ABLATIONS:
        rows.append(
            {
                "schema_name": "gunnchos.gate4_result_record",
                "schema_version": "1.0.0",
                "experiment_id": experiment_id,
                "component": "ablation",
                "condition": ablation,
                "metric": "service_continuity_delta",
                "value": round(deterministic_score(ablation, sample_count) - 0.5, 4),
                "unit": "delta_score",
                "evaluation_label": eval_label,
                "inference_label": inf_label,
                "privacy_controls_active": "true",
                "notes": "Privacy ablation toggles a simulated decision constraint only; actual privacy controls remain active."
                if "privacy_constraint" in ablation
                else "Dry-run ablation record is an infrastructure check, not a physical measurement."
                if eval_label == "infrastructure_validation_only"
                else "Computed by Gate 4 ablation harness.",
            }
        )
    write_csv(output, rows)
    return rows


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--experiment-id", default="gate4-experiment")
    args = p.parse_args(argv)
    manifest = load_dataset_manifest(Path(args.dataset))
    rows = run(manifest, Path(args.output), experiment_id=args.experiment_id)
    print(json.dumps({"wrote": args.output, "records": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
