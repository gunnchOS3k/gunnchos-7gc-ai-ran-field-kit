# Controlled Pilot Protocol

Minimum design: 3 zones × 2 network conditions × 3 days × 3 workloads = **54 sessions**.
Planned duration: **300 seconds** per session.

## Profiles
learn, create, sense

## Network conditions (lawful only)
- wifi_normal
- wifi_degraded (local traffic shaping / distance / competing local traffic on a personally controlled network)

Do **not** jam, spoof base stations, manipulate SIMs, or transmit unauthorized RF.

## Days
day_01, day_02, day_03 — distinct calendar days.

## Zones (non-identifying)
zone_a, zone_b, zone_c with coarse location categories only.

## Counting rule
Only `evidence_level=controlled_device_measurement` sessions from physical collectors count.
Calibration runs do not count toward the 54.
