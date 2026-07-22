# Gate 3 Device Collection Handoff

## APK

- path: `/agent/repos/edge-io-measurement-node/clients/android/app/build/outputs/apk/debug/app-debug.apk`
- sha256: `c0476831adf27d38d4be80dee0afe7ad084dcbce85fbb29a2c64110e163b549d`
- build: SUCCESS (local user-space Android SDK 34 + Gradle 8.2)

## Installation

```bash
export PATH="$HOME/Android/Sdk/platform-tools:$PATH"
adb devices
adb install -r /agent/repos/edge-io-measurement-node/clients/android/app/build/outputs/apk/debug/app-debug.apk
```

No Pixel/device was attached during automation (`adb devices` was empty). Installation was **not** attempted.

## Permissions

INTERNET, ACCESS_NETWORK_STATE only. No location permission.

## Calibration

Run one short session to verify consent/export. Calibration does **not** count toward the 54-cell matrix.

## 54-session matrix

See `protocols/controlled_pilot_matrix.csv` (3 zones × 2 networks × 3 days × 3 workloads).

## Daily checklist

1. Confirm `collection_day_id`
2. Collect zone_a/b/c × wifi_normal/wifi_degraded × learn/create/sense
3. Export sessions to host
4. `python3 scripts/validate_session.py --input <file>`
5. `python3 scripts/sanitize_session.py --input <raw> --output datasets/controlled/sanitized/<name>.json`
6. `python3 scripts/audit_collection_coverage.py --matrix protocols/controlled_pilot_matrix.csv --sessions datasets/controlled/sanitized`

## Laptop collector

```bash
cd edge-io-measurement-node
PYTHONPATH=src python3 -m edge_io_node collect \
  --collector physical --device-category laptop --profile learn --duration 300 \
  --site gary --zone zone_a --location-category library_or_community_indoor \
  --network-condition wifi_normal --collection-day-id day_01 \
  --run-id 2026-day01-zonea-wifi-learn \
  --output ../gunnchos-7gc-ai-ran-field-kit/datasets/controlled/raw/session.json \
  --consent
```

## Session counting criteria

- `evidence_level` must be `controlled_device_measurement`
- collector must not be `deterministic_emulator`
- consent active and predating collection
- privacy scan pass
- maps to a unique matrix cell
- not withdrawn/deleted; not a duplicate hash

## Gate 3 completion criteria

Requires genuine physical coverage of the 54-cell matrix plus eligible external/source-validated evidence. See `docs/GATE3_GENUINE_EVIDENCE.md`.
