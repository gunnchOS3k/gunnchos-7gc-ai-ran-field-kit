# ICD — Edge I/O Rings

**ADR:** ADR-FP-008  
**Updated:** 2026-08-08T00:50:00Z

| Interface | Direction | Protocol | Notes | Evidence |
|---|---|---|---|---|
| BLE | bidirectional | BLE 5.x (nRF52840) | identity, sample stream, DFU | MODELED |
| I2C/SPI IMU | sensor→MCU | BMI270 | motion modality | MODELED |
| I2C CAP | sensor→MCU | IQS7222A class | contact modality — FOOTPRINT_REQUIRED | MODELED |
| SPI UWB | sensor↔MCU | DW3000 / DWM3001C | ranging assist; DNP → UWB_ON_COMPANION | MODELED |
| Mag I2C | sensor→MCU | BMM350 optional | heading assist | MODELED |
| SE I2C | MCU↔SE | SE050 | attestation | MODELED |
| Charge pogo | cradle→ring | 5 V | CHARGE_5V + GND keyed | MODELED |
| Host fusion | ring↔dock/host | BLE + optional UWB | heavy fusion off-ring | MODELED |

Physical connector mating and RF chamber results: `PHYSICAL_PENDING`.  
KiCad ERC/DRC CLI: `EDMUND_ACTION_REQUIRED`.
