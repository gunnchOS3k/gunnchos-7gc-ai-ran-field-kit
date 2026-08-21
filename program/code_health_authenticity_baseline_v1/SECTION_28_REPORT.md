# SECTION 28 — Code Health & Implementation Authenticity Baseline V1 Report

Generated: 2026-08-21T17:48:03Z
**CODE_HEALTH_AUTHENTICITY_BASELINE_V1=`BASELINE_COMPLETE_WITH_FINDINGS`**
**CODE_HEALTH_BASELINE_V1_CALIBRATION_REPAIR=`COMPLETE_PENDING_OWNER_MERGE`**

## 1. Prerequisite
- field-kit #113 MERGED (`556f2815a0b3`)
- Baseline frozen unmodified: 419 / COMPLETE=111 / IMPL_OPEN=51 / VALIDATION_OPEN=0 / EVIDENCE_MAPPING=0 / POOL=162
- NEXT_VALIDATION total_open=0; NEXT_IMPL total_open=51

## 2. Accepted-main manifest (17)
- `gunnchos-7gc-ai-ran-field-kit` `556f2815a0b3` live=True local_match=True
- `gunnchos-research-portal` `afb2bab2b415` live=True local_match=True
- `gunnchos-device-os` `28562a845620` live=True local_match=True
- `gunnchos-hardware-industrial-design` `9ee0ef2f688b` live=True local_match=True
- `gunnchAI3k` `4b4f411710e8` live=True local_match=True
- `edge-io-measurement-node` `af57fbdac857` live=True local_match=True
- `anime-aggressors` `0afe3079db47` live=True local_match=True
- `pedestrian-pursuit` `3f8fdb5f0f2f` live=True local_match=True
- `archive-of-life-artifact-world` `069243c36555` live=True local_match=True
- `beatlink-party` `23a95d152c2d` live=True local_match=True
- `7gc-digital-twin` `4cd70169b35a` live=True local_match=True
- `spectrumx-ai-ran-gary` `cef3900af100` live=True local_match=True
- `ntn-resilience-sim` `916520919bea` live=True local_match=True
- `readygary-6g-beam-selection` `569875224db7` live=True local_match=True
- `waike-research-ops` `5d416c09164c` live=True local_match=True
- `gunnchos-emergent-service-intent-protocols` `088c5e88e155` live=True local_match=True
- `gunnchos-gpu-nr-baseband-platform` `3931f51d43b7` live=True local_match=True

## 3. Audit integrity + FP controls
- Audit integrity: `PASS`
- FP controls: `PASS`
- Calibration flags: `{"VENDORED_ENVIRONMENT_PATHS_EXCLUDED_FROM_S0_S1": true, "LEGACY_REQUIRES_ACTIVE_REACHABILITY_FOR_S0_S1": true, "S0_REQUIRES_CAPABILITY_CLOSURE_PATH": true, "ASSERT_TRUE_TOKEN_ALONE_NOT_S0": true, "PASS_TODO_TOKEN_ALONE_NOT_S1": true, "ROOT_CAUSE_DEDUPLICATION": true, "ARTIFACT_PATH_NOT_AUTOMATICALLY_ACTIVE": true}`

## 4. Top-level result (calibrated)
- Token: `BASELINE_COMPLETE_WITH_FINDINGS`
- Repos scanned: 17/17
- Raw pattern observations: 369
- Root-cause findings: 35 (S0=0, S1=5)
- Critical dimension cells: 19
- S0_REGEX_ONLY_COUNT=0; S0_SEMANTIC_REVIEW_COMPLETE=True
- S1 sample: n=2 frac=0.4 FP_rate=0.0 reviewed_all=False

## 5. Dimension matrix (no aggregate %)
See `DIMENSION_MATRIX.json`. CRITICAL anti_test_theater requires calibrated S0 root causes.

## 6. Proof independence
- Statuses: `{'PASS_INDEPENDENT': 17}`

## 7. Anti-test-theater (calibrated root causes)
- S0 root causes: 0
- S1 root causes: 5

## 8. Mutation resistance sampling
- Dimensions: {'ADEQUATE': 4, 'CRITICAL': 5, 'NEEDS_WORK': 2, 'NOT_APPLICABLE': 6}
- CRITICAL sample: `gunnchos-research-portal`
- CRITICAL sample: `7gc-digital-twin`
- CRITICAL sample: `readygary-6g-beam-selection`
- CRITICAL sample: `waike-research-ops`
- CRITICAL sample: `gunnchos-emergent-service-intent-protocols`

## 9. Remediation families R1–R8 (from root causes)
- `R1` Production/proof coupling: 0 items
- `R2` Test theater (S0/S1): 0 items
- `R3` Wave/canonical duplicate implementations: 5 items
- `R4` Runtime-path inauthenticity: 4 items
- `R5` Mutation blindness: 5 items
- `R6` Complexity / hotspot debt: 12 items
- `R7` Orphan/dead code & fixture honesty: 9 items
- `R8` Docs/architecture truth drift: 0 items
- Baseline requirement counts unchanged.

## 10. Hard stops honored
- No product behavior changes in the 17 repos
- No requirement/Baseline count modifications
- No merges by Cursor
- No feature waves / census / portal refresh started

## 11. CI / PR
- Branch: `eng/code-health-authenticity-baseline-v1`
- PR: field-kit #114 (repair in place)
- Workflow: `Code Health & Authenticity Baseline`
- Make: `make code-health-authenticity-baseline`
- CI must not fail merely because genuine S0/S1 findings exist

## 12. Artifacts root
`program/code_health_authenticity_baseline_v1/`
