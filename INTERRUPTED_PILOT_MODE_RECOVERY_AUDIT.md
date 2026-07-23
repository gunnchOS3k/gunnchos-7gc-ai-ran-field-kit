# INTERRUPTED_PILOT_MODE_RECOVERY_AUDIT

Recovered without branch switches, resets, cleans, or discarding edits.
Patch backups written under `/tmp/*-gate3-pilot-*.patch`.

## Repository path manifest

Used: `/tmp/gunnchos_gate3_pilot_repo_manifest.json` (present).

Earlier `/tmp/gunnchos_gate34_repo_manifest.json`: missing (not required).

## Primary repositories

### gunnchos-7gc-ai-ran-field-kit

| Field | Value |
|---|---|
| Path | `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gunnchos-7gc-ai-ran-field-kit` |
| Branch | `cursor/gate3-pilot-assignment-controller` |
| HEAD | `ffb237fb29a77f68fe2185b6d72de33edc076748` |

**Modified**

- `contracts/measurement_session_context.v1.schema.json`
- `datasets/external/registry/external_dataset_registry.json` (timestamp-only drift; leave untouched)
- `scripts/pilotctl.py`
- `scripts/validate_contract.py`

**Untracked (selected)**

- `GATE3_PILOT_MODE_BASELINE_AUDIT.md`
- `contracts/pilot_assignment.v1.schema.json`
- `datasets/controlled/assignments/rehearsal_assignment_latest.json`
- `tests/pilotctl/test_pilot_assignment_contract.py`
- `results/gate4/gate4-run-20260723T222614Z/` (dry-run artifacts)
- `results/calibration/pixel6a/integrated_pipeline_console.log`

**Patch backups**

- `/tmp/field-kit-gate3-pilot-interrupted.patch`
- `/tmp/field-kit-gate3-pilot-index.patch`
- `/tmp/field-kit-gate3-pilot-untracked.txt`

### edge-io-measurement-node

| Field | Value |
|---|---|
| Path | `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/edge-io-measurement-node` |
| Branch | `cursor/gate3-pilot-mode-hardening` |
| HEAD | `764192fd889bd42246096402d3ea573d85b1f923` |

**Modified**

- `clients/android/app/build.gradle.kts` (0.4.0 / versionCode 6 + build identity)
- `MainActivity.kt`, `MeasurementSessionController.kt`, `Models.kt`, `PhysicalMetricsSampler.kt`, `SessionExporter.kt`
- `activity_main.xml`
- `ConsentManagerTest.kt`

**Untracked**

- `NetworkTransportDetector.kt`
- `PilotAssignment.kt`
- `SessionMode.kt`

**Patch backups**

- `/tmp/edge-io-gate3-pilot-interrupted.patch`
- `/tmp/edge-io-gate3-pilot-index.patch`
- `/tmp/edge-io-gate3-pilot-untracked.txt`

### Supporting repos (unchanged by this interrupted pilot branch)

| Repo | Branch | HEAD | Dirty |
|---|---|---|---|
| 7gc-digital-twin | main | `fcc9b11` | clean |
| spectrumx-ai-ran-gary | main | `f7af6c7` | clean |
| ntn-resilience-sim | main | `2403456` | clean |

## Device / install state at recovery

| Field | Value |
|---|---|
| adb | DEVICE_AUTHORIZED |
| Pixel | Pixel 6a |
| Installed package | `org.gunnchos.edgeio.debug` |
| versionName | `0.4.0-gate3-pilot` |
| versionCode | 6 |
| Local APK | `clients/android/app/build/outputs/apk/debug/app-debug.apk` (present) |
| Rehearsal assignment on device | `/sdcard/Download/gate3_rehearsal_assignment.json` |
| Rehearsal export | **not found** (no `pixel-rehearsal-*.json`) |

Prior calibration `pixel-cal-1784756973874.json` is **not** rehearsal evidence and must not be reused.

## Implemented vs incomplete

### Field-kit — implemented

- `pilot_assignment.v1` schema
- assignment emit / validate / hash in `pilotctl`
- `emit-rehearsal`, `emit-assignment`, `validate-assignment`, `import-session`, `next`, `status`
- calibration + rehearsal exclusion from pilot counting
- assignment contract tests (partial)

### Field-kit — incomplete at recovery

- broader negative-path tests (expiry, reuse, day/zone/network/workload mismatch, short duration, deleted, missing producer commit)
- post-rehearsal validation / integration / GO-NO-GO reports
- commits / draft PRs

### Edge-IO — implemented

- typed CALIBRATION / PILOT_REHEARSAL / PILOT
- 60s / 300s durations and run-ID prefixes
- document-picker assignment import + hash verification
- declared vs detected transport
- counting banner / build identity / export fields
- unit tests for modes, assignment, export, FileProvider

### Edge-IO — incomplete at recovery

- five-minute physical rehearsal not yet exported by operator
- commits / draft PR

## Hash interoperability incident (post-recovery)

Failed assignment import (no measurement session):

- assignment_id `asn_7cd312d6fa594505`
- stored hash valid under field-kit canonicalization
- Android hashed differently because `JSONObject.toString()` collapsed `300.0` → `300`

Fix landed on dirty branches without discarding prior work:

- shared algorithm `gunnchos-canonical-json-sha256-v1`
- integer `planned_duration_seconds`
- Android `AssignmentCanonicalJson` (no toString crypto path)
- regenerated `gate3_rehearsal_assignment_v2.json` (`asn_33c87f5e180c45ad`)
- Android app `0.4.1-gate3-pilot` / versionCode 7

See `PILOT_ASSIGNMENT_HASH_INTEROPERABILITY_REPORT.md`.
