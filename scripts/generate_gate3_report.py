#!/usr/bin/env python3
"""Generate Gate 3 evidence report markdown + JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--status-json", required=True)
    p.add_argument("--coverage-json", required=True)
    p.add_argument("--output-dir", required=True)
    args = p.parse_args(argv)
    status = json.loads(Path(args.status_json).read_text(encoding="utf-8"))
    coverage = json.loads(Path(args.coverage_json).read_text(encoding="utf-8"))
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    report = {
        **status,
        "descriptive_tables": {
            "note": "Descriptive pilot evidence only; not causal evaluation.",
            "rejected_sessions": coverage.get("rejected", []),
            "missing_cells": coverage.get("missing_cells", []),
        },
        "integrated_run_ids": status.get("integrated_run_ids", []),
    }
    (out / "gate3_evidence_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = f"""# GATE3 Evidence Report

Status: **{report.get('gate3_status')}**

## Required vs observed

```json
{json.dumps({'required': report.get('required_counts'), 'observed': report.get('observed_counts')}, indent=2)}
```

## Missing requirements

```json
{json.dumps(report.get('missing_requirements'), indent=2)}
```

## Evidence honesty

- Physical sessions counted only when `evidence_level=controlled_device_measurement` and collector is not the emulator.
- Synthetic fixtures do not satisfy Gate 3.
- Label: descriptive pilot evidence (not publication-grade causal evaluation).

## External / source-validated evidence

`{report.get('external_evidence_status')}`

## Limitations

```json
{json.dumps(report.get('limitations'), indent=2)}
```
"""
    (out / "GATE3_EVIDENCE_REPORT.md").write_text(md, encoding="utf-8")
    print(str(out / "gate3_evidence_report.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
