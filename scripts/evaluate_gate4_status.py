#!/usr/bin/env python3
"""Evaluate Gate 4 status from generated artifacts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate4_common import evaluate_artifact_status, load_dataset_manifest, load_json, write_json  # noqa: E402


def evaluate(dataset: Path, run_dir: Path, output: Path | None = None) -> dict:
    manifest = load_dataset_manifest(dataset)
    split_summary_path = run_dir / "splits" / "split_summary.json"
    split_summary = load_json(split_summary_path) if split_summary_path.is_file() else {"ok": False}
    sample_count = int(split_summary.get("sample_count") or manifest.get("n_sessions") or 0)
    status = evaluate_artifact_status(
        manifest=manifest,
        sample_count=sample_count,
        split_summary=split_summary,
        run_dir=run_dir,
    )
    if output:
        write_json(output, status)
    return status


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--run-dir", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args(argv)
    status = evaluate(Path(args.dataset), Path(args.run_dir), Path(args.output))
    print(json.dumps(status, indent=2))
    return 0 if status["gate4_status"] != "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
