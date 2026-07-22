# POST_MERGE_GATE3_GATE4_FINAL_REPORT

Generated: 2026-07-22T17:10:05.764565+00:00

## A. Gate 3 promotion status

| Repository | Original PR | Already on main? | Promotion branch | Promotion PR | Merge | Final main SHA |
|---|---|---|---|---|---|---|
| edge-io-measurement-node | #20 | no | cursor/gate3-main-promotion-3ec5 | #21 | merged | `2b4434952e6a533dff451349a10eb587045dd9f7` |
| 7gc-digital-twin | #25 | no | cursor/gate3-main-promotion-3ec5 | #26 | merged | `b036905df4f867aabdcc939ac646464874a3ee1f` |
| spectrumx-ai-ran-gary | #95 | no | cursor/gate3-main-promotion-3ec5 | #96 | merged | `f7af6c7f7541360e07402f6927794116a1684d32` |
| ntn-resilience-sim | #22 | no | cursor/gate3-main-promotion-3ec5 | #23 | merged | `9055b806fa001b6b8d0130353d87668f038dce6e` |
| gunnchos-7gc-ai-ran-field-kit | #3 | no | cursor/gate3-main-promotion-3ec5 | #4 | merged | `6a239e942aef31088589190eaa0e290b095f5578` |
| readygary-6g-beam-selection | n/a | n/a | n/a | n/a | n/a | `525405cb19d7987ad218272f5897d4917c10dd75` |

Tests: local component suites passed; GitHub CI PYTHONPATH failures were pre-existing on main and not introduced by Gate 3 deltas.

## B. Android status

| Field | Value |
|---|---|
| APK build | SUCCESS |
| APK path | `clients/android/app/build/outputs/apk/debug/app-debug.apk` |
| SHA-256 | `c0476831adf27d38d4be80dee0afe7ad084dcbce85fbb29a2c64110e163b549d` |
| Package | `org.gunnchos.edgeio.debug` |
| Pixel detection | empty device list |
| Authorization | **NO_DEVICE** |
| Installation | not performed |
| Launch / crash | n/a |

## C. Calibration status

| Field | Value |
|---|---|
| Real session | **yes** (laptop physical collector) |
| Device | laptop (Pixel unavailable) |
| Duration | 60 s |
| Evidence level | controlled_device_measurement |
| Consent | PASS (`--consent`, not adb-simulated) |
| Privacy | PASS |
| Schema | PASS |
| Sanitization | PASS |
| Integrated pipeline | PASS |
| Committed raw/sanitized | **no** |

## D. External evidence

| Field | Value |
|---|---|
| Selected path | NTN source-validated assumptions (3GPP TR 38.821) + M-Lab registry stub |
| Status | **EXTERNAL_EVIDENCE_PASS** via NTN source-validated path |
| M-Lab | still `blocked_pending_access` (not required once NTN qualifies) |

See `results/external_evidence/EXTERNAL_EVIDENCE_REPORT.md`.

## E. Pilot readiness

| Field | Value |
|---|---|
| Matrix cells | 54 |
| Eligible completed | 0 |
| Calibration sessions | 1 (excluded from matrix) |
| Missing cells | 54 |
| Next cell | via `python3 scripts/pilotctl.py next` |
| Operator guide | `GATE3_PILOT_OPERATOR_GUIDE.md` |

## F. Gate 4 readiness

| Field | Value |
|---|---|
| Baselines | static_uniform, network_only, service_priority, optimization_based, twin_informed (+ resilience set) |
| Held-out splits | leave-one-day/zone/network/workload + stress |
| Ablations | implemented |
| Uncertainty | bootstrap / repeated-seed; calibration labeled insufficient_sample_size_for_inference |
| Sensitivity | implemented |
| Negative results | NEGATIVE_RESULTS_REGISTER.md |
| One-command | `make gate4-evaluation-ready` → GATE4_EVALUATION_READY |
| CI | `.github/workflows/gate4-evaluation-readiness.yml` |

## G. Exact status

- **Gate 3:** `GATE3_PARTIAL_EVIDENCE`
- **Gate 4:** `GATE4_EVALUATION_READY`

Not claimed: `GATE_3_PASS`, `GATE_4_PASS`.
