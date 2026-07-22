# GATE3_CALIBRATION_HANDOFF

Generated: 2026-07-22T17:10:05.764565+00:00

## Device

- Pixel 6a: **NO_DEVICE** (`adb devices -l` empty)
- Fallback: **60s laptop physical collector** calibration

## Session

- run_id: `cal-20260722T170604Z`
- evidence_level: `controlled_device_measurement`
- protocol_deviation: `calibration_not_pilot`
- calibration_only: true (not pilot)

## Artifacts (local / ignored)

- Raw: `datasets/controlled/raw/cal-20260722T170604Z.json` and `/tmp/edgeio_calibration_raw/`
- Sanitized: `datasets/controlled/sanitized/cal-20260722T170604Z.sanitized.json`
- Reports: `results/calibration/`
- Integrated: `results/integrated/calibration-cal-20260722T170604Z/`

**Raw and sanitized measurement payloads are not committed** pending Edmund publication approval.

## Android

See `edge-io-measurement-node/docs/android/EDGE_IO_ANDROID_BUILD_REPORT.md`.
Unlock the Pixel and accept USB debugging authorization to install and run on-device calibration next.
