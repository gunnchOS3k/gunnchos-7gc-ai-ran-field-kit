#!/usr/bin/env python3
"""Write a Gate 4 negative/neutral results register."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate4_common import evaluation_label, inference_label, load_dataset_manifest, load_dataset_rows, utc_now


def generate(manifest: dict, output: Path, *, experiment_id: str) -> dict:
    sample_count = len(load_dataset_rows(manifest)) or int(manifest.get("n_sessions") or 0)
    eval_label = evaluation_label(manifest)
    inf_label = inference_label(manifest, sample_count)
    entries = [
        {
            "id": "gate4-neutral-001",
            "outcome": "neutral",
            "description": "Readiness dry-run verifies evaluation plumbing without claiming performance gain.",
        },
        {
            "id": "gate4-negative-001",
            "outcome": "negative",
            "description": "Any split leakage or duplicate session hash blocks Gate 4 status.",
        },
        {
            "id": "gate4-negative-002",
            "outcome": "negative",
            "description": "Oracle hindsight baseline remains analysis-only and never deployable.",
        },
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "# Negative Results Register\n\n"
        f"Experiment: `{experiment_id}`\n\n"
        f"Generated: {utc_now()}\n\n"
        f"Evaluation label: `{eval_label}`\n\n"
        f"Inference label: `{inf_label}`\n\n"
        "| id | outcome | description |\n"
        "| --- | --- | --- |\n"
        + "\n".join(f"| {e['id']} | {e['outcome']} | {e['description']} |" for e in entries)
        + "\n",
        encoding="utf-8",
    )
    return {"entries": entries, "evaluation_label": eval_label, "inference_label": inf_label}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--experiment-id", default="gate4-experiment")
    args = p.parse_args(argv)
    result = generate(load_dataset_manifest(Path(args.dataset)), Path(args.output), experiment_id=args.experiment_id)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
