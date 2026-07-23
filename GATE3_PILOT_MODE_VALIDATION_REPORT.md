# GATE3_PILOT_MODE_VALIDATION_REPORT

## Modes

| Mode | Duration | Run-ID prefix | Counts toward 54? |
|---|---|---|---|
| CALIBRATION | 60s | pixel-cal | No |
| PILOT_REHEARSAL | 300s | pixel-rehearsal | No |
| PILOT | 300s | pixel-pilot | Yes, after full validation |

## Assignment contract

- Schema: `contracts/pilot_assignment.v1.schema.json`
- Algorithm: `gunnchos-canonical-json-sha256-v1`
- Spec: `docs/PILOT_ASSIGNMENT_CANONICAL_HASHING.md`
- pilotctl: emit-assignment / emit-rehearsal / validate-assignment / verify-roundtrip / import-session

## Android

| Field | Value |
|---|---|
| Package | org.gunnchos.edgeio.debug |
| versionName | 0.4.1-gate3-pilot |
| versionCode | 7 |
| Producer commit | dd1a7ec18673263eb181ff51479a8249a6635989 |
| Build dirty (installed rehearsal APK) | false |
| Assignment import | PASS (v2) |
| Declared vs detected transport | Separated |
| Counting banner | REHEARSAL — DOES NOT COUNT |

## Hash interoperability incident

Resolved: Android `JSONObject.toString()` collapsed `300.0`→`300`. Fixed via shared integer-seconds canonicalization. See `PILOT_ASSIGNMENT_HASH_INTEROPERABILITY_REPORT.md`.

## Rehearsal exercise

Completed physical five-minute PILOT_REHEARSAL; validated; excluded from matrix.

## Pilot matrix

Eligible: **0 / 54**
