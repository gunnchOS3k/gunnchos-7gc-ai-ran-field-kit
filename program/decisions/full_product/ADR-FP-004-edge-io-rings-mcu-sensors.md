# ADR-FP-004 — Edge I/O Rings MCU + sensor fusion freeze

- Status: **ACCEPTED (engineering baseline)**
- Date: 2026-08-08T00:07:41Z

## Decision
- MCU: **Nordic nRF52840** (already in ring digital path) — Zephyr + MCUboot production required (`RING_ZEPHYR_WEST_BUILD_PASS`)
- IMU: **Bosch BMI270** (exact MPN)
- Optional mag: **Bosch BMM350** footprint
- Capacitive contact: **Azoteq IQS5xx** class or discrete Cu electrodes + MCU CAP
- UWB (target-device assist, not sole): Qorvo/Apple-unrelated **DW3000** footprint on companion/dock/target — ring may omit UWB if size/power fail; fusion ADR requires multi-modal evidence
- BLE: onboard nRF52840 radio + chip antenna + keep-outs
- Secure element: **NXP SE050C1HQ1** footprint
- Battery: rechargeable Li-ion pouch or LiPo 3.7V 40–60 mAh with protection; charging case TBD mechanical

## Sensor fusion policy
No single modality claimed sufficient. Pipeline: Sense→identity→target→frame→contact/gesture→action→confidence→auth→dispatch→feedback→privacy diagnostics.
