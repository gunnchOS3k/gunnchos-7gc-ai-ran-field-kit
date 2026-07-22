# Gate 4 Evaluation Report

Status: **GATE4_EVALUATION_READY**

Evaluation label: `infrastructure_validation_only`

Inference label: `insufficient_sample_size_for_inference`

Sample count: `6`

## Missing requirements

```json
[
  "insufficient_sample_size_for_inference",
  "sample_count_below_gate4_minimum",
  "synthetic_or_calibration_run_not_eligible_for_gate4_pass"
]
```

## Evidence honesty

- Synthetic and calibration-only fixtures are infrastructure validation only.
- Synthetic/calibration artifacts cannot produce `GATE_3_PASS` or `GATE_4_PASS`.
- `oracle_hindsight_analysis_only` is retained for analysis and is never deployable.

## Uncertainty

```json
{
  "schema_name": "gunnchos.gate4_uncertainty_report",
  "schema_version": "1.0.0",
  "methods": [
    "bootstrap",
    "repeated_seed",
    "scenario_range"
  ],
  "confidence_level": 0.95,
  "resampling_count": 1000,
  "seed": 0,
  "sample_count": 6,
  "evaluation_label": "infrastructure_validation_only",
  "inference_label": "insufficient_sample_size_for_inference",
  "interval": [
    null,
    null
  ],
  "assumptions": [
    "Bootstrap resamples result records after upstream split validation.",
    "Repeated-seed and scenario-range outputs are comparable only when generated from non-synthetic inputs."
  ],
  "limitations": [
    "Calibration-only and synthetic dry-runs are insufficient_sample_size_for_inference.",
    "Intervals are null unless sample count and evidence level support inference."
  ],
  "generated_at": "2026-07-22T17:03:51Z"
}
```

## Limitations

```json
[
  "Synthetic and calibration-only fixtures never produce GATE_4_PASS.",
  "Oracle hindsight resilience baseline is analysis-only and never deployable.",
  "GATE_4_PASS requires eligible non-synthetic data, no leakage, no duplicate hashes, and sufficient sample size."
]
```
