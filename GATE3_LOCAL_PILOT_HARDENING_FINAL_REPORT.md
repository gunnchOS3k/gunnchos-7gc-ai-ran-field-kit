# GATE3_LOCAL_PILOT_HARDENING_FINAL_REPORT

## Baseline

| Item | Value |
|---|---|
| Field-kit merge SHA | `ffb237fb29a77f68fe2185b6d72de33edc076748` |
| Field-kit branch HEAD | `cursor/gate3-pilot-assignment-controller` |
| Edge-IO branch | `cursor/gate3-pilot-mode-hardening` @ `dd1a7ec…` |
| 7GC | main `fcc9b11…` |
| SpectrumX | main `f7af6c7…` |
| NTN | main `2403456…` |

Gate statuses:

- Gate 1: **GATE_1_PASS**
- Gate 2: **GATE2_SYSTEM_PASS**
- Release evidence: **RELEASE_EVIDENCE_PENDING**
- Gate 3: **GATE3_PARTIAL_EVIDENCE**
- Gate 4: **GATE4_EVALUATION_READY**

## Android

| Field | Value |
|---|---|
| versionName | 0.4.1-gate3-pilot |
| versionCode | 7 |
| producer commit | dd1a7ec18673263eb181ff51479a8249a6635989 |
| dirty/clean | clean for installed rehearsal APK |
| install | Success |
| launch | No crash |
| modes | CALIBRATION / PILOT_REHEARSAL / PILOT |

## Assignment

| Field | Value |
|---|---|
| Schema | gunnchos.pilot_assignment + hash algorithm v1 |
| Rehearsal assignment ID | asn_33c87f5e180c45ad |
| Assignment hash | 30adbabcd1a059d0d4362c31da2030259d8943fcefa4c27dbd80ba44b35f48b2 |
| Validation / import | PASS on Pixel |

## Rehearsal

| Field | Value |
|---|---|
| Manual consent | PASS |
| Duration | 300.402 s |
| Physical evidence | PASS |
| Schema / privacy / producer | PASS |
| Network detection | wifi (declared wifi_normal) |
| Assignment verification | PASS |
| Sanitization | PASS (local ignored) |
| Integration | PASS (five AI-RAN policies + NTN) |
| Exclusion from pilot | PASS → **0 / 54** |

## Pilot

| Field | Value |
|---|---|
| Eligible sessions | 0 |
| Completed cells | 0 |
| Missing cells | 54 |
| Next cell | first missing matrix cell via `pilotctl next` |
| Day 1 GO/NO-GO | **GO** (not started) |
| Remaining human decisions | zones, network conditions, day dates |

## Expected successful result

- Five-minute rehearsal: **PASS**
- Pilot: **0 / 54**
- Day 1: **GO**

Do **not** report GATE_3_PASS or GATE_4_PASS.
Do **not** start Day 1.
Do **not** merge without Edmund.

## Non-claims

No scientific performance claims from one rehearsal.
