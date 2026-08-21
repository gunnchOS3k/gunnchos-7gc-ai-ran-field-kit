# SECTION 28 — Code Health & Implementation Authenticity Baseline V1 Report

Generated: 2026-08-21T18:12:36Z
**CODE_HEALTH_AUTHENTICITY_BASELINE_V1=`BASELINE_COMPLETE_WITH_FINDINGS`**
**CODE_HEALTH_BASELINE_V1_CALIBRATION_REPAIR=`COMPLETE_PENDING_OWNER_MERGE`**
**CODE_HEALTH_BASELINE_V1_FINAL_TRUTH_CONVERGENCE=`COMPLETE_PENDING_OWNER_MERGE`**

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
- Mutation classifier controls: `True`
- Calibration flags: `{"VENDORED_ENVIRONMENT_PATHS_EXCLUDED_FROM_S0_S1": true, "LEGACY_REQUIRES_ACTIVE_REACHABILITY_FOR_S0_S1": true, "S0_REQUIRES_CAPABILITY_CLOSURE_PATH": true, "ASSERT_TRUE_TOKEN_ALONE_NOT_S0": true, "PASS_TODO_TOKEN_ALONE_NOT_S1": true, "ROOT_CAUSE_DEDUPLICATION": true, "ARTIFACT_PATH_NOT_AUTOMATICALLY_ACTIVE": true, "FULL_TEST_RUN_REQUIRED_FOR_MUTATION_SURVIVAL": true, "COLLECTION_ONLY_NOT_SURVIVAL": true, "LIKELY_UNDETECTED_NOT_SURVIVAL": true, "NO_TESTS_DIR_NOT_SURVIVAL": true, "BEHAVIORAL_MUTATION_REQUIRED": true, "MARKER_MUTATIONS_COUNT_AS_SURVIVAL": false, "MUTATION_SURVIVAL_REQUIRES_EXECUTED_RELEVANT_TESTS": true, "APPEND_MARKER_REQUIRES_BEHAVIORAL_EFFECT": true}`

## 4. Top-level result (calibrated)
- Token: `BASELINE_COMPLETE_WITH_FINDINGS`
- Repos scanned: 17/17
- Raw pattern observations: 369
- Root-cause findings: 29 (S0=0, S1=2)
- Critical dimension cells: 12
- S0_REGEX_ONLY_COUNT=0; S0_SEMANTIC_REVIEW_COMPLETE=True
- S1 sample: n=1 frac=0.5 FP_rate=0.0 reviewed_all=False

## 5. Dimension matrix (no aggregate %)
See `DIMENSION_MATRIX.json`. CRITICAL anti_test_theater requires calibrated S0 root causes.

## 6. Proof independence
- Statuses: `{'PASS_INDEPENDENT': 17}`
- PROOF_INDEPENDENCE_RUNTIME_MATRIX_CONTRADICTIONS=0

## 7. Anti-test-theater (calibrated root causes)
- S0 root causes: 0
- S1 root causes: 2

## 8. Mutation resistance sampling
- Dimensions: {'NEEDS_WORK': 14, 'CRITICAL': 2, 'NOT_APPLICABLE': 1}
- Outcomes: {'MUTATION_TEST_NOT_EXECUTED': 11, 'MUTATION_SURVIVED': 2, 'INVALID_MUTATION_SAMPLE': 1, 'MUTATION_VALIDATION_INCOMPLETE': 3}
- R5 `gunnchos-research-portal`: outcome=`MUTATION_SURVIVED` dim=`CRITICAL`
- R5 `7gc-digital-twin`: outcome=`MUTATION_VALIDATION_INCOMPLETE` dim=`NEEDS_WORK`
- R5 `readygary-6g-beam-selection`: outcome=`MUTATION_VALIDATION_INCOMPLETE` dim=`NEEDS_WORK`
- R5 `waike-research-ops`: outcome=`MUTATION_SURVIVED` dim=`CRITICAL`
- R5 `gunnchos-emergent-service-intent-protocols`: outcome=`MUTATION_VALIDATION_INCOMPLETE` dim=`NEEDS_WORK`

## 9. Remediation families R1–R8 (from root causes)
- `R1` Production/proof coupling: 0 items
- `R2` Test theater (S0/S1): 0 items
- `R3` Wave/canonical duplicate implementations: 5 items
- `R4` Runtime-path inauthenticity: 0 items
- `R5` Mutation blindness: 5 items
- `R6` Complexity / hotspot debt: 12 items
- `R7` Orphan/dead code & fixture honesty: 7 items
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

## 13. Mutation calibration (R5 focus)
- `gunnchos-research-portal` sha=`afb2bab2b415` outcome=`MUTATION_SURVIVED` killed=1 survived=1
  - flip_return_zero `scripts/validate_supervisor_ready.py` → `MUTATION_KILLED` (full_run=True baseline=True mutated=False)
  - flip_return_zero `scripts/audit_portfolio.py` → `MUTATION_SURVIVED` (full_run=True baseline=True mutated=True)
- `7gc-digital-twin` sha=`4cd70169b35a` outcome=`MUTATION_VALIDATION_INCOMPLETE` killed=0 survived=0
  - flip_return_true `src/seven_gc_twin/scene/osm_overpass.py` → `MUTATION_VALIDATION_INCOMPLETE` (full_run=True baseline=False mutated=False)
  - flip_return_zero `src/seven_gc_twin/cli.py` → `MUTATION_VALIDATION_INCOMPLETE` (full_run=True baseline=False mutated=False)
  - invert_condition `src/seven_gc_twin/continuity_benchmark.py` → `MUTATION_VALIDATION_INCOMPLETE` (full_run=True baseline=False mutated=False)
- `readygary-6g-beam-selection` sha=`569875224db7` outcome=`MUTATION_VALIDATION_INCOMPLETE` killed=0 survived=0
  - flip_return_true `sim/experiments/digital_programme.py` → `MUTATION_VALIDATION_INCOMPLETE` (full_run=True baseline=False mutated=False)
  - flip_return_zero `scripts/run_benchmark_table.py` → `MUTATION_VALIDATION_INCOMPLETE` (full_run=True baseline=False mutated=False)
  - flip_return_zero `scripts/run_timing_harness.py` → `MUTATION_VALIDATION_INCOMPLETE` (full_run=True baseline=False mutated=False)
- `waike-research-ops` sha=`5d416c09164c` outcome=`MUTATION_SURVIVED` killed=1 survived=2
  - flip_return_zero `src/waike_curriculum/evaluation/metrics.py` → `MUTATION_SURVIVED` (full_run=True baseline=True mutated=True)
  - remove_validation `src/waike_course_ready/batch002/exams.py` → `MUTATION_SURVIVED` (full_run=True baseline=True mutated=True)
  - invert_condition `src/waike_course_ready/batch002/labs.py` → `MUTATION_KILLED` (full_run=True baseline=True mutated=False)
- `gunnchos-emergent-service-intent-protocols` sha=`088c5e88e155` outcome=`MUTATION_VALIDATION_INCOMPLETE` killed=0 survived=0
  - invert_condition `src/emergent_intent/algorithms/trainers.py` → `MUTATION_VALIDATION_INCOMPLETE` (full_run=True baseline=False mutated=False)
  - flip_return_zero `src/emergent_intent/env/wireless_env.py` → `MUTATION_VALIDATION_INCOMPLETE` (full_run=True baseline=False mutated=False)
  - invert_condition `src/emergent_intent/abstraction/encoders.py` → `MUTATION_VALIDATION_INCOMPLETE` (full_run=True baseline=False mutated=False)

## 14. Truth contradictions corrected
- PROOF↔RUNTIME contradictions: 0
- PRODUCTION_PROOF_COUPLING_ROOT_CAUSES: []
- KNOWN_ACTIVE_CODE_CLASSIFIED_ORPHAN: 0
- VENDORED_ENVIRONMENT_COMPLEXITY_HOTSPOTS: 0
- Remaining CONFIRMED_ORPHAN sample: []

## 15. FINAL TRUTH CONVERGENCE
- Token: `CODE_HEALTH_BASELINE_V1_TRUTH_CONVERGENCE_VALIDATION_PASS`
- TRUTH_CONVERGENCE_VALIDATION: `PASS`
- CANONICAL_REPOS_AUDITED=17
- BASELINE_COUNTS_CHANGED=False
- REQUIREMENT_STATES_CHANGED=0
- OTHER_REPO_MUTATIONS=0
- S0=0 S1=2
- Cursor merged nothing.
