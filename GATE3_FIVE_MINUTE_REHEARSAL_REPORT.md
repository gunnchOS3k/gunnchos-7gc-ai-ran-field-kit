# GATE3_FIVE_MINUTE_REHEARSAL_REPORT

## Verdict

Five-minute rehearsal: **PASS**

Pilot: **0 / 54** (rehearsal excluded)

## Physical evidence (raw preserved, not committed)

| Field | Value |
|---|---|
| Export path (operator) | `~/Downloads/pixel-rehearsal-1784848985767.json` |
| Preserved raw | `results/rehearsal/pixel6a/_ignored_raw/pixel-rehearsal-1784848985767.json` |
| SHA-256 | `acb21f3bf24113cfb1c422ac06ebeb6c632c6b4e8df344b05cb928234f4fd958` |
| Mode label | PHYSICAL DEVICE COLLECTION |
| session_mode | PILOT_REHEARSAL |
| rehearsal_only | true |
| calibration_only | false |
| planned_duration_seconds | 300 |
| actual_duration_seconds | 300.402 |
| Samples | 60 |
| run_id | `pixel-rehearsal-1784848985767` |
| assignment_id | `asn_33c87f5e180c45ad` |
| assignment_hash | `30adbabcd1a059d0d4362c31da2030259d8943fcefa4c27dbd80ba44b35f48b2` |
| protocol_version | gate3-pilot-v1 |
| collection_day_id | rehearsal_day |
| named_test_zone | zone_rehearsal |
| declared_network_condition | wifi_normal |
| detected_network_transport | wifi |
| workload | learn |
| protocol_deviation | rehearsal_not_pilot |
| evidence_level | controlled_device_measurement |
| consent | active; captured_at precedes collection start |
| producer | edge-io-measurement-node @ `dd1a7ec…` / 0.4.1-gate3-pilot / build_dirty=false |

## Validation

| Check | Result |
|---|---|
| Schema (`validate_session`) | PASS |
| Privacy scan | PASS |
| Consent ordering | PASS |
| Assignment ID/hash | PASS (matches v2 assignment) |
| Producer identity | PASS |
| Duration ≈ 300s | PASS |
| Sanitization | PASS (local ignored copy only) |
| pilotctl import | **REJECTED** — rehearsal_only |
| Pilot coverage after attempt | **0 / 54** |

## Integrated pipeline

Edge-IO → 7GC → SpectrumX → NTN: **PASS** (`GATE2_SYSTEM_PASS` on rehearsal run)

Policies generated:

- static_uniform
- network_only
- service_priority
- optimization_based
- twin_informed

Resilience decision: terrestrial (`service_aware_multi_access`)

Note: pipeline ran without `--strict` because edge-io HEAD is the pilot-hardening
commit `dd1a7ec` (producer of this APK), ahead of repo-lock main `764192f`. Warning recorded.

## Non-claims

One rehearsal does not support scientific performance claims, Day 1 start,
Gate 3 PASS, or Gate 4 PASS.
