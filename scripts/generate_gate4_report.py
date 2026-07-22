#!/usr/bin/env python3
"""Generate Gate 4 JSON and Markdown reports."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate4_common import load_json, read_csv, write_json  # noqa: E402


def generate(run_dir: Path, status_json: Path, output_dir: Path) -> dict:
    status = load_json(status_json)
    split_summary = load_json(run_dir / "splits" / "split_summary.json")
    uncertainty = load_json(run_dir / "raw_results" / "uncertainty_report.json")
    table_rows = read_csv(run_dir / "tables" / "gate4_summary_table.csv")
    report = {
        **status,
        "schema_name": "gunnchos.gate4_evaluation_report",
        "schema_version": "1.0.0",
        "split_summary": split_summary,
        "uncertainty": uncertainty,
        "table_row_count": len(table_rows),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "gate4_evaluation_report.json", report)
    md = f"""# Gate 4 Evaluation Report

Status: **{report.get('gate4_status')}**

Evaluation label: `{report.get('evaluation_label')}`

Inference label: `{report.get('inference_label')}`

Sample count: `{report.get('sample_count')}`

## Missing requirements

```json
{json.dumps(report.get('missing_requirements'), indent=2)}
```

## Evidence honesty

- Synthetic and calibration-only fixtures are infrastructure validation only.
- Synthetic/calibration artifacts cannot produce `GATE_3_PASS` or `GATE_4_PASS`.
- `oracle_hindsight_analysis_only` is retained for analysis and is never deployable.

## Uncertainty

```json
{json.dumps(uncertainty, indent=2)}
```

## Limitations

```json
{json.dumps(report.get('limitations'), indent=2)}
```
"""
    (output_dir / "GATE4_EVALUATION_REPORT.md").write_text(md, encoding="utf-8")
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--run-dir", required=True)
    p.add_argument("--status-json", required=True)
    p.add_argument("--output-dir", required=True)
    args = p.parse_args(argv)
    report = generate(Path(args.run_dir), Path(args.status_json), Path(args.output_dir))
    print(json.dumps({"gate4_status": report["gate4_status"], "report": str(Path(args.output_dir) / "GATE4_EVALUATION_REPORT.md")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
