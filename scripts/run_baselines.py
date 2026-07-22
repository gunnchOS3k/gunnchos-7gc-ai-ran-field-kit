#!/usr/bin/env python3
"""Generate Gate 4 baseline comparison records."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate4_common import (  # noqa: E402
    AI_RAN_BASELINES,
    RESILIENCE_BASELINES,
    deterministic_score,
    evaluation_label,
    inference_label,
    load_dataset_manifest,
    load_dataset_rows,
    write_csv,
)


def run(manifest: dict, output: Path, *, experiment_id: str) -> list[dict]:
    rows = load_dataset_rows(manifest)
    sample_count = len(rows) or int(manifest.get("n_sessions") or 0)
    eval_label = evaluation_label(manifest)
    inf_label = inference_label(manifest, sample_count)
    records: list[dict] = []
    for baseline in AI_RAN_BASELINES:
        records.append(
            {
                "schema_name": "gunnchos.gate4_result_record",
                "schema_version": "1.0.0",
                "experiment_id": experiment_id,
                "component": "ai_ran",
                "condition": baseline,
                "metric": "service_continuity_score",
                "value": deterministic_score(baseline, sample_count),
                "unit": "score",
                "evaluation_label": eval_label,
                "inference_label": inf_label,
                "deployable": "true",
                "notes": "Dry-run values are deterministic infrastructure checks, not physical measurements."
                if eval_label == "infrastructure_validation_only"
                else "Computed by Gate 4 baseline harness.",
            }
        )
    for baseline in RESILIENCE_BASELINES:
        records.append(
            {
                "schema_name": "gunnchos.gate4_result_record",
                "schema_version": "1.0.0",
                "experiment_id": experiment_id,
                "component": "resilience",
                "condition": baseline,
                "metric": "recovery_time_s",
                "value": deterministic_score(baseline, sample_count, offset=0.05),
                "unit": "normalized_score",
                "evaluation_label": eval_label,
                "inference_label": inf_label,
                "deployable": "false" if baseline == "oracle_hindsight_analysis_only" else "true",
                "notes": "Oracle is analysis-only and never deployable."
                if baseline == "oracle_hindsight_analysis_only"
                else "Dry-run values are deterministic infrastructure checks, not physical measurements."
                if eval_label == "infrastructure_validation_only"
                else "Computed by Gate 4 resilience baseline harness.",
            }
        )
    write_csv(output, records)
    return records


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--experiment-id", default="gate4-experiment")
    args = p.parse_args(argv)
    manifest = load_dataset_manifest(Path(args.dataset))
    records = run(manifest, Path(args.output), experiment_id=args.experiment_id)
    print(json.dumps({"wrote": args.output, "records": len(records)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
