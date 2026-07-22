# CALIBRATION_REPORT

## Status

Real physical calibration session completed on **laptop** (Pixel unavailable: NO_DEVICE).

**calibration_only: true** — does **not** count toward the 54-session pilot.

## Session

| Field | Value |
|---|---|
| run_id | `cal-20260722T170604Z` |
| session_id | `sess_cal-20260722T170604Z` |
| device_category | `laptop` |
| zone | `zone_calibration` |
| network_condition | `wifi_normal` |
| workload | `learn` |
| duration | 60.0 s |
| evidence_level | `controlled_device_measurement` |
| protocol_deviation | `calibration_not_pilot` |
| samples | 12 |

## Checks

- Schema validation: PASS (after zone rename to `zone_calibration`)
- Privacy scan: PASS
- Consent order: PASS
- Sanitization: PASS
- Raw data: kept local/ignored — **not committed**
- Sanitized artifact: local under `datasets/controlled/sanitized/` and `results/calibration/` — **not committed pending Edmund publication approval**

## Limitations

- Not Pixel 6a; laptop physical HTTPS/device probe collector
- Consent timestamp equal to start at second resolution
- Single calibration session → Gate 3 becomes at most GATE3_PARTIAL_EVIDENCE after integration, never GATE_3_PASS
