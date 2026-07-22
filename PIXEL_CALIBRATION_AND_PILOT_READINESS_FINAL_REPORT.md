# PIXEL_CALIBRATION_AND_PILOT_READINESS_FINAL_REPORT

Generated: 2026-07-22T18:30:03Z

## Android

| Field | Value |
|---|---|
| Device classification | **NO_DEVICE** (cloud agent; Pixel on Mac USB-C not visible) |
| Device model | not readable here |
| Android version | not readable here |
| APK path | edge-io `clients/android/app/build/outputs/apk/debug/app-debug.apk` |
| APK hash | `98b4c9dcb4e36df1177e35e7a9c845aa54542b20c81a667a37dbed665f9a0f4a` |
| Install result | not performed |
| Launch result | not performed |
| Crash result | n/a |

## Calibration

| Field | Value |
|---|---|
| Real Pixel session | **no** (blocked by NO_DEVICE) |
| Laptop calibration | yes (prior 60s physical) |
| Duration (laptop) | 60 s |
| Consent / privacy / schema / sanitize / integrated | PASS (laptop) |
| Committed evidence JSON | **no** |

Android exporter was hardened for Pixel (real timestamps, measurement_batch, calibration_only, zone_calibration, explicit unavailable fields). Ready for install once device is authorized to this agent or installed from Mac.

## External

| Field | Value |
|---|---|
| Path | NTN / 3GPP TR 38.821 |
| Status | **EXTERNAL_EVIDENCE_PASS** |
| Section pointers | Clause 5 / scenario context recorded |
| M-Lab | blocked_pending_access |

## Pilot

| Field | Value |
|---|---|
| Matrix size | 54 |
| Eligible completed | **0** |
| Missing | 54 |
| Calibration exclusion | PASS |
| Next cell | day_01_zone_a_wifi_normal_learn |
| Day 1 readiness | packet prepared; not started |

## Pull requests

| Repo | PR | Notes |
|---|---|---|
| edge-io | #22 | Android calibration hardening + build report |
| field-kit | #5 | schema nullability, pilotctl acceptance, Day1 packet, external audit |

Merge recommendation: **do not merge** until Edmund reviews; Pixel install still blocked in this environment unless wireless adb is provided.

## Exact status

- Gate 3: **GATE3_PARTIAL_EVIDENCE**
- Gate 4: **GATE4_EVALUATION_READY**
