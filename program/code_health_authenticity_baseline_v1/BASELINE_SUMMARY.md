# Code Health & Implementation Authenticity Baseline V1

**Result:** `BASELINE_COMPLETE_WITH_FINDINGS`

Generated: 2026-08-21T18:12:36Z

## Prerequisite (frozen, unmodified)
- field-kit #113 MERGED
- Baseline 419 / COMPLETE=111 / IMPL_OPEN=51 / VALIDATION_OPEN=0 / EVIDENCE_MAPPING=0 / POOL=162
- NEXT_VALIDATION total_open=0; NEXT_IMPL total_open=51

## Calibration
- S0/S1 totals = root causes (not raw regex hits)
- Raw pattern observations: 369
- S0_REGEX_ONLY_COUNT=0; S0_SEMANTIC_REVIEW_COMPLETE=True
- S1 sample fraction=0.5; FP rate=0.0

## Totals
- Repos scanned: 17/17
- Findings: 29 (S0=0, S1=2) [root causes]
- Critical dimension cells: 12

## Critical / high repos
- `7gc-digital-twin`
- `edge-io-measurement-node`
- `gunnchos-7gc-ai-ran-field-kit`
- `gunnchos-device-os`
- `gunnchos-hardware-industrial-design`
- `gunnchos-research-portal`
- `ntn-resilience-sim`
- `pedestrian-pursuit`
- `spectrumx-ai-ran-gary`
- `waike-research-ops`

## Dimension matrix
See `DIMENSION_MATRIX.json` — ratings only, no fake aggregate %.

## Outputs
- Per-repo maps: `reports/repos/<repo>/`
- UML: `uml/current`, `uml/rendered`
- Remediation families R1–R8: `REMEDIATION_REGISTER.md`
- Calibration: `RAW_PATTERN_OBSERVATIONS.json`, `S0_SEMANTIC_REVIEW.json`, `S1_CALIBRATION_REVIEW.json`, `AUDIT_FALSE_POSITIVE_CONTROLS.json`

Findings are not hidden to preserve a green result.
