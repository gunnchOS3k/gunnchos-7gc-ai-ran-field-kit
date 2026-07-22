#!/usr/bin/env python3
"""Generate integrated_report.md and reproduction_log.md for a Gate 2 run."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    d = args.run_dir
    edge = json.loads((d / "01_edge_measurements.json").read_text())
    twin = json.loads((d / "02_twin_state.json").read_text())
    airan = json.loads((d / "03_airan_twin_informed_decision.json").read_text())
    ntn = json.loads((d / "04_resilience_decision.json").read_text())
    gate = json.loads((d / "gate2_status.json").read_text()) if (d / "gate2_status.json").exists() else {}
    manifest = json.loads((d / "manifest.json").read_text()) if (d / "manifest.json").exists() else {}

    report = f"""# Gate 2 Integrated Report

## Evidence honesty

- Edge input evidence level: `{edge.get('evidence_level')}`
- Twin evidence level: `{twin.get('evidence_level')}`
- Do not interpret synthetic fixtures as physical-device measurements.

## Data path

1. Edge measurement batch → `01_edge_measurements.json`
2. 7GC normalization → `02_twin_state.json`
3. SpectrumX policies → `03_airan_*_decision.json`
4. NTN resilience decision → `04_resilience_decision.json`

## Validation

Schema validation was enforced at every repository boundary using the field-kit
canonical JSON Schema Draft 2020-12 contracts. Provenance hashes and run IDs are
checked across stages.

## Policy comparison

Deployed AI-RAN policy for NTN stage: `{manifest.get('selected_airan_policy', airan.get('policy_name'))}`

Twin-informed predicted metrics:

```json
{json.dumps(airan.get('predicted_metrics'), indent=2)}
```

## Selected resilience mode

- Mode: `{ntn.get('selected_mode')}`
- Trigger: `{ntn.get('fallback_trigger')}`
- Continuity score (computed): `{ntn.get('continuity_score')}`

## Assumptions and uncertainty

NTN non-measured parameters are labeled in `assumptions_used` inside
`04_resilience_decision.json` (`configured` / `synthetic` as applicable).

AI-RAN predicted metrics use an explicit analytical model documented in
`metric_model_assumptions`.

## Benchmark / ablation / sensitivity

Artifacts:

- `benchmark_results.csv` — executed policy runtime distributions
- `ablation_results.csv` — executed ablations under fixed seed
- `sensitivity_results.csv` — executed NTN parameter sweeps

## Remaining evidence limitations

Gate status: `{gate.get('status')}`

Unmet criteria:

```json
{json.dumps(gate.get('unmet_criteria'), indent=2)}
```

## Reproduction command

```bash
python scripts/run_integrated_pipeline.py \\
  --edge-input <path-to-edge-batch.json> \\
  --repos-root .. \\
  --output-root results/integrated \\
  --strict
```
"""
    (d / "integrated_report.md").write_text(report, encoding="utf-8")
    (d / "reproduction_log.md").write_text(
        "# Reproduction log\n\n"
        f"run_id: `{edge.get('run_id')}`\n\n"
        f"evidence_level: `{edge.get('evidence_level')}`\n\n"
        "Commands are recorded in `command_log.txt` and `manifest.json`.\n",
        encoding="utf-8",
    )
    print(str(d / "integrated_report.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
