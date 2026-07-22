# PIXEL_NO_REPO_LOCAL_CONTINUATION_FINAL_REPORT

Generated: 2026-07-22T22:01:36Z

## Discovery

- Search roots: Downloads/Documents/Desktop/Developer/Projects/repos
- Canonical copies: `.../gunnchos-7gc-research-product-spine/repos/{edge-io,7gc,spectrumx,ntn,field-kit,readygary}`
- Manifest: `/tmp/gunnchos_gate34_repo_manifest.json`
- Duplicates under Downloads left untouched (including dirty spectrumx copy)

## Android

| Field | Value |
|---|---|
| adb | DEVICE_AUTHORIZED |
| Pixel | Pixel 6a, API 37 |
| Package | org.gunnchos.edgeio.debug |
| version | 0.3.2-gate3-android / versionCode 5 |
| APK SHA-256 | `62f0b68320eaf08b409dc2e5685ac27813668a2443f3883ec0c69ba184fc404a` |
| Install | Success |
| Launch | MainActivity, no crash |
| FileProvider | fixed to `org.gunnchos.edgeio.debug.provider` |

## Calibration

| Field | Value |
|---|---|
| Manual consent | yes |
| Real Pixel calibration | yes |
| Run ID | pixel-cal-1784756973874 |
| Duration | ~60.66s |
| Raw SHA-256 | `6f8d62b9e2ec1cff5f3087eb2bd95039194c4db167ee5b1d153c3b83e8e2e904` |
| Schema | PASS |
| Consent | PASS (active, predates start) |
| Privacy | PASS |
| Sanitization | PASS |
| Integration | PASS (AUTOMATED_PIPELINE_PASS) |
| Measurement JSON committed | **no** |

Prior failed export `pixel-cal-1784755600830` preserved as recovery evidence only.

## External

- Status: **EXTERNAL_EVIDENCE_PASS**
- 3GPP TR 38.821 / Clause 5 path validated
- M-Lab remains blocked

## Pilot

- Total cells: 54
- Eligible: 0
- Missing: 54
- Calibration exclusion: yes
- Next cell: day_01_zone_a_wifi_normal_learn
- Day 1: **READY** (not started)

## Gate 4

- Command: `make gate4-evaluation-ready` → **GATE4_EVALUATION_READY**
- Baselines / splits / ablations / uncertainty / sensitivity: exercised in dry-run infrastructure validation

## Status (exact)

- Gate 3: **GATE3_PARTIAL_EVIDENCE**
- Gate 4: **GATE4_EVALUATION_READY**
- Pixel calibration: **PASS**
- Pilot: **0 / 54**
- Day 1: **READY**

## PRs

- Edge-IO #22 — FileProvider fix, export resilience, tests, build notes (do not merge)
- Field-kit #5 — privacy false-positive fix, calibration/integration reports, pilot/Day1 docs (do not merge)
- NTN #24 — unchanged (no code change required)
- 7GC null-metrics branch — local fix for physical unavailable fields

Do not merge. Edmund remains final merge approver.
