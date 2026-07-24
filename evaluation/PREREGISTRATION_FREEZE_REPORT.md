# Preregistration Freeze Report

Frozen at: `2026-07-24T15:04:05Z`  
Status: **PASS**

## Evidence

- Metric calculator: `scripts/compute_recovery_time.py`
- Tests: `tests/evaluation/test_recovery_time_metric.py`
- Manifest: `evaluation/PREREGISTRATION_MANIFEST.json`
- Checksums: `evaluation/PREREGISTRATION_CHECKSUMS.sha256`
- Primary lock SHA-256: `bcf035b67e88f4fcc25284b5dab3d53101ae7a38e65e00703f8ff7e37c0290f9`

## Verification performed

- `recovery_time_s` measurable from frozen `edge_measurement_batch.v1` fields
- Distinct from model `expected_recovery_time_s`
- Baselines, ablations, holdouts, SAP, thresholds present
- No authentic full-pilot results inspected (0/54)

## Gate update

`EVALUATION_PREREGISTERED = PASS`
