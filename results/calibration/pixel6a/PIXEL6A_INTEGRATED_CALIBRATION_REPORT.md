# PIXEL6A_INTEGRATED_CALIBRATION_REPORT

## Result

Integrated chain: **PASS** (automated pipeline) for calibration-only Pixel session.

| Field | Value |
|---|---|
| Run ID | `pixel-cal-1784756973874` |
| Evidence | controlled_device_measurement |
| calibration_only | true (excluded from pilot) |
| Gate2 automated status | `AUTOMATED_PIPELINE_PASS` |
| Selected AI-RAN policy | twin_informed |
| Resilience mode | `terrestrial` |
| Scientific conclusion | **None drawn** — single calibration |

## Artifacts

Relative to `results/calibration/pixel6a/integrated/pixel-cal-1784756973874/`:

- `01_edge_measurements.json`
- `02_twin_state.json`
- `03_airan_static_decision.json`
- `03_airan_network_only_decision.json`
- `03_airan_service_priority_decision.json`
- `03_airan_optimization_decision.json`
- `03_airan_twin_informed_decision.json`
- `04_resilience_decision.json`
- `manifest.json`
- `checksums.sha256`
- `validation_report.json`

## Notes

- Repo-lock warnings expected while continuation branches differ from locked main SHAs.
- 7GC twin required a null-metric aggregation fix for physical unavailable fields.
- Raw/sanitized measurement JSON are not committed.
