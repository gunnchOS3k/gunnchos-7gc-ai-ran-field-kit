# GATE3_DAY1_READINESS_PACKET

Generated: 2026-07-22T18:30:03Z

**Do not start Day 1 automatically.** Edmund must approve the three broad test zones and two network conditions first.

## Current pilot counts

| Metric | Value |
|---|---|
| Eligible pilot sessions | **0** |
| Missing cells | **54** |
| Calibration sessions (excluded) | 1 laptop (+ Pixel pending) |

## Proposed first cell

```json
{
  "ok": true,
  "next": {
    "cell_id": "day_01_zone_a_wifi_normal_learn",
    "collection_day_id": "day_01",
    "zone_id": "zone_a",
    "location_category": "library_or_community_indoor",
    "network_condition": "wifi_normal",
    "workload_profile": "learn",
    "planned_duration_seconds": "300",
    "status": "pending",
    "session_file": "",
    "validation_status": "not_run",
    "privacy_status": "not_run",
    "notes": ""
  },
  "message": "collect this cell; do not prefill measurements"
}
```

| Field | Proposed |
|---|---|
| cell_id | day_01_zone_a_wifi_normal_learn |
| zone category | library_or_community_indoor (`zone_a`) |
| network condition | wifi_normal |
| workload | learn |
| duration | 300 seconds |

## App / APK

| Field | Value |
|---|---|
| Package | org.gunnchos.edgeio.debug |
| Version | 0.3.1-gate3-android (versionCode 4) |
| APK SHA-256 | `98b4c9dcb4e36df1177e35e7a9c845aa54542b20c81a667a37dbed665f9a0f4a` |

## Phone checklist (operator)

- [ ] Battery ≥ 50% and charging available
- [ ] Storage ≥ 1 GB free
- [ ] USB debugging authorized (or wireless debugging connected)
- [ ] Wi-Fi connected for wifi_normal cells
- [ ] Exact address not recorded — named zone only

## Export / validate / import

1. Export session from app share sheet to Downloads / approved folder.
2. Validate:
   ```
   python3 scripts/validate_session.py --input <file>
   python3 scripts/sanitize_session.py --input <file> --output datasets/controlled/sanitized/<name>.json
   ```
3. Import only if pilot-eligible (not calibration):
   ```
   python3 scripts/pilotctl.py import-session <sanitized>
   python3 scripts/pilotctl.py validate-day day_01
   python3 scripts/pilotctl.py report
   ```

## Success criteria for a counting session

- controlled_device_measurement
- consent active and before start
- privacy scan clean
- maps to an open matrix cell
- duration meets protocol (≥300 s for pilot cells)
- not calibration_only
- not duplicate hash

## Failure recovery

- Preserve failed export + logs
- Do not edit measured values/timestamps
- Fix app/pipeline; new session ID; mark prior attempt failed in day notes

## End-of-day audit

```
python3 scripts/pilotctl.py validate-day day_01
python3 scripts/pilotctl.py status
```
