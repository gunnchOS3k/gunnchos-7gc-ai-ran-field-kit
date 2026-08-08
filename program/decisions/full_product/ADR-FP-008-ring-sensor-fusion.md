# ADR-FP-008 — Ring spatial-input sensor fusion (MCU alone insufficient)

- Status: **ACCEPTED (engineering baseline)**
- Date: 2026-08-08T00:50:00Z
- Relates: ADR-FP-004, `FP-RING-SPATIAL-INPUT`, RING-INPUT-002
- Deciders: Cursor (engineering baseline); Edmund remains final product-scope authority

## Context
Full-product charter promises **spatial input** for Edge I/O Rings: multi-modal sense → identity → target → frame → contact/gesture → action → confidence → auth → dispatch → feedback, **without single-sensor reliance**.

Wave A ring digital path freezes **Nordic nRF52840** + **Bosch BMI270**. That stack can ship authenticated BLE gesture mule behavior, but it does **not** satisfy the spatial-input promise by itself:

| Gap | Why nRF52840 (+ BMI270 alone) fails the promise |
|---|---|
| Single modality | Accel/gyro-only path is single-sensor reliance (forbidden by RING-INPUT-002) |
| Contact / capacitive | Spatial contact/gesture needs finger/skin or pad electrodes; nRF SAADC CAP alone is not production-grade |
| Ranging / target assist | Absolute/relative spatial targeting needs UWB (or host-side vision); BLE RSSI is insufficient |
| Fusion compute vs radio | Concurrent BLE auth + high-rate IMU + capacitive + UWB SPI stresses M4F + power budget |
| Secure multi-modal evidence | Confidence/auth gating needs ≥2 independent modalities before dispatch |

## Decision
**Verdict: nRF52840 alone is insufficient for the spatial-input promise.**

Keep **nRF52840** as the **primary BLE / identity / DFU MCU**. Add **mandatory multi-modal footprints** and a **fusion policy** (ring-local light fusion + host/dock heavy fusion):

### Silicon / footprints (ring PCB)
| Role | Preferred MPN | Status | Notes |
|---|---|---|---|
| Primary MCU + BLE | Nordic **nRF52840-QIAA** (alt CKAA WLCSP) | FROZEN_BASELINE | Auth, pairing, DFU, sample stream |
| IMU | Bosch **BMI270** | FROZEN_BASELINE | Gesture / motion; INT wake |
| Mag (optional) | Bosch **BMM350** | FOOTPRINT / DNP OK | Heading assist |
| Capacitive | Azoteq **IQS7222A** class | FOOTPRINT_REQUIRED | Contact/proximity modality |
| UWB | Qorvo **DWM3001C** / **DW3000** footprint | FOOTPRINT; DNP on size-fail | Target assist; not sole modality |
| Sensor-hub coprocessor (optional) | Bosch **BHI360** (alt BHI260AP) | FOOTPRINT_OPTIONAL | Offloads fusion when standalone |
| Secure element | NXP **SE050C1HQ1** | FROZEN_BASELINE | Identity / attestation |

### Fusion architecture
1. **Ring-local:** BMI270 + capacitive (+ mag if populated) → light confidence on nRF52840 (or BHI360 if populated).
2. **Assist:** DW3000 ranging to dock/host/target — or `UWB_ON_COMPANION` if ring DNP.
3. **Host/dock heavy fusion:** paired device runs multi-modal fusion; ring never claims absolute 6-DoF from IMU alone.
4. **Policy:** ≥2 modalities required before action dispatch.

## Consequences
- Update `device_designs/edge_io_rings` BOM, block diagram, power-budget YAML.
- Mirror in hardware `gate1_digital_fabrication/edge_io_ring`.
- KiCad layout of new footprints `DESIGN_PENDING` until CLI present (`EDMUND_ACTION_REQUIRED`).

## Non-claims
No physical prototype, FCC/CE, or MEASURED spatial accuracy.
