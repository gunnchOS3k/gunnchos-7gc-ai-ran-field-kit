# POST_MERGE_GATE3_TOPOLOGY_AUDIT

Generated: 2026-07-22T16:48:23.205063+00:00

## Summary

Gate 2 is present on each repository default branch. Gate 3 was merged into
`cursor/gate2-integrated-system-3ec5` (original Gate 3 PRs) but is **not**
reachable from `main`/`master`. Promotion PRs are required for all five
Gate 3 repositories. ReadyGary had no Gate 3 implementation PR.

| Repository | Default | Main SHA | Gate 2 on main | Gate 3 commit on main | Gate 3 merge on main | Promotion needed |
|---|---|---|---|---|---|---|
| edge-io-measurement-node | main | `c3f6fc38ed6c` | yes | no | no | YES |
| 7gc-digital-twin | main | `8fa2f729584e` | yes | no | no | YES |
| spectrumx-ai-ran-gary | main | `3030fcad25b6` | yes | no | no | YES |
| ntn-resilience-sim | main | `4170aca8af0c` | yes | no | no | YES |
| gunnchos-7gc-ai-ran-field-kit | master | `e06a9a89c216` | yes | no | no | YES |

## Per-repository detail

### edge-io-measurement-node

- **Current default tip:** `c3f6fc38ed6c3fd9887e8273b4d78890a81cc3c9`
- **Original Gate 3 PR:** #20
- **Approved Gate 3 commit:** `f8081ab4be8e702522dc35c1bf9b356f708844b1` (exists locally: True)
- **Gate 3 merge commit (into Gate 2 branch):** `0fd5225fa4f4cd8fd52097773c155dc7b4475b83`
- **Gate 2 commit present on default:** `9d04dd5bf3b726b21b76718ee80c7c2f5c6c18f7` → True
- **Gate 3 commit reachable from default:** False
- **Gate 3 patch already represented by different SHA on default:** False
- **Files changed in Gate 3 commit:** 18
- **Files mismatched vs default tip:** 18
- **Promotion needed:** True

Changed files:
- `.gitignore` (missing/mismatched on default)
- `Makefile` (missing/mismatched on default)
- `clients/android/app/build.gradle.kts` (missing/mismatched on default)
- `clients/android/app/src/main/AndroidManifest.xml` (missing/mismatched on default)
- `clients/android/app/src/main/java/org/gunnchos/edgeio/MainActivity.kt` (missing/mismatched on default)
- `clients/android/app/src/main/java/org/gunnchos/edgeio/SessionExporter.kt` (missing/mismatched on default)
- `clients/android/app/src/main/res/layout/activity_main.xml` (missing/mismatched on default)
- `clients/android/app/src/main/res/values/strings.xml` (missing/mismatched on default)
- `clients/android/app/src/main/res/values/themes.xml` (missing/mismatched on default)
- `clients/android/app/src/main/res/xml/file_paths.xml` (missing/mismatched on default)
- `clients/android/app/src/test/java/org/gunnchos/edgeio/ConsentManagerTest.kt` (missing/mismatched on default)
- `clients/android/build.gradle.kts` (missing/mismatched on default)
- `clients/android/gradle.properties` (missing/mismatched on default)
- `clients/android/gradle/wrapper/gradle-wrapper.properties` (missing/mismatched on default)
- `clients/android/settings.gradle.kts` (missing/mismatched on default)
- `src/edge_io_node/cli.py` (missing/mismatched on default)
- `src/edge_io_node/collectors/base.py` (missing/mismatched on default)
- `tests/contracts/test_gate2_edge_contracts.py` (missing/mismatched on default)

### 7gc-digital-twin

- **Current default tip:** `8fa2f729584e58f107c5a690b3f389c1ef717b84`
- **Original Gate 3 PR:** #25
- **Approved Gate 3 commit:** `ffa214f1b006497184cb9cdd514142720ef101a5` (exists locally: True)
- **Gate 3 merge commit (into Gate 2 branch):** `cf324c5e9913365c401fd27735614c4f9466b50d`
- **Gate 2 commit present on default:** `323a88ca21b7ff7bee2a8549cddb09da96b0ed1b` → True
- **Gate 3 commit reachable from default:** False
- **Gate 3 patch already represented by different SHA on default:** False
- **Files changed in Gate 3 commit:** 1
- **Files mismatched vs default tip:** 1
- **Promotion needed:** True

Changed files:
- `docs/GATE3_NOTE.md` (missing/mismatched on default)

### spectrumx-ai-ran-gary

- **Current default tip:** `3030fcad25b6a5ba57db12f7ff3d10f4a783008c`
- **Original Gate 3 PR:** #95
- **Approved Gate 3 commit:** `0cba08dd7be6b7ad1d0c93ddf231f5f61bfc059b` (exists locally: True)
- **Gate 3 merge commit (into Gate 2 branch):** `b86a32dc224e0c617b57d93b30f720efd83fdd96`
- **Gate 2 commit present on default:** `0686d47d77cbc9fb9cbce262cdae732996f106b5` → True
- **Gate 3 commit reachable from default:** False
- **Gate 3 patch already represented by different SHA on default:** False
- **Files changed in Gate 3 commit:** 1
- **Files mismatched vs default tip:** 1
- **Promotion needed:** True

Changed files:
- `docs/GATE3_NOTE.md` (missing/mismatched on default)

### ntn-resilience-sim

- **Current default tip:** `4170aca8af0c33d0076832d2f07e0767bbff2488`
- **Original Gate 3 PR:** #22
- **Approved Gate 3 commit:** `f3a8ff415401322a29aa9faca5fcdb910fd497ae` (exists locally: True)
- **Gate 3 merge commit (into Gate 2 branch):** `60e0038a509d17ba866be5856f552fad70f213d1`
- **Gate 2 commit present on default:** `ea7800e22409f2d7b6a41e22560f81d59043475e` → True
- **Gate 3 commit reachable from default:** False
- **Gate 3 patch already represented by different SHA on default:** False
- **Files changed in Gate 3 commit:** 3
- **Files mismatched vs default tip:** 3
- **Promotion needed:** True

Changed files:
- `config/assumption_registry.yaml` (missing/mismatched on default)
- `docs/ASSUMPTION_REGISTRY.md` (missing/mismatched on default)
- `src/ntn_resilience/gate2/decide.py` (missing/mismatched on default)

### gunnchos-7gc-ai-ran-field-kit

- **Current default tip:** `e06a9a89c21624401296656532313ee9cfbd661f`
- **Original Gate 3 PR:** #3
- **Approved Gate 3 commit:** `5af0e4ffeef9bd45a6701e35f6bf895aa2bf94fe` (exists locally: True)
- **Gate 3 merge commit (into Gate 2 branch):** `d3d344e18e45e3ccd9eb205c35b2d0c32c70214c`
- **Gate 2 commit present on default:** `82099df12323c9b689e55f8a1169781416e406b5` → True
- **Gate 3 commit reachable from default:** False
- **Gate 3 patch already represented by different SHA on default:** False
- **Files changed in Gate 3 commit:** 89
- **Files mismatched vs default tip:** 89
- **Promotion needed:** True

Changed files:
- `.github/workflows/gate3-evidence-readiness.yml` (missing/mismatched on default)
- `.gitignore` (missing/mismatched on default)
- `GATE3_DEVICE_COLLECTION_HANDOFF.md` (missing/mismatched on default)
- `GATE3_GATE2_BASELINE_VERIFICATION.md` (missing/mismatched on default)
- `Makefile` (missing/mismatched on default)
- `contracts/controlled_dataset_manifest.v1.schema.json` (missing/mismatched on default)
- `contracts/external_dataset_record.v1.schema.json` (missing/mismatched on default)
- `contracts/gate3_evidence_report.v1.schema.json` (missing/mismatched on default)
- `contracts/measurement_session_context.v1.schema.json` (missing/mismatched on default)
- `datasets/README.md` (missing/mismatched on default)
- `datasets/controlled/published/.gitkeep` (missing/mismatched on default)
- `datasets/controlled/raw/.gitkeep` (missing/mismatched on default)
- `datasets/controlled/sanitized/.gitkeep` (missing/mismatched on default)
- `datasets/controlled/staged/.gitkeep` (missing/mismatched on default)
- `datasets/external/registry/external_dataset_registry.json` (missing/mismatched on default)
- `datasets/external/source/.gitkeep` (missing/mismatched on default)
- `datasets/external/transformed/.gitkeep` (missing/mismatched on default)
- `datasets/simulated/source/.gitkeep` (missing/mismatched on default)
- `datasets/simulated/transformed/.gitkeep` (missing/mismatched on default)
- `docs/GATE3_ANDROID_SETUP.md` (missing/mismatched on default)
- `docs/GATE3_COLLECTION_QUICKSTART.md` (missing/mismatched on default)
- `docs/GATE3_DATA_PROVENANCE.md` (missing/mismatched on default)
- `docs/GATE3_EVIDENCE_LIMITATIONS.md` (missing/mismatched on default)
- `docs/GATE3_EXTERNAL_DATA.md` (missing/mismatched on default)
- `docs/GATE3_GENUINE_EVIDENCE.md` (missing/mismatched on default)
- `docs/GATE3_PRIVACY_REVIEW.md` (missing/mismatched on default)
- `protocols/CONSENT_AND_WITHDRAWAL_GUIDE.md` (missing/mismatched on default)
- `protocols/CONTROLLED_PILOT_PROTOCOL.md` (missing/mismatched on default)
- `protocols/DATA_HANDLING_PLAN.md` (missing/mismatched on default)
- `protocols/LOCATION_AND_ENVIRONMENT_GUIDE.md` (missing/mismatched on default)
- `protocols/NETWORK_CONDITION_GUIDE.md` (missing/mismatched on default)
- `protocols/PILOT_DEVIATION_LOG_TEMPLATE.md` (missing/mismatched on default)
- `protocols/controlled_pilot_matrix.csv` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160425Z/GATE3_EVIDENCE_REPORT.md` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160425Z/coverage_audit.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160425Z/external_evidence/source_record.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160425Z/external_evidence/transformation_report.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160425Z/external_evidence/transformed_data.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160425Z/gate3-controlled-20260722/controlled_dataset/DATASET_CARD.md` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160425Z/gate3-controlled-20260722/controlled_dataset/checksums.sha256` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160425Z/gate3-controlled-20260722/controlled_dataset/collection_matrix_completed.csv` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160425Z/gate3-controlled-20260722/controlled_dataset/consent_summary.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160425Z/gate3-controlled-20260722/controlled_dataset/dataset_manifest.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160425Z/gate3-controlled-20260722/controlled_dataset/privacy_review.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160425Z/gate3-controlled-20260722/controlled_dataset/protocol_deviations.csv` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160425Z/gate3_evidence_report.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160425Z/gate3_status.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160528Z/GATE3_EVIDENCE_REPORT.md` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160528Z/coverage_audit.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160528Z/external_evidence/source_record.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160528Z/external_evidence/transformation_report.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160528Z/external_evidence/transformed_data.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160528Z/gate3-controlled-20260722/controlled_dataset/DATASET_CARD.md` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160528Z/gate3-controlled-20260722/controlled_dataset/checksums.sha256` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160528Z/gate3-controlled-20260722/controlled_dataset/collection_matrix_completed.csv` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160528Z/gate3-controlled-20260722/controlled_dataset/consent_summary.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160528Z/gate3-controlled-20260722/controlled_dataset/dataset_manifest.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160528Z/gate3-controlled-20260722/controlled_dataset/privacy_review.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160528Z/gate3-controlled-20260722/controlled_dataset/protocol_deviations.csv` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160528Z/gate3_evidence_report.json` (missing/mismatched on default)
- `results/gate3/gate3-run-20260722T160528Z/gate3_status.json` (missing/mismatched on default)
- `results/integrated/2026-07-22-synthetic-gary-learn-001/02_twin_state.json` (missing/mismatched on default)
- `results/integrated/2026-07-22-synthetic-gary-learn-001/03_airan_network_only_decision.json` (missing/mismatched on default)
- `results/integrated/2026-07-22-synthetic-gary-learn-001/03_airan_optimization_decision.json` (missing/mismatched on default)
- `results/integrated/2026-07-22-synthetic-gary-learn-001/03_airan_service_priority_decision.json` (missing/mismatched on default)
- `results/integrated/2026-07-22-synthetic-gary-learn-001/03_airan_static_decision.json` (missing/mismatched on default)
- `results/integrated/2026-07-22-synthetic-gary-learn-001/03_airan_twin_informed_decision.json` (missing/mismatched on default)
- `results/integrated/2026-07-22-synthetic-gary-learn-001/04_resilience_decision.json` (missing/mismatched on default)
- `results/integrated/2026-07-22-synthetic-gary-learn-001/ablation_results.csv` (missing/mismatched on default)
- `results/integrated/2026-07-22-synthetic-gary-learn-001/benchmark_results.csv` (missing/mismatched on default)
- `results/integrated/2026-07-22-synthetic-gary-learn-001/checksums.sha256` (missing/mismatched on default)
- `results/integrated/2026-07-22-synthetic-gary-learn-001/command_log.txt` (missing/mismatched on default)
- `results/integrated/2026-07-22-synthetic-gary-learn-001/manifest.json` (missing/mismatched on default)
- `scripts/assemble_controlled_dataset.py` (missing/mismatched on default)
- `scripts/audit_collection_coverage.py` (missing/mismatched on default)
- `scripts/build_collection_matrix.py` (missing/mismatched on default)
- `scripts/evaluate_gate3_status.py` (missing/mismatched on default)
- `scripts/gate3_common.py` (missing/mismatched on default)
- `scripts/generate_gate3_report.py` (missing/mismatched on default)
- `scripts/register_external_dataset.py` (missing/mismatched on default)
- `scripts/run_gate3_evidence_pipeline.py` (missing/mismatched on default)
- `scripts/sanitize_session.py` (missing/mismatched on default)
- `scripts/transform_external_dataset.py` (missing/mismatched on default)
- `scripts/validate_contract.py` (missing/mismatched on default)
- `scripts/validate_session.py` (missing/mismatched on default)
- `scripts/verify_external_dataset.py` (missing/mismatched on default)
- `tests/evidence_status/test_gate3_status.py` (missing/mismatched on default)
- `tests/external_data/test_registry.py` (missing/mismatched on default)
- `tests/privacy/test_privacy_scan.py` (missing/mismatched on default)

### readygary-6g-beam-selection

- No Gate 3 implementation PR.
- No promotion required.

## Promotion plan

1. Branch `cursor/gate3-main-promotion-3ec5` from current `origin/<default>`.
2. Cherry-pick the approved Gate 3 commit (Gate 2 already on default → expect clean Gate 3-only delta).
3. If cherry-pick duplicates Gate 2, abort and apply only `git diff <g3>^..<g3>`.
4. Open promotion PRs targeting `main`/`master`.
5. Merge order after tests: edge-io → 7gc → spectrumx → ntn → field-kit.
