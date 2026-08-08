# Architecture — Edge I/O Rings

**Status:** DIGITAL_DESIGN / NONPHYSICAL  
**Physical:** `REPRESENTATIVE_ENCLOSURE_PHYSICAL_PENDING`  
**Freeze:** PHYSICAL_EXECUTION_FREEZE ACTIVE  
**ADRs:** ADR-FP-004 (MCU freeze), **ADR-FP-008 (sensor fusion — MCU alone insufficient)**

## Role
wearable ring input + edge I/O measurement node companion with **multi-modal spatial-input** path

## Subsystems
- Mechanical enclosure (parameterized CAD)
- Electrical power + I/O (see `electrical/power_tree.yaml`)
- Primary MCU: nRF52840 (BLE / identity / DFU) — **not** sole spatial sensor
- Sensors: BMI270 + capacitive (IQS7222A footprint) + optional mag/UWB/sensor-hub
- OS integration profile
- Manufacturing package (candidate)
- Validation harnesses (sim + collectors for later MEASURED)

## Spatial-input architecture (ADR-FP-008)
1. Ring-local light fusion: IMU + capacitive (+ mag)
2. UWB assist via DW3000 footprint or `UWB_ON_COMPANION`
3. Host/dock heavy fusion for absolute frame
4. Confidence gate: ≥2 modalities before dispatch

## Trust boundary
Root of Trust → bootloader → OS kernel → signed update client → apps/games.

## Non-claims
This package does **not** claim physical build, FCC/CE, measured spatial accuracy, or `GATE_2_PASS`.
