#!/usr/bin/env python3
"""Generate Gate 4 summary tables from raw CSV results."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate4_common import read_csv, write_csv


def generate(raw_results_dir: Path, output_dir: Path) -> dict:
    rows = []
    for name in ["baseline_results.csv", "ablation_results.csv", "sensitivity_results.csv", "failure_boundaries.csv"]:
        for row in read_csv(raw_results_dir / name):
            rows.append(
                {
                    "source_file": name,
                    "component": row.get("component") or "failure_boundary",
                    "condition": row.get("condition") or row.get("parameter"),
                    "metric": row.get("metric") or row.get("boundary_metric"),
                    "value": row.get("value") or row.get("boundary_value"),
                    "evaluation_label": row.get("evaluation_label"),
                    "inference_label": row.get("inference_label"),
                }
            )
    csv_path = output_dir / "gate4_summary_table.csv"
    write_csv(csv_path, rows)
    md_path = output_dir / "gate4_summary_table.md"
    md_path.write_text(
        "# Gate 4 Summary Table\n\n"
        "| source | component | condition | metric | value | label |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        + "\n".join(
            "| {source_file} | {component} | {condition} | {metric} | {value} | {evaluation_label}/{inference_label} |".format(
                **row
            )
            for row in rows[:80]
        )
        + "\n",
        encoding="utf-8",
    )
    return {"rows": len(rows), "csv": str(csv_path), "markdown": str(md_path)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--raw-results-dir", required=True)
    p.add_argument("--output-dir", required=True)
    args = p.parse_args(argv)
    result = generate(Path(args.raw_results_dir), Path(args.output_dir))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
